import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_report():
    doc = Document()

    # Define A4 Page Size & 1-inch Margins
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(6)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def add_p(text="", bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.alignment = align
        if text:
            run = p.add_run(text)
            run.bold = bold
            run.italic = italic
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(15)
        run.font.color.rgb = RGBColor(27, 54, 93) # Deep academic blue
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(40, 40, 40)
        return p

    def style_table(table, col_widths, headers, data):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        # Header Row
        hdr_row = table.rows[0]
        for idx, title in enumerate(headers):
            cell = hdr_row.cells[idx]
            cell.width = Inches(col_widths[idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            shading = parse_xml(r'<w:shd {} w:fill="1B365D"/>'.format(nsdecls('w')))
            cell._tc.get_or_add_tcPr().append(shading)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(title)
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10.5)
            run.font.color.rgb = RGBColor(255, 255, 255)

        # Data Rows
        for r_idx, row_data in enumerate(data):
            row = table.rows[r_idx + 1]
            fill_hex = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row_data):
                cell = row.cells[c_idx]
                cell.width = Inches(col_widths[c_idx])
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                shading = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), fill_hex))
                cell._tc.get_or_add_tcPr().append(shading)
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx != 0 else WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.15
                run = p.add_run(str(val))
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(30, 30, 30)

    # --------------------------------------------------------------------------
    # 1. COVER PAGE
    # --------------------------------------------------------------------------
    p_cov_top = add_p("A MINI-PROJECT REPORT ON", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=12)
    p_cov_top.runs[0].font.size = Pt(13)

    p_title = add_p("CIVICPULSE", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
    p_title.runs[0].font.size = Pt(22)
    p_title.runs[0].font.color.rgb = RGBColor(27, 54, 93)

    p_sub = add_p("Cloud-Based Public Infrastructure Issue Intelligence and Automated Triage Platform", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24)
    p_sub.runs[0].font.size = Pt(13)

    add_p("SUBMITTED IN PARTIAL FULFILLMENT OF THE REQUIREMENTS FOR THE DEGREE OF", bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=4)
    p_deg = add_p("BACHELOR OF TECHNOLOGY IN COMPUTER ENGINEERING", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24)
    p_deg.runs[0].font.size = Pt(12)

    add_p("SUBMITTED BY", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
    add_p("Daksh Shetty   (Roll No: 10761)\nShwet Shigwan  (Roll No: 10763)\nDaksh Gurav    (Roll No: 10734)", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24)

    add_p("UNDER THE GUIDANCE OF", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=4)
    add_p("[Project Guide Name]\nAssistant Professor, Department of Computer Engineering", bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=36)

    p_inst = add_p("DEPARTMENT OF COMPUTER ENGINEERING\nFR. CONCEICAO RODRIGUES COLLEGE OF ENGINEERING\nBANDRA (WEST), MUMBAI – 400050\nUNIVERSITY OF MUMBAI\nACADEMIC YEAR 2026–2027", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=0)
    p_inst.runs[0].font.size = Pt(11)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # TABLE OF CONTENTS
    # --------------------------------------------------------------------------
    add_heading_1("TABLE OF CONTENTS")
    toc_items = [
        ("1. Abstract", "iii"),
        ("2. Introduction", "1"),
        ("   2.1 Project Background", "1"),
        ("   2.2 Problem Statement", "1"),
        ("   2.3 Objectives and Scope", "2"),
        ("3. Existing and Proposed System", "3"),
        ("   3.1 Limitations of Existing Systems", "3"),
        ("   3.2 Features of Proposed CivicPulse System", "3"),
        ("   3.3 Comparative Evaluation", "4"),
        ("4. System Architecture and Cloud Design", "5"),
        ("   4.1 Multi-Tier Architecture Overview", "5"),
        ("   4.2 AWS Cloud Component Roles", "6"),
        ("   4.3 Network Isolation & Security", "6"),
        ("5. Technology Stack", "7"),
        ("6. Methodology and Implementation", "8"),
        ("   6.1 System Workflow", "8"),
        ("   6.2 Simplified Duplicate-Report Clustering", "8"),
        ("   6.3 Transparent Priority Scoring Formula", "9"),
        ("   6.4 Asynchronous Worker & Secure S3 Storage", "9"),
        ("7. Results and Testing", "10"),
        ("   7.1 User Interface Modules", "10"),
        ("   7.2 Verification and Test Results", "11"),
        ("8. Conclusion and Future Scope", "12"),
        ("   8.1 Conclusion", "12"),
        ("   8.2 Limitations", "12"),
        ("   8.3 Future Improvements", "12"),
        ("9. References", "13")
    ]
    for title, page in toc_items:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.space_before = Pt(1)
        p_toc.paragraph_format.space_after = Pt(1)
        p_toc.paragraph_format.line_spacing = 1.15
        run_t = p_toc.add_run(title)
        run_t.font.name = 'Times New Roman'
        run_t.font.size = Pt(11)
        # Add tab and page
        p_toc.add_run(" " + "." * (75 - len(title)) + " " + page)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 1. ABSTRACT
    # --------------------------------------------------------------------------
    add_heading_1("1. ABSTRACT")
    add_p(
        "Municipal defect management portals frequently suffer from complaint redundancy, lack of geographical clustering, and "
        "arbitrary manual prioritization. This leads to prolonged repair times, duplicated work crews, and inefficient civic budget expenditure. "
        "CivicPulse is a cloud-based public infrastructure intelligence platform engineered to streamline grievance reporting, duplicate triage, "
        "and resolution tracking for urban local bodies."
    )
    add_p(
        "The system introduces a deterministic duplicate clustering model that groups nearby complaints using geospatial proximity (under 350 meters) "
        "and text similarity without discarding original citizen records. Additionally, a transparent multi-factor priority scoring algorithm dynamically "
        "ranks issues (0–100) based on severity, immediate life-safety hazards, repetition density, and unresolved aging."
    )
    add_p(
        "Built on Amazon Web Services (AWS), the platform deploys a React frontend and Python Flask API on an Amazon EC2 compute instance in a public subnet, "
        "an Amazon RDS MySQL database isolated in private subnets, an Amazon SQS asynchronous queue with a Dead Letter Queue (DLQ), and an Amazon S3 "
        "private bucket using short-lived pre-signed URLs for secure media delivery. Test verification confirms high clustering accuracy, secure private "
        "data tiering, and non-blocking asynchronous report generation."
    )

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 2. INTRODUCTION
    # --------------------------------------------------------------------------
    add_heading_1("2. INTRODUCTION")
    add_heading_2("2.1 Project Background")
    add_p(
        "Public infrastructure such as paved roadways, pedestrian walkways, streetlights, stormwater drainage, and municipal water supply "
        "forms the foundation of urban livability. Timely maintenance of civic infrastructure is essential for public safety, commercial transit, and disaster prevention. "
        "In metropolitan regions like Mumbai, civic bodies receive thousands of defect reports each month across call centers, mobile applications, and web portals."
    )

    add_heading_2("2.2 Problem Statement")
    add_p(
        "Despite existing complaint mechanisms, municipal administrations face several critical bottlenecks:\n"
        "1. Complaint Duplication: When a severe defect appears on a busy road, dozens of citizens lodge separate complaints for the same incident. Staff must manually sift through redundant reports.\n"
        "2. Subjective Triage: Issues are typically handled in first-in, first-out (FIFO) order rather than prioritizing critical life-safety hazards.\n"
        "3. Cloud Security Gaps: Many municipal websites store complaint images in publicly accessible storage buckets and host unprotected databases with public IP addresses, risking sensitive resident data."
    )

    add_heading_2("2.3 Objectives and Scope")
    add_p(
        "The primary objectives of the CivicPulse project are:\n"
        "• To create an intuitive, geotagged web interface for citizens to submit defects with coordinates and photographs.\n"
        "• To automatically identify and cluster duplicate complaints using explainable distance and text comparison rules.\n"
        "• To calculate an objective, mathematical priority score (0–100) that directs emergency work to critical safety hazards first.\n"
        "• To deploy a multi-tier AWS cloud architecture that isolates sensitive database and storage records in private subnets with pre-signed access controls.\n"
        "• To provide an operations dashboard with role-based access for citizens, field workers, and administrators."
    )
    add_p(
        "Project Scope: The system manages reporting, triage, assignment, and SLA tracking for road, electrical, water, and sanitation defects. "
        "Physical maintenance operations and direct municipal accounting systems are outside the scope of this project."
    )

    # --------------------------------------------------------------------------
    # 3. EXISTING AND PROPOSED SYSTEM
    # --------------------------------------------------------------------------
    add_heading_1("3. EXISTING AND PROPOSED SYSTEM")
    add_heading_2("3.1 Limitations of Existing Systems")
    add_p(
        "Current municipal grievance portals act as basic databases with standard text input forms. Their primary limitations include:\n"
        "• No Spatial Awareness: Complaints are saved as plain text records without proximity comparisons, preventing automated duplicate detection.\n"
        "• Synchronous Bottlenecks: Heavy tasks like image thumbnailing and PDF generation run inside the main web request thread, causing page slowdowns and HTTP timeouts during heavy traffic.\n"
        "• Insecure Media Storage: Uploaded defect photos are frequently left in public directories with no access control or encryption.\n"
        "• Lack of SLA Accountability: No automated calculation of acknowledgment time or resolution deadlines based on defect urgency."
    )

    add_heading_2("3.2 Features of Proposed CivicPulse System")
    add_p(
        "CivicPulse overcomes these challenges through several key enhancements:\n"
        "• Automated Duplicate Grouping: Evaluates location coordinates and description wording to link redundant reports to a parent issue while preserving individual citizen tracking numbers.\n"
        "• Objective Multi-Factor Scoring: Combines severity levels, safety hazard flags, recurring report counts, and unresolved days into a clear 0–100 score.\n"
        "• Asynchronous Queue Pipeline: Uses Amazon SQS to offload background tasks to a dedicated worker, guaranteeing fast web page response times.\n"
        "• Secure Cloud Design: Houses database records in private subnets with no public internet access and delivers photos via time-limited, encrypted pre-signed S3 links."
    )

    add_heading_2("3.3 Comparative Evaluation")
    t_comp = doc.add_table(rows=6, cols=3)
    comp_headers = ["Evaluation Metric", "Traditional Portals", "Proposed CivicPulse"]
    comp_data = [
        ["Duplicate Handling", "Manual human cross-referencing", "Automated proximity (<=350m) & text overlap"],
        ["Priority Triage", "First-come, first-served (FIFO)", "Explainable 0–100 score based on hazard & SLA"],
        ["Database Security", "Single-tier with public IP", "Isolated in private subnets (No public IP)"],
        ["Photo Storage", "Public directory / unencrypted", "Private Amazon S3 with 1-hour pre-signed URLs"],
        ["Heavy Tasks (PDF/Export)", "Synchronous (blocks user UI)", "Decoupled via Amazon SQS & background daemon"]
    ]
    style_table(t_comp, [2.0, 2.1, 2.17], comp_headers, comp_data)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 4. SYSTEM ARCHITECTURE AND CLOUD DESIGN
    # --------------------------------------------------------------------------
    add_heading_1("4. SYSTEM ARCHITECTURE AND CLOUD DESIGN")
    add_heading_2("4.1 Multi-Tier Architecture Overview")
    add_p(
        "CivicPulse employs a 2-tier cloud architecture hosted in a custom Amazon Virtual Private Cloud (VPC). "
        "The infrastructure separates public client traffic from internal database storage, ensuring enterprise security and operational resilience."
    )
    add_p(
        "System Components & Flow:\n"
        "1. Client Layer: Citizens, field workers, and municipal admins access the system via modern web browsers.\n"
        "2. Public Subnet (Compute Tier): An Amazon EC2 instance (Ubuntu 22.04 LTS) runs Nginx on ports 80/443. Nginx serves the compiled React frontend "
        "and proxies API calls to the Gunicorn WSGI server running Flask on port 5000. An autonomous Python background daemon (worker.py) runs on the same instance.\n"
        "3. Private Subnet (Database Tier): An Amazon RDS for MySQL instance operates across a private DB subnet group with no public IP address. "
        "Inbound traffic on port 3306 is strictly limited to the EC2 security group.\n"
        "4. Managed Cloud Tier: Integrates Amazon S3 for private file storage, Amazon SQS for background queues, Amazon SNS for urgent alerts, "
        "and Amazon CloudWatch for health monitoring."
    )

    add_heading_2("4.2 AWS Cloud Component Roles")
    add_p(
        "• Amazon EC2: Runs web server, REST API, and queue-polling background workers with persistent database connection pooling.\n"
        "• Amazon RDS (MySQL): Manages relational tables for complaints, categories, user roles, SLA history, and cluster links.\n"
        "• Amazon S3: Stores photos and generated PDF reports under AES-256 server-side encryption with public access blocked.\n"
        "• Amazon SQS & DLQ: Decouples compute-heavy background tasks. Failed tasks retry up to 3 times before routing to the Dead Letter Queue.\n"
        "• Amazon SNS: Broadcasts instantaneous alerts to municipal teams when critical life hazards or high CPU alarms occur.\n"
        "• Amazon CloudWatch: Collects server logs and monitors CPU utilization, triggering automated alarms when CPU exceeds 80%."
    )

    add_heading_2("4.3 Network Isolation & Security")
    add_p(
        "• Amazon VPC CIDR: 10.0.0.0/16 with public subnet 10.0.1.0/24 and private subnets 10.0.2.0/24 & 10.0.3.0/24.\n"
        "• IAM Instance Profile: EC2 accesses S3, SQS, SNS, and CloudWatch through an attached IAM role, eliminating hardcoded access keys.\n"
        "• AWS SSM Parameter Store: Database passwords and session secrets are stored securely as encrypted SecureString parameters."
    )

    # --------------------------------------------------------------------------
    # 5. TECHNOLOGY STACK
    # --------------------------------------------------------------------------
    add_heading_1("5. TECHNOLOGY STACK")
    t_tech = doc.add_table(rows=11, cols=3)
    tech_headers = ["Layer", "Technology", "Role & Justification"]
    tech_data = [
        ["Frontend UI", "React 19 & TypeScript", "Component-based user interface with strict compile-time type safety."],
        ["Styling", "Tailwind CSS", "Utility-first framework for responsive layouts and mobile interfaces."],
        ["Mapping", "Leaflet.js", "Interactive map rendering for coordinate pin placement and hotspot markers."],
        ["Backend API", "Python 3.12 & Flask", "Lightweight, modular REST API with Blueprint routing."],
        ["Database ORM", "SQLAlchemy 2.0", "Object-relational mapping, relationship integrity, and transaction handling."],
        ["Database", "Amazon RDS (MySQL 8.0)", "Managed relational database engine for complaints and SLA tracking."],
        ["Cloud Storage", "Amazon S3", "Highly durable, private object storage with time-limited pre-signed URLs."],
        ["Message Queue", "Amazon SQS + DLQ", "Decouples background jobs with automated Dead Letter Queue retries."],
        ["Alerts", "Amazon SNS", "Pub/sub notification service for safety hazard alerts and server alarms."],
        ["Monitoring", "Amazon CloudWatch", "Centralized logging and automated CPU utilization alarms."]
    ]
    style_table(t_tech, [1.4, 1.8, 3.07], tech_headers, tech_data)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 6. METHODOLOGY AND IMPLEMENTATION
    # --------------------------------------------------------------------------
    add_heading_1("6. METHODOLOGY AND IMPLEMENTATION")
    add_heading_2("6.1 System Workflow")
    add_p(
        "The end-to-end operation of CivicPulse follows a clear 6-step lifecycle:\n"
        "1. Report Submission: Citizen marks a location pin on the Leaflet map, selects a defect category, enters title/description, and attaches an optional photo.\n"
        "2. Record Creation: Backend saves the issue in RDS, generates a unique public reference (e.g., CP-2026-AB12), and computes an initial priority score.\n"
        "3. Duplicate Check: The system queries active issues in the same category nearby and flags potential duplicates.\n"
        "4. Queue Dispatch: Dispatches an asynchronous job to SQS for background image validation and area indexing.\n"
        "5. Triage & Notification: If flagged as an urgent safety hazard (or priority >= 70), an alert is sent via SNS to municipal supervisors.\n"
        "6. Field Resolution: Field workers view assigned tasks, update status to 'In Progress', and mark issues 'Resolved' with notes for admin verification."
    )

    add_heading_2("6.2 Simplified Duplicate-Report Clustering")
    add_p(
        "To prevent duplicate complaints from cluttering the operations board, CivicPulse evaluates incoming reports using two simple, explainable checks:\n"
        "1. Distance Check (Haversine Formula): Calculates the real-world distance between the new report and existing active reports in the same category. "
        "If the distance is within 350 meters (0.35 km), the report qualifies for proximity matching.\n"
        "2. Word Overlap Check (Jaccard Similarity): Compares the common words between the titles and descriptions of both reports after removing punctuation and common stop words.\n"
        "3. Combined Decision: If both reports share the same category, are located within 350 meters, and have a word overlap score above 50%, "
        "the new report is linked to an existing cluster with a 'pending_review' tag. Both citizen complaints remain saved, ensuring full accountability."
    )

    add_heading_2("6.3 Transparent Priority Scoring Formula")
    add_p(
        "CivicPulse replaces subjective manual triage with an automated formula that assigns each defect a clear score between 0 and 100 points:\n"
        "• Base Severity: Citizen-selected severity (1 to 5) contributes up to 35 points (7 points per level).\n"
        "• Safety Hazard Bonus: Reports flagged as an immediate public danger (e.g., live wire, open manhole) receive +25 points.\n"
        "• Critical Infrastructure Bonus: Defects located on major arterial roads or transit corridors receive +15 points.\n"
        "• Duplicate Repetition Bonus: Each additional duplicate report in a cluster adds +3 points (up to +15 points max).\n"
        "• Unresolved Aging: Complaints open for more than 24 hours gain points over time (up to +10 points max).\n"
        "Along with the final score, the system stores a readable explanation string (e.g., 'Base level 4 + Safety hazard + 2 duplicate reports') "
        "so municipal administrators understand exactly why an issue received its priority."
    )

    add_heading_2("6.4 Asynchronous Worker & Secure S3 Storage")
    add_p(
        "• Asynchronous Queue: When an administrator requests a ward-wide summary or a citizen uploads an image, the API enqueues a lightweight message into Amazon SQS "
        "and immediately returns a success response. The background worker picks up the message, compiles the PDF/CSV report, and updates the database without freezing the web UI.\n"
        "• Pre-Signed S3 Access: Defect photos and generated reports are stored in an S3 bucket with public access disabled. "
        "When an authorized user views a photo or report, the backend generates an authenticated pre-signed URL valid for exactly 60 minutes, preventing unauthorized file sharing."
    )

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # 7. RESULTS AND TESTING
    # --------------------------------------------------------------------------
    add_heading_1("7. RESULTS AND TESTING")
    add_heading_2("7.1 User Interface Modules")
    add_p(
        "The system was fully implemented and evaluated across six responsive web modules:\n"
        "1. Public Issue Submission: Interactive Leaflet map with instant coordinate pin-drop, file upload validation (max 8MB, PNG/JPEG), and reference code generation.\n"
        "2. Municipal Operations Dashboard: Overview map displaying color-coded defect markers (red for high priority, yellow for medium, green for low), category filters, and SLA indicators.\n"
        "3. Duplicate Cluster Review: Side-by-side view showing candidate duplicates, distance in meters, word overlap percentage, and one-click 'Confirm' or 'Dismiss' buttons.\n"
        "4. Field Worker Portal: Clean list of assigned work orders allowing field teams to update statuses to 'In Progress' and submit completion notes.\n"
        "5. Public Tracking Page: Allows residents to check repair progress and view milestone timelines by entering their reference code (e.g., CP-2026-6FE7).\n"
        "6. Operations Report Center: One-click export of structured CSV data and formatted summary PDF documents saved directly to Amazon S3."
    )

    add_heading_2("7.2 Verification and Test Results")
    add_p("The backend and business algorithms were tested using the automated Pytest test suite. All 10 test cases passed successfully:")

    t_tests = doc.add_table(rows=11, cols=4)
    test_headers = ["ID", "Test Function", "Test Objective", "Result"]
    test_data = [
        ["TC-01", "test_health_endpoint", "Verify API server and database health status.", "PASS (200 OK)"],
        ["TC-02", "test_auth_login", "Verify JWT authentication and user role permissions.", "PASS (Role: admin)"],
        ["TC-03", "test_public_submission", "Verify issue creation and tracking by reference code.", "PASS (Reference generated)"],
        ["TC-04", "test_haversine_distance", "Verify accurate distance calculation between GPS points.", "PASS (Accurate to <0.1 km)"],
        ["TC-05", "test_text_similarity", "Verify Jaccard word overlap on matching defect descriptions.", "PASS (>40% match detected)"],
        ["TC-06", "test_duplicate_candidate", "Verify pothole reports within 25m are flagged as duplicates.", "PASS (Flagged for review)"],
        ["TC-07", "test_priority_base", "Verify baseline priority calculation for Level 1 severity.", "PASS (Score = 7.0)"],
        ["TC-08", "test_priority_hazard", "Verify +25 hazard bonus and +15 critical route bonus.", "PASS (Score = 75.0)"],
        ["TC-09", "test_priority_cluster", "Verify +6 point boost for 2 duplicate reports in cluster.", "PASS (+6.0 boost verified)"],
        ["TC-10", "test_priority_aging", "Verify score increases for unresolved issues over 48 hours.", "PASS (Aging factor applied)"]
    ]
    style_table(t_tests, [0.8, 1.9, 2.77, 0.8], test_headers, test_data)

    # --------------------------------------------------------------------------
    # 8. CONCLUSION AND FUTURE SCOPE
    # --------------------------------------------------------------------------
    add_heading_1("8. CONCLUSION AND FUTURE SCOPE")
    add_heading_2("8.1 Conclusion")
    add_p(
        "CivicPulse provides a practical, cloud-based solution for municipal infrastructure management. "
        "By replacing manual triage with automated geospatial duplicate clustering and transparent multi-factor priority scoring, the platform reduces administrative workload "
        "and accelerates response times for critical public safety hazards. "
        "The 2-tier AWS deployment demonstrates secure cloud design by isolating sensitive database records inside private VPC subnets, "
        "using Amazon SQS to handle background tasks without web server slowdowns, and delivering media through private Amazon S3 pre-signed URLs."
    )

    add_heading_2("8.2 Limitations")
    add_p(
        "• Exact Word Matching: Jaccard similarity relies on common words and may miss duplicates that use different synonyms (e.g., 'crater in road' vs. 'broken asphalt').\n"
        "• Single EC2 Host: The current deployment uses a single EC2 instance rather than an auto-scaling group with an Application Load Balancer.\n"
        "• Manual Verification: Verifying that a repair was successfully completed still requires manual administrative review."
    )

    add_heading_2("8.3 Future Improvements")
    add_p(
        "1. Semantic NLP Matching: Integrate lightweight AI text embeddings to detect duplicate complaints even when citizens use completely different phrasing or local languages.\n"
        "2. Auto-Scaling & Load Balancing: Add an AWS Application Load Balancer (ALB) across multiple availability zones to handle severe traffic spikes during monsoon emergencies.\n"
        "3. AI Image Verification: Implement a computer vision model that automatically compares the initial complaint photo with the field worker's repair photo to verify work completion."
    )

    # --------------------------------------------------------------------------
    # 9. REFERENCES
    # --------------------------------------------------------------------------
    add_heading_1("9. REFERENCES")
    refs = [
        "[1] Amazon Web Services, 'AWS Well-Architected Framework: Reliability and Security Pillars,' AWS Whitepapers, 2024. Available: https://docs.aws.amazon.com/wellarchitected/",
        "[2] R. W. Sinnott, 'Virtues of the Haversine,' Sky and Telescope, vol. 68, no. 2, p. 159, 1984.",
        "[3] P. Jaccard, 'The Distribution of the Flora in the Alpine Zone,' The New Phytologist, vol. 11, no. 2, pp. 37–50, 1912.",
        "[4] M. Grinberg, Flask Web Development: Developing Web Applications with Python, 2nd ed. O'Reilly Media, 2018.",
        "[5] React Documentation Team, 'React 19 Documentation,' Meta Platforms Inc., 2024. Available: https://react.dev/",
        "[6] Amazon Web Services, 'Amazon RDS User Guide: Security in Amazon RDS,' AWS Documentation, 2024. Available: https://docs.aws.amazon.com/rds/",
        "[7] Amazon Web Services, 'Amazon SQS Developer Guide: Dead-Letter Queues,' AWS Documentation, 2024. Available: https://docs.aws.amazon.com/sqs/",
        "[8] Leaflet Open-Source Project, 'Leaflet: JavaScript Library for Mobile-Friendly Interactive Maps,' 2024. Available: https://leafletjs.com/"
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(4)
        run_r = p_ref.add_run(r)
        run_r.font.name = 'Times New Roman'
        run_r.font.size = Pt(10)

    output_path = "C:/Users/SHWET/.gemini/antigravity/scratch/CivicPulse/CivicPulse_Mini_Project_Report.docx"
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    create_report()
