# CivicPulse Security & Privacy Model

## 1. Network Boundary Isolation

CivicPulse implements multi-tiered network isolation within a custom Amazon VPC (`10.0.0.0/16`):
* **Public Tier (Subnet `10.0.1.0/24`):**
  * Contains the EC2 application host running Nginx and Gunicorn.
  * Ingress: HTTP (port 80) and HTTPS (port 443) from public internet.
  * SSH (port 22): Restricted to the student's personal IP address or managed via AWS Systems Manager Session Manager (eliminating port 22 entirely).
* **Private Database Tier (Subnets `10.0.10.0/24` & `10.0.11.0/24`):**
  * Contains Amazon RDS for MySQL across two Availability Zones.
  * `PubliclyAccessible: false` is strictly enforced.
  * Security Group Ingress: **MySQL (port 3306) is allowed ONLY from the EC2 Security Group ID.**
  * Ingress from `0.0.0.0/0` is strictly forbidden.

---

## 2. Identity, Credential & Secrets Management

* **No Hardcoded Credentials:** The source repository contains zero hardcoded AWS secret keys, session tokens, or database passwords. All local testing uses `.env` (ignored in `.gitignore`).
* **IAM Instance Profile:** The EC2 instance accesses AWS services (S3, SQS, SNS, Parameter Store) via an attached IAM role (`CivicPulseLeastPrivilegePolicy`).
* **AWS Parameter Store:** Production database credentials and environment secrets are fetched at runtime from SSM Parameter Store as encrypted `SecureString` parameters.

---

## 3. Object Storage Security (Amazon S3)

* **S3 Block Public Access:** All four public access block settings (`BlockPublicAcls`, `BlockPublicPolicy`, `IgnorePublicAcls`, `RestrictPublicBuckets`) are enabled.
* **Server-Side Encryption:** All objects (issue attachments and generated reports) are encrypted at rest using `AES256`.
* **Short-Lived Pre-Signed URLs:** Private objects are accessed strictly via cryptographic pre-signed URLs generated on the backend with an expiration window of 3,600 seconds (1 hour). Anonymous users cannot read S3 bucket contents.

---

## 4. Citizen Privacy & Data Protection

* **Public vs Private Segregation:**
  * Public APIs (`GET /api/v1/issues`, `GET /api/v1/issues/track/{ref}`) return only sanitized issue details: approximate community area, category, description, and status.
  * Citizen names, email addresses, phone numbers, and exact home addresses are stripped from public responses and visible only to authorized administrators.
* **Photo Upload Sanitization:**
  * Uploaded filenames are discarded. Files are renamed using cryptographic UUIDs (`attachments/<uuid>.ext`) to prevent path traversal or metadata leakage.
  * Maximum upload size is strictly capped at 8 MB with MIME-type verification.

---

## 5. Audit Logging & Compliance

All sensitive operational actions are recorded in the `audit_events` table:
* Issue creation and location coordinates
* Duplicate review confirmations, separations, and dismissals
* Status transitions (`Submitted` $\rightarrow$ `Triaged` $\rightarrow$ `Assigned` $\rightarrow$ `Resolved`)
* Work order assignment to field personnel
* Compliance CSV/PDF report downloads
* Administrative user logins with IP address tracking
