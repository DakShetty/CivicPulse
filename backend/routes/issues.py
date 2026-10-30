import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from backend.models import SessionLocal
from backend.models.issue import (
    Issue,
    IssueCategory,
    IssueAttachment,
    StatusHistory,
    generate_public_reference,
)
from backend.models.cluster import IssueCluster, IssueClusterMember
from backend.models.assignment import Assignment
from backend.models.audit import AuditEvent
from backend.models.user import User
from backend.services.priority_scorer import calculate_priority_score
from backend.services.duplicate_detector import evaluate_duplicate_candidate
from backend.services.storage_service import storage_service
from backend.services.queue_service import queue_service
from backend.services.notification_service import notification_service
from backend.routes.auth import get_current_user_from_request, require_auth

issues_bp = Blueprint("issues", __name__, url_prefix="/api/v1/issues")


@issues_bp.route("/categories", methods=["GET"])
def get_categories():
    """Returns active issue categories."""
    db = SessionLocal()
    try:
        categories = db.query(IssueCategory).filter_by(is_active=True).all()
        return jsonify([c.to_dict() for c in categories])
    finally:
        db.close()


@issues_bp.route("", methods=["POST"])
def create_issue():
    """Submits a new public issue report."""
    data = request.form.to_dict() if request.form else (request.get_json() or {})

    category_id = data.get("category_id")
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    ward_or_district = data.get("ward_or_district", "").strip()
    approximate_address = data.get("approximate_address", "").strip()
    severity = int(data.get("severity", 3))
    safety_hazard = str(data.get("safety_hazard", "")).lower() in ("true", "1", "yes")
    impacts_critical = str(data.get("impacts_critical_infrastructure", "")).lower() in ("true", "1", "yes")

    if not title or not description or category_id is None or latitude is None or longitude is None:
        return jsonify({"error": "Missing required fields: title, description, category_id, latitude, longitude"}), 400

    try:
        lat = float(latitude)
        lon = float(longitude)
        cat_id = int(category_id)
    except ValueError:
        return jsonify({"error": "Invalid numerical format for coordinates or category"}), 400

    user = get_current_user_from_request()
    reporter_id = user.id if user else None

    db = SessionLocal()
    try:
        category = db.query(IssueCategory).filter_by(id=cat_id).first()
        if not category:
            return jsonify({"error": f"Category with id {cat_id} not found."}), 404

        # Calculate initial explainable priority score
        score, explanation = calculate_priority_score(
            severity=severity,
            safety_hazard=safety_hazard,
            impacts_critical_infrastructure=impacts_critical,
            cluster_member_count=1,
            hours_unresolved=0.0,
            category_weight=category.default_severity_weight,
        )

        issue = Issue(
            public_reference=generate_public_reference(),
            reporter_id=reporter_id,
            category_id=cat_id,
            title=title,
            description=description,
            approximate_address=approximate_address or "Approximate community location",
            ward_or_district=ward_or_district or "General Zone",
            latitude=lat,
            longitude=lon,
            severity=severity,
            safety_hazard=safety_hazard,
            impacts_critical_infrastructure=impacts_critical,
            priority_score=score,
            priority_explanation=explanation,
            status=Issue.STATUS_SUBMITTED,
        )
        db.add(issue)
        db.flush()

        # Record initial status history
        history = StatusHistory(
            issue_id=issue.id,
            old_status=None,
            new_status=Issue.STATUS_SUBMITTED,
            actor_id=reporter_id,
            note="Issue report submitted by resident.",
        )
        db.add(history)

        # Audit event
        audit = AuditEvent(
            actor_id=reporter_id,
            action="ISSUE_SUBMITTED",
            entity_type="issue",
            entity_id=str(issue.id),
            metadata_json=json.dumps({"ref": issue.public_reference, "category": category.name}),
            ip_address=request.remote_addr,
        )
        db.add(audit)

        # Handle optional photo file attachment if submitted via multipart/form-data
        attachment_created = None
        if "photo" in request.files:
            file = request.files["photo"]
            if file and file.filename:
                file_bytes = file.read()
                ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
                if ext in ("png", "jpg", "jpeg", "webp") and len(file_bytes) <= 8 * 1024 * 1024:
                    obj_key, size = storage_service.save_file(file_bytes, file.filename, prefix="attachments")
                    att = IssueAttachment(
                        issue_id=issue.id,
                        s3_object_key=obj_key,
                        original_filename=file.filename,
                        file_type=file.content_type or f"image/{ext}",
                        file_size_bytes=size,
                        storage_driver=storage_service.driver,
                    )
                    db.add(att)
                    attachment_created = obj_key

        db.commit()
        db.refresh(issue)

        # Check for potential duplicates against existing non-resolved issues
        candidate_issues = (
            db.query(Issue)
            .filter(
                Issue.id != issue.id,
                Issue.category_id == issue.category_id,
                Issue.status != Issue.STATUS_RESOLVED,
                Issue.status != Issue.STATUS_VERIFIED,
                Issue.status != Issue.STATUS_REJECTED,
            )
            .all()
        )

        detected_duplicate = None
        for candidate in candidate_issues:
            dup_eval = evaluate_duplicate_candidate(
                issue.to_dict(),
                candidate.to_dict(),
                max_distance_km=0.35,
                similarity_threshold=0.50,
            )
            if dup_eval["is_candidate"]:
                # Found a likely duplicate match! Link to existing cluster or create one
                target_cluster = None
                if candidate.cluster_id:
                    target_cluster = db.query(IssueCluster).filter_by(id=candidate.cluster_id).first()
                if not target_cluster:
                    target_cluster = IssueCluster(
                        title=f"{issue.category.name} Cluster near {issue.ward_or_district or 'Community'}",
                        representative_issue_id=candidate.id,
                        status="active",
                    )
                    db.add(target_cluster)
                    db.flush()
                    candidate.cluster_id = target_cluster.id
                    candidate.is_cluster_representative = True

                # Link this new issue to cluster
                issue.cluster_id = target_cluster.id
                cluster_member = IssueClusterMember(
                    cluster_id=target_cluster.id,
                    issue_id=issue.id,
                    similarity_score=dup_eval["composite_similarity"],
                    distance_km=dup_eval["distance_km"],
                    text_similarity=dup_eval["text_similarity"],
                    similarity_explanation=dup_eval["explanation"],
                    reviewed_status="pending_review",
                )
                db.add(cluster_member)

                # Recalculate priority score for both to reflect cluster repetition
                member_count = len(target_cluster.cluster_links) + 1
                new_score, new_expl = calculate_priority_score(
                    severity=issue.severity,
                    safety_hazard=issue.safety_hazard,
                    impacts_critical_infrastructure=issue.impacts_critical_infrastructure,
                    cluster_member_count=member_count,
                    hours_unresolved=0.0,
                    category_weight=category.default_severity_weight,
                )
                issue.priority_score = new_score
                issue.priority_explanation = new_expl

                db.commit()
                detected_duplicate = {
                    "matched_reference": candidate.public_reference,
                    "explanation": dup_eval["explanation"],
                    "cluster_id": target_cluster.id,
                }
                break

        # Queue async processing job (image processing / notification dispatch)
        queue_service.enqueue_job("new_issue_process", {
            "issue_id": issue.id,
            "has_attachment": bool(attachment_created),
            "is_safety_hazard": issue.safety_hazard,
        }, db=db)

        # Send alert if critical safety hazard
        if issue.safety_hazard or issue.priority_score >= 70:
            notification_service.send_notification(
                subject=f"URGENT: High Priority Civic Issue [{issue.public_reference}]",
                body=f"High priority issue reported: '{issue.title}' at {issue.ward_or_district}. Priority score: {issue.priority_score}.",
                issue_id=issue.id,
                channel="email",
                db=db,
            )

        return jsonify({
            "message": "Report submitted successfully",
            "public_reference": issue.public_reference,
            "issue": issue.to_dict(include_private=True if user else False),
            "duplicate_detected": detected_duplicate,
        }), 201
    finally:
        db.close()


@issues_bp.route("", methods=["GET"])
def list_issues():
    """Returns issues with filtering, pagination, and sorting."""
    db = SessionLocal()
    try:
        query = db.query(Issue)

        # Filters
        category_id = request.args.get("category_id")
        if category_id:
            query = query.filter(Issue.category_id == int(category_id))

        status = request.args.get("status")
        if status:
            query = query.filter(Issue.status == status)

        severity = request.args.get("severity")
        if severity:
            query = query.filter(Issue.severity == int(severity))

        ward = request.args.get("ward")
        if ward:
            query = query.filter(Issue.ward_or_district.ilike(f"%{ward}%"))

        safety_only = request.args.get("safety_only")
        if safety_only in ("true", "1"):
            query = query.filter(Issue.safety_hazard == True)

        search = request.args.get("search", "").strip()
        if search:
            query = query.filter(
                or_(
                    Issue.title.ilike(f"%{search}%"),
                    Issue.description.ilike(f"%{search}%"),
                    Issue.public_reference.ilike(f"%{search}%"),
                    Issue.approximate_address.ilike(f"%{search}%"),
                )
            )

        # Ordering: by priority_score desc or created_at desc
        sort = request.args.get("sort", "priority")
        if sort == "date":
            query = query.order_by(Issue.created_at.desc())
        else:
            query = query.order_by(Issue.priority_score.desc(), Issue.created_at.desc())

        # Pagination
        page = max(1, int(request.args.get("page", 1)))
        limit = min(100, max(1, int(request.args.get("limit", 25))))
        total = query.count()
        items = (
            query.options(
                joinedload(Issue.category),
                joinedload(Issue.reporter),
                joinedload(Issue.assignment).joinedload(Assignment.field_worker),
                joinedload(Issue.attachments),
            )
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        current_user = get_current_user_from_request()
        is_staff = current_user and current_user.role in ("admin", "field_worker")

        serialized_issues = [i.to_dict(include_private=is_staff) for i in items]

        return jsonify({
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "issues": serialized_issues,
        })
    finally:
        db.close()


@issues_bp.route("/<int:issue_id>", methods=["GET"])
def get_issue(issue_id: int):
    """Retrieves full details of a single issue."""
    db = SessionLocal()
    try:
        issue = (
            db.query(Issue)
            .options(
                joinedload(Issue.category),
                joinedload(Issue.reporter),
                joinedload(Issue.assignment).joinedload(Assignment.field_worker),
                joinedload(Issue.attachments),
                joinedload(Issue.status_history),
            )
            .filter_by(id=issue_id)
            .first()
        )
        if not issue:
            return jsonify({"error": "Issue not found"}), 404

        current_user = get_current_user_from_request()
        is_staff = current_user and current_user.role in ("admin", "field_worker")
        data = issue.to_dict(include_private=is_staff)
        data["attachments"] = [a.to_dict() for a in issue.attachments]
        data["history"] = [h.to_dict() for h in issue.status_history]
        return jsonify(data)
    finally:
        db.close()


@issues_bp.route("/track/<string:reference>", methods=["GET"])
def track_by_reference(reference: str):
    """Public lookup by report reference number."""
    db = SessionLocal()
    try:
        issue = db.query(Issue).filter_by(public_reference=reference.strip().upper()).first()
        if not issue:
            return jsonify({"error": f"No issue found with reference '{reference}'"}), 404

        # Return public-safe details
        data = issue.to_dict(include_private=False)
        data["history"] = [h.to_dict() for h in issue.status_history]
        return jsonify(data)
    finally:
        db.close()


@issues_bp.route("/<int:issue_id>/status", methods=["PATCH"])
@require_auth(roles=["admin", "field_worker"])
def update_issue_status(issue_id: int):
    """Updates issue workflow status."""
    data = request.get_json() or {}
    new_status = data.get("status")
    note = data.get("note", "").strip()
    rejection_reason = data.get("rejection_reason", "").strip()

    if new_status not in Issue.ALL_STATUSES:
        return jsonify({"error": f"Invalid status. Allowed values: {Issue.ALL_STATUSES}"}), 400

    if new_status == Issue.STATUS_REJECTED and not rejection_reason:
        return jsonify({"error": "A rejection reason is required when rejecting a report."}), 400

    db = SessionLocal()
    try:
        issue = db.query(Issue).filter_by(id=issue_id).first()
        if not issue:
            return jsonify({"error": "Issue not found"}), 404

        old_status = issue.status
        issue.status = new_status
        now = datetime.now(timezone.utc)

        # Update specific milestone timestamps
        if new_status in (Issue.STATUS_TRIAGED, Issue.STATUS_ASSIGNED) and not issue.acknowledged_at:
            issue.acknowledged_at = now
        if new_status == Issue.STATUS_RESOLVED and not issue.resolved_at:
            issue.resolved_at = now
        if new_status == Issue.STATUS_VERIFIED and not issue.verified_at:
            issue.verified_at = now
        if new_status == Issue.STATUS_REJECTED:
            issue.rejection_reason = rejection_reason

        # Record Status History
        history = StatusHistory(
            issue_id=issue.id,
            old_status=old_status,
            new_status=new_status,
            actor_id=g.current_user.id,
            note=note or (f"Status updated to {new_status} by {g.current_user.display_name}."),
        )
        db.add(history)

        # Audit Event
        audit = AuditEvent(
            actor_id=g.current_user.id,
            action="ISSUE_STATUS_UPDATE",
            entity_type="issue",
            entity_id=str(issue.id),
            metadata_json=json.dumps({"old_status": old_status, "new_status": new_status, "note": note}),
            ip_address=request.remote_addr,
        )
        db.add(audit)

        db.commit()
        db.refresh(issue)

        # Dispatch status update notification
        notification_service.send_notification(
            subject=f"Status Update: Issue {issue.public_reference} is now {new_status}",
            body=f"Issue '{issue.title}' has transitioned from {old_status} to {new_status}. Note: {note}",
            issue_id=issue.id,
            channel="in_app",
        )

        return jsonify({
            "message": f"Status updated to {new_status}",
            "issue": issue.to_dict(include_private=True),
        })
    finally:
        db.close()


@issues_bp.route("/<int:issue_id>/assign", methods=["POST"])
@require_auth(roles=["admin"])
def assign_worker(issue_id: int):
    """Assigns an issue to a field worker."""
    data = request.get_json() or {}
    field_worker_id = data.get("field_worker_id")
    notes = data.get("notes", "").strip()

    if not field_worker_id:
        return jsonify({"error": "field_worker_id is required"}), 400

    db = SessionLocal()
    try:
        issue = db.query(Issue).filter_by(id=issue_id).first()
        if not issue:
            return jsonify({"error": "Issue not found"}), 404

        worker = db.query(User).filter_by(id=int(field_worker_id), role="field_worker", is_active=True).first()
        if not worker:
            return jsonify({"error": "Invalid or inactive field worker"}), 400

        assignment = db.query(Assignment).filter_by(issue_id=issue.id).first()
        if not assignment:
            assignment = Assignment(
                issue_id=issue.id,
                field_worker_id=worker.id,
                assigned_by_id=g.current_user.id,
                notes=notes,
            )
            db.add(assignment)
        else:
            assignment.field_worker_id = worker.id
            assignment.assigned_by_id = g.current_user.id
            assignment.notes = notes

        # Update issue status to Assigned if currently Submitted or Triaged
        if issue.status in (Issue.STATUS_SUBMITTED, Issue.STATUS_TRIAGED):
            issue.status = Issue.STATUS_ASSIGNED
            now = datetime.now(timezone.utc)
            if not issue.acknowledged_at:
                issue.acknowledged_at = now
            issue.assigned_at = now

        db.add(StatusHistory(
            issue_id=issue.id,
            old_status=issue.status,
            new_status=Issue.STATUS_ASSIGNED,
            actor_id=g.current_user.id,
            note=f"Assigned to field worker {worker.display_name}. Notes: {notes}",
        ))

        db.add(AuditEvent(
            actor_id=g.current_user.id,
            action="ISSUE_ASSIGNED",
            entity_type="issue",
            entity_id=str(issue.id),
            metadata_json=json.dumps({"worker": worker.display_name, "notes": notes}),
            ip_address=request.remote_addr,
        ))

        db.commit()
        db.refresh(issue)

        # Notify field worker
        notification_service.send_notification(
            subject=f"New Task Assigned: {issue.public_reference}",
            body=f"You have been assigned to issue '{issue.title}' at {issue.ward_or_district}. Priority: {issue.priority_score:.0f}",
            issue_id=issue.id,
            recipient=worker.email,
            channel="email",
        )

        return jsonify({"message": f"Assigned to {worker.display_name}", "issue": issue.to_dict(include_private=True)})
    finally:
        db.close()
