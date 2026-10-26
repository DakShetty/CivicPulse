import io
import csv
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from backend.services.storage_service import storage_service


def generate_issues_csv(issues_data: list[dict], title: str = "CivicPulse Issues Summary") -> tuple[str, int]:
    """Generates a CSV file and stores it via storage_service.
    Returns: (s3_object_key, file_size_bytes)
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Reference",
        "Title",
        "Category",
        "Status",
        "Severity",
        "Priority Score",
        "Safety Hazard",
        "Critical Infra",
        "Ward/District",
        "Approx Address",
        "Latitude",
        "Longitude",
        "Created At",
        "Resolved At",
    ])

    for item in issues_data:
        writer.writerow([
            item.get("public_reference", ""),
            item.get("title", ""),
            item.get("category", {}).get("name", "") if isinstance(item.get("category"), dict) else "",
            item.get("status", ""),
            item.get("severity", ""),
            item.get("priority_score", ""),
            "Yes" if item.get("safety_hazard") else "No",
            "Yes" if item.get("impacts_critical_infrastructure") else "No",
            item.get("ward_or_district", ""),
            item.get("approximate_address", ""),
            item.get("latitude", ""),
            item.get("longitude", ""),
            item.get("created_at", ""),
            item.get("resolved_at", ""),
        ])

    csv_bytes = output.getvalue().encode("utf-8")
    object_key, size = storage_service.save_file(csv_bytes, "issues_summary.csv", prefix="reports")
    return object_key, size


def generate_summary_pdf(
    summary_metrics: dict,
    recent_issues: list[dict],
    title: str = "CivicPulse Operations Report",
) -> tuple[str, int]:
    """Generates an executive PDF report and stores it via storage_service.
    Returns: (s3_object_key, file_size_bytes)
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    story = []

    # Title & Metadata
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSub",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15,
    )

    story.append(Paragraph(title, title_style))
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    story.append(Paragraph(f"Generated at: {now_str} | System: CivicPulse Cloud Platform", subtitle_style))
    story.append(Spacer(1, 10))

    # KPI Summary Cards in a 2x2 table
    total = summary_metrics.get("total_issues", 0)
    open_count = summary_metrics.get("open_issues", 0)
    resolved = summary_metrics.get("resolved_issues", 0)
    clusters = summary_metrics.get("active_clusters", 0)
    avg_ack = summary_metrics.get("avg_acknowledge_hours", 0.0)
    avg_res = summary_metrics.get("avg_resolve_hours", 0.0)

    kpi_data = [
        ["Total Reports Submitted", str(total), "Open / In-Progress Issues", str(open_count)],
        ["Resolved Issues", str(resolved), "Duplicate Clusters Identified", str(clusters)],
        ["Avg Acknowledge Time", f"{avg_ack:.1f} hrs", "Avg Resolution Time", f"{avg_res:.1f} hrs"],
    ]

    kpi_table = Table(kpi_data, colWidths=[160, 90, 180, 90])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTNAME", (3, 0), (3, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 15))

    # Recent Issues Table
    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=8,
    )
    story.append(Paragraph("Recent Issues Snapshot", h2_style))

    table_data = [["Ref #", "Category", "Title", "Area", "Status", "Priority"]]
    for item in recent_issues[:15]:
        cat_name = item.get("category", {}).get("name", "") if isinstance(item.get("category"), dict) else ""
        table_data.append([
            item.get("public_reference", ""),
            cat_name[:18],
            item.get("title", "")[:28],
            (item.get("ward_or_district") or "N/A")[:15],
            item.get("status", ""),
            f"{item.get('priority_score', 0):.0f}",
        ])

    issues_table = Table(table_data, colWidths=[80, 95, 150, 85, 75, 45])
    issues_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0284c7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(issues_table)

    # Build document
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    object_key, size = storage_service.save_file(pdf_bytes, "operations_summary.pdf", prefix="reports")
    return object_key, size
