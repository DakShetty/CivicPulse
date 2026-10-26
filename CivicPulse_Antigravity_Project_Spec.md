# CivicPulse --- Cloud-Based Public Infrastructure Issue Intelligence

## Instructions for the Antigravity coding agent

Treat this document as the primary project specification. First inspect
the existing workspace and report what is already present. Then
implement the project in small, testable phases. Do not overwrite
existing files without checking them first. Prefer a working,
understandable application over unnecessary complexity. Ask before
destructive actions or provisioning paid AWS resources.

## 1. Project summary

**Project name:** CivicPulse\
**Project type:** Cloud Computing mini project\
**Core idea:** A cloud-hosted platform for reporting, grouping,
prioritizing, tracking, and analyzing local public infrastructure issues
such as potholes, broken streetlights, water leaks, damaged footpaths,
overflowing bins, and drainage problems.

The project must be more than a basic complaint CRUD application. Its
differentiators are duplicate-report clustering, hotspot analytics,
issue-priority scoring, service-level tracking, asynchronous
media/report processing, and area-level insights.

Use fictional/sample records and clearly marked demo data unless real
data is explicitly authorized. Do not claim the platform is connected to
a municipal authority or that a complaint has been officially submitted.

## 2. Problem statement and goals

Residents may report the same local infrastructure problem through
different channels, while responsible teams need to understand which
issues are urgent, repeated, unresolved, or concentrated in particular
areas. CivicPulse provides one place to submit reports, attach photos
and locations, group likely duplicates, prioritize issues, track
resolution, and visualize trends.

Goals: - Provide a polished responsive public-facing reporting interface
and an administrative operations dashboard. - Support issue reports with
category, description, approximate location, severity indicators,
timestamp, and optional photo. - Identify likely duplicate reports using
transparent, explainable rules. - Map issue clusters and show recurring
infrastructure hotspots. - Calculate an explainable priority score using
severity, safety risk, number of similar reports, and time unresolved. -
Track assignment, status changes, acknowledgement time, and resolution
time. - Store uploaded images and generated reports privately in S3. -
Generate CSV/PDF summaries. - Demonstrate meaningful AWS compute,
networking, database, storage, IAM/security, monitoring, and additional
cloud capabilities. - Keep the main web application and backend running
on EC2. This must **not** be a completely serverless application.

## 3. Roles and access

Implement role-based access: - **Reporter:** create reports, view their
own reports, and see public-safe status updates. - **Field worker:**
view assigned issues, add progress updates, and mark work as completed
pending verification. - **Administrator:** manage categories,
assignments, priority settings, reports, and analytics.

For the classroom demo, include seeded demo data and documented local
setup. Provide a safe way to create the first administrator. Never
hard-code production passwords or AWS credentials. Do not commit secrets
or expose private reporter details on public pages.

## 4. Functional requirements

### 4.1 Public reporting workflow

-   Submit an issue category, short title, description, and approximate
    location.
-   Allow a map pin or latitude/longitude entry where mapping
    configuration is available.
-   Upload an optional photo with file type and size validation.
-   Generate a unique report reference number.
-   Show confirmation and current status.
-   Do not require exact home addresses; allow approximate locations and
    warn users not to include personal information in photos or
    descriptions.

### 4.2 Issue categories

Seed categories such as: - Pothole/road damage - Broken streetlight -
Water leakage - Drainage/flooding - Waste overflow - Damaged footpath -
Public facility damage - Other infrastructure issue

Categories should be configurable rather than hard-coded throughout the
application.

### 4.3 Duplicate-report clustering

Implement an explainable first version: - Compare reports within a
configurable distance threshold. - Compare category and text
similarity. - Consider reports within a configurable time window. - If
similarity exceeds a configurable threshold, suggest an existing issue
cluster rather than silently merging reports. - Let an administrator
confirm, separate, or dismiss a duplicate suggestion. - Keep original
report records and an audit trail; never delete a report just because it
resembles another. - Make the logic testable and describe its
limitations. Do not claim perfect duplicate detection.

Use a simple geospatial distance calculation and text similarity to
start. Keep advanced ML optional.

### 4.4 Priority scoring

Implement a transparent, configurable score using factors such as: -
Reported severity. - Potential safety risk. - Number of similar reports
in a cluster. - Time unresolved. - Whether the issue affects access or
critical public infrastructure.

Display the score and a short explanation of why the issue received its
priority. Avoid presenting the score as an official government rating.

### 4.5 Map and hotspot analytics

-   Show issues on an interactive map when map tiles/configuration are
    available.
-   Cluster nearby markers to avoid a cluttered map.
-   Filter by category, status, priority, date, and area.
-   Display hotspots by area and recurring issue category.
-   Provide a table-based alternative if the map service is unavailable.
-   Do not expose reporter names, email addresses, or precise personal
    information in public map views.

Use a mapping library such as Leaflet with a suitable tile provider.
Document any external tile-provider limits; do not assume map tiles are
an AWS service or unlimited/free.

### 4.6 Status and service-level tracking

Use a workflow such as:
`Submitted → Triaged → Assigned → In Progress → Resolved → Verified/Closed`
Allow a report to be marked `Rejected` only with a reason and authorized
role.

Record timestamps for submission, acknowledgement, assignment, progress,
resolution, and verification. Calculate time-to-acknowledge and
time-to-resolve. Show overdue issues based on configurable targets.

### 4.7 Notifications

-   Provide in-app notifications.
-   Use Amazon SNS for email alerts where configured, such as
    assignment, status change, or critical safety report.
-   Use deduplication and a cooldown to avoid notification spam.
-   Record notification attempts and safe error summaries.
-   Document SNS email subscription confirmation.

### 4.8 Attachments and reports

-   Store issue photos and generated CSV/PDF reports in a private S3
    bucket.
-   Save metadata and S3 object keys in RDS.
-   Generate short-lived pre-signed URLs only after authorization
    checks.
-   Never make the bucket public.
-   Generate date/category/area summaries with issue counts, status
    breakdown, hotspots, and resolution-time metrics.

### 4.9 Admin analytics

Dashboard should include: - Total reports and new reports over time. -
Open, overdue, and resolved issue counts. - Issues by category and
priority. - Median/average acknowledgement and resolution times. -
Duplicate clusters and recurring hotspots. - Filters for date range,
category, status, and approximate area. - Clearly label sample/demo
data.

### 4.10 Audit trail

Record key actions such as report creation, duplicate review, priority
changes, assignment, status changes, export generation, and
administrative configuration changes. Do not store passwords, session
tokens, secrets, or unnecessary personal data in logs.

## 5. Recommended technology stack

-   **Frontend:** React + TypeScript + Vite + Tailwind CSS.
-   **Map:** Leaflet and a documented tile provider, with a non-map
    fallback.
-   **Charts:** a maintained React charting library.
-   **Backend:** Python Flask with modular blueprints.
-   **Database:** MySQL on Amazon RDS; SQLAlchemy and migrations.
-   **Authentication:** secure server-side sessions or a reviewed token
    approach; password hashing; secure cookies in production.
-   **AWS SDK:** boto3 for S3, SQS, SNS, and Parameter Store.
-   **Testing:** pytest for backend and business logic; frontend
    build/lint checks.
-   **Version control:** Git; include `.env.example`, `.gitignore`, and
    README.

Keep AWS credentials and database secrets out of frontend code. Pin
compatible dependency versions and keep the code understandable enough
for a student to explain.

## 6. AWS architecture --- mandatory base

The architecture must use a **custom VPC** and the main application must
run on EC2.

### Network design

-   One custom VPC with documented CIDR range.
-   Public subnet for EC2 application host, with an Internet Gateway and
    suitable route.
-   Private subnets in at least two Availability Zones for an RDS DB
    subnet group; choose an affordable single-AZ RDS deployment for the
    student demo if supported by the account/region.
-   RDS must have no public IP and must not be publicly accessible.
-   EC2 security group: allow HTTP/HTTPS only as appropriate; restrict
    SSH to the student's current IP or use Systems Manager Session
    Manager.
-   RDS security group: allow MySQL only from the EC2 application
    security group.
-   Do not create a NAT Gateway in the baseline architecture because it
    can be expensive. Document safe alternatives for outbound access.
-   Never open MySQL or SSH to `0.0.0.0/0`.

### Required AWS services and functional purposes

1.  **Amazon EC2 --- compute:** runs the Flask backend, frontend/reverse
    proxy, and a small background worker.
2.  **Amazon VPC --- networking:** isolates the application and database
    and defines network boundaries.
3.  **Internet Gateway and route tables --- connectivity:** provide
    controlled public web access and route traffic.
4.  **Amazon RDS for MySQL --- database:** stores reports, users, issue
    clusters, assignments, status history, categories, audit events, and
    report metadata.
5.  **Amazon S3 --- object storage:** stores issue photos, imported
    datasets, and generated reports in private buckets/prefixes.
6.  **AWS IAM --- identity/access:** EC2 instance role with
    least-privilege access to only required resources.
7.  **AWS Systems Manager Parameter Store --- secrets/config:** store
    database credentials as SecureString and other environment
    configuration server-side. Use encryption where appropriate.
8.  **Amazon CloudWatch --- monitoring:** application logs, EC2 metrics,
    dashboards, and log queries.
9.  **CloudWatch Alarm --- operational alerting:** at least one
    meaningful alarm such as sustained EC2 CPU, EC2 status-check
    failure, or custom metric for repeated processing failures.
10. **Amazon SNS --- notifications:** send issue assignment/critical
    issue email alerts and CloudWatch alarm notifications.
11. **Amazon SQS --- asynchronous processing:** queue image metadata
    processing, duplicate-analysis jobs, or report generation. A worker
    process on EC2 must poll and process the queue. Configure retries,
    visibility timeout, and a dead-letter queue (DLQ).
12. **AWS Budgets --- cost control:** monthly budget and email alerts if
    permissions allow. Explain that a budget alert does not
    automatically stop resources.
13. **AWS CloudFormation --- infrastructure as code:** templates for
    repeatable deployment of selected infrastructure; parameterize
    values and document possible charges.
14. **AWS CloudTrail --- AWS control-plane audit:** use Event history to
    demonstrate reviewing resource/API actions. If creating a trail to
    S3, document scope and possible charges.
15. **Amazon EventBridge --- event/schedule routing:** optionally
    schedule daily summary generation or route selected
    application-support events. Use only if it is implemented and
    tested.
16. **AWS Lambda --- supporting task only:** optional scheduled daily
    summary or small cleanup task. The core web application,
    authentication, report workflow, and issue processing must remain on
    EC2.

Do not claim that every listed service is deployed merely because the
design document mentions it. Clearly distinguish implemented services
from planned/optional services in the final report.

## 7. Additional capabilities --- optional, justify cost before deployment

### A. Application Load Balancer + EC2 Auto Scaling

-   Optional stretch goal to demonstrate scaling the EC2 application.
-   May incur charges even with little traffic; do not provision by
    default without explicit approval.
-   If not deployed, include a future-state architecture diagram
    labelled "proposed, not deployed."

### B. Amazon CloudFront

-   Optional delivery/caching of public frontend assets if it offers a
    clear benefit.
-   Never expose private issue photos or reports through a public
    distribution.
-   Omit if cost or complexity is not justified.

### C. Amazon Rekognition (optional, only if useful)

-   Could identify broad image labels for issue triage, but it is not
    required.
-   Do not rely on image labels as authoritative evidence; require human
    confirmation.
-   Check pricing, privacy implications, and regional availability
    before using it. A simple image-upload workflow is sufficient for
    the base project.

### D. AWS KMS

-   Use customer-managed keys only if there is a justified requirement
    and cost/permissions are understood.
-   Suitable default encryption options may be sufficient for the
    student baseline.

Do not add DynamoDB, NAT Gateway, Multi-AZ RDS, WAF, ECR/ECS, or other
services solely to increase the service count. Every service must have a
clear implemented purpose.

## 8. Suggested database entities

Create migrations and suitable foreign keys/indexes for: - `users`: id,
display name, email, password hash, role, active flag, created
timestamp. - `issue_categories`: id, name, description, default priority
settings, active flag. - `issues`: id, public reference, reporter id,
category id, title, description, latitude/longitude or approximate
location, severity, priority score, status, created timestamp. -
`issue_attachments`: id, issue id, S3 object key, file type, size,
uploaded timestamp. - `issue_clusters`: id, representative issue id,
cluster status, created timestamp. - `issue_cluster_members`: cluster
id, issue id, similarity explanation, reviewed status. - `assignments`:
issue id, field-worker id, assigned by, assigned timestamp. -
`status_history`: issue id, old status, new status, actor, timestamp,
note. - `audit_events`: actor id when applicable, action, entity
type/id, timestamp, safe metadata. - `reports`: requesting user, report
type, filters/date range, S3 object key, status, created timestamp. -
`notification_events`: issue id, channel, status, attempted timestamp,
safe error summary. - `processing_jobs`: job type, status, retry count,
related entity id, timestamps, safe error summary.

Avoid storing unnecessary personal information. Keep public-safe fields
separate from administrative/private fields.

## 9. API outline

Use versioned endpoints such as: - `POST /api/v1/auth/login` -
`POST /api/v1/auth/logout` - `POST /api/v1/issues` -
`GET /api/v1/issues` - `GET /api/v1/issues/{id}` -
`PATCH /api/v1/issues/{id}/status` -
`POST /api/v1/issues/{id}/attachments` -
`GET /api/v1/issues/{id}/history` - `GET /api/v1/clusters` -
`POST /api/v1/clusters/{id}/review` - `GET /api/v1/analytics/summary` -
`GET /api/v1/analytics/hotspots` - `POST /api/v1/reports` -
`GET /api/v1/reports/{id}` - `GET /api/v1/health`

Validate input, paginate list endpoints, enforce role checks, and return
consistent errors. Avoid exposing internal IDs or personal data
unnecessarily.

## 10. UI and design direction

Build a modern civic operations dashboard: - Light neutral background
with deep navy text and restrained teal/amber/red status colors. - Clear
typography, map + issue list layout, readable charts, useful filters. -
Public reporting flow should be simple and mobile-friendly. - Admin
sidebar: Overview, Issue Map, Reports, Clusters, Assignments, Analytics,
Audit Log, Settings. - Field-worker view: My Assignments, Issue Details,
Add Update, Mark Resolved. - Accessible contrast and labels; do not rely
on color alone. - Show status, priority, age, and location clearly. -
Include loading, empty, error, and map-unavailable states. - Label demo
data visibly. Do not invent official government logos, endorsements, or
integrations.

## 11. Security and privacy requirements

-   No hard-coded AWS credentials, database passwords, or secrets.
-   Use the EC2 instance profile for AWS API access.
-   Retrieve database secrets server-side from Parameter Store
    SecureString.
-   Keep RDS private; restrict its security group to the EC2 application
    security group.
-   Enable S3 Block Public Access and encryption.
-   Use short-lived pre-signed URLs after authorization checks.
-   Validate file type/size and generate safe S3 object keys; do not
    trust uploaded filenames.
-   Implement authentication, authorization, CSRF protection where
    applicable, rate limiting, and secure session configuration.
-   Minimize personal information and keep reporter contact details
    private.
-   Add a clear privacy notice and a report-abuse/rate-limit strategy.
-   Never log passwords, session tokens, secrets, or unnecessary
    personal data.
-   Do not claim production-grade security without testing.

## 12. Monitoring and alarms

At minimum: - Send structured application logs to CloudWatch Logs. -
Monitor EC2 CPU and status checks. - Configure at least one CloudWatch
alarm and route its notification through SNS. - Log CSV/image processing
failures, duplicate-job failures, report failures, and notification
errors safely. - If practical, publish custom metrics such as
`CivicPulse/NewIssues`, `CivicPulse/ProcessingFailures`, and
`CivicPulse/OverdueIssues`. - Document a safe alarm test and list the
screenshots needed for evidence.

## 13. Cost and lifecycle management

The project must stay within the student's Free Tier eligibility or
available credits. Check current regional pricing and account
eligibility before deployment; never assume a service is free.

-   Use a small EC2 instance and smallest suitable single-AZ RDS
    configuration.
-   Avoid NAT Gateway, Multi-AZ RDS, always-on load balancers, large
    instances, and unnecessary always-running resources unless
    explicitly approved.
-   Keep S3 storage and CloudWatch log retention modest.
-   Configure AWS Budgets monthly alert thresholds if allowed.
-   Provide `COSTS.md` with region, instance/database sizes,
    storage/traffic assumptions, pricing source/date, and possible
    charges.
-   Include teardown instructions. Stopping EC2 does not necessarily
    remove EBS, public IPv4, snapshots, or other billable resources.
-   Never automatically delete cloud resources or user data without
    explicit confirmation.

## 14. Testing and acceptance criteria

The project is complete only when: 1. A reporter can submit an issue and
receive a reference number. 2. An optional image can be uploaded and
stored privately in S3. 3. Reports appear in the admin dashboard and
map/table view. 4. Similar reports can be suggested as duplicates with
an explanation; an admin can review the suggestion. 5. Priority scoring
is visible and explainable. 6. Authorized staff can assign, acknowledge,
update, resolve, and verify an issue. 7. Status history and audit events
are recorded. 8. CSV/PDF reports can be generated, stored in private S3,
and downloaded by authorized users. 9. At least one genuine background
job is processed through SQS by the EC2 worker. 10. RDS is private and
only reachable from the app security group. 11. AWS access uses an IAM
role; secrets are loaded from Parameter Store and are not hard-coded.
12. CloudWatch receives logs and at least one meaningful alarm is
configured. 13. SNS notification works when configured, or a clear
setup/test procedure is documented if AWS access is not available. 14. A
budget alert is configured if permissions allow; otherwise exact manual
steps and the limitation are documented. 15. Tests cover priority
scoring, duplicate suggestions, status permissions, upload validation,
and report access. 16. The README describes implemented vs planned
services honestly.

## 15. College submission deliverables

Generate: - `README.md` --- setup, architecture, local demo, deployment,
cleanup. - `ARCHITECTURE.md` --- architecture explanation and Mermaid
diagram. - `COSTS.md` --- cost estimate with assumptions and pricing
date. - `SECURITY.md` --- network, IAM, secrets, privacy, storage, and
limitations. - `DEMO_SCRIPT.md` --- a 5--7 minute demonstration
sequence. - `screenshots/` checklist --- do not fabricate screenshots or
claim undeployed resources exist. - Infrastructure templates and
deployment scripts. - Backend/frontend tests and sample data. - A
service justification table covering every AWS service actually used. -
A clear list of assumptions and limitations.

## 16. Implementation sequence

**Phase 1 --- Inspect and plan** - Inspect workspace; report existing
files, risks, proposed file tree, and implementation plan. - Do not
overwrite existing work without checking it.

**Phase 2 --- Local MVP** - Implement frontend, backend, auth/roles,
database models, seeded sample reports, issue workflow, duplicate
suggestions, priority scoring, map/table view, analytics, and tests. -
Provide `.env.example` with placeholders only. - Use local development
configuration so the app works without AWS credentials.

**Phase 3 --- AWS integrations** - Add S3 attachment/report storage, SQS
background processing, SNS notifications, Parameter Store, and
CloudWatch integration in small testable modules. - Keep local
mocks/development mode where practical.

**Phase 4 --- AWS deployment** - Prepare custom VPC, EC2, private RDS,
IAM role/policies, S3, SQS, SNS, CloudWatch, and budget setup. - Do not
deploy paid resources without explicit user approval.

**Phase 5 --- Optional services** - Consider EventBridge/Lambda
scheduled summaries, CloudFront, or ALB/Auto Scaling only after the core
system works and costs are reviewed.

**Phase 6 --- Final validation** - Run tests and frontend build. -
Review security groups, IAM scope, S3 access, secrets, and data
privacy. - Generate architecture diagram, cost estimate, evidence
checklist, and demo script.

## 17. Instructions for every phase

-   Explain whether each command runs locally, on EC2, or in the AWS
    Console.
-   Provide copy-pasteable commands and explain placeholders.
-   Do not fabricate AWS resource IDs, deployment results, screenshots,
    test results, or costs.
-   If AWS credentials/access are unavailable, build and test locally
    and give exact deployment instructions.
-   Do not create resources that may incur charges without explicit
    approval.
-   If a requirement conflicts with account permissions or cost
    constraints, explain it and propose the lowest-cost compliant
    option.
-   Keep the implementation simple enough for a student to explain in a
    viva.

**First action:** inspect the current workspace and return a concise
plan, proposed file tree, and risks. Then start with the local MVP. Do
not provision AWS resources at the start.
