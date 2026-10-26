# CivicPulse — 5–7 Minute Classroom Demonstration & Viva Script

This script provides an exact step-by-step walkthrough for presenting CivicPulse during project evaluation, practical exams, or a viva voce.

---

## Part 1: Introduction & Architecture (0:00 – 0:45)

* **Spoken Pitch:**
  > "CivicPulse is a cloud-hosted public infrastructure issue intelligence platform. Rather than being a basic complaint portal, it solves a real municipal operations problem: duplicate complaints from multiple citizens, triage prioritization, and SLA resolution tracking. The architecture runs on Amazon EC2 within a custom VPC, backed by a private Amazon RDS MySQL database, private S3 object storage with pre-signed URLs, an SQS asynchronous worker queue, and CloudWatch operational monitoring."
* **Screen Display:** Open the web app at `http://localhost:5173`. Point out the banner indicating the custom VPC/EC2 cloud architecture.

---

## Part 2: Public Reporting & Instant Duplicate Detection (0:45 – 2:00)

1. Click **"Report Issue"** in the navigation header.
2. Select **"Pothole / Road Damage"**.
3. Fill in the demo details:
   * **Title:** `Severe asphalt cavity near 5th Cross`
   * **Description:** `Deep road pothole on Market Street causing vehicle damage.`
   * **Severity:** Slide to **Level 4**.
   * **Safety Hazard:** Check the box *(imminent risk of injury)*.
   * **Location:** Click on the interactive map near Market Street (coordinates automatically populate).
4. Click **"Submit Public Report"**.
5. **Key Talking Point:**
   * Point out the generated tracking reference number (e.g., `CP-2026-XXXX`).
   * Highlight the **Duplicate Warning Banner**:
     > "Notice that CivicPulse immediately ran geospatial distance and Jaccard text similarity against existing open reports. It detected an existing report 35 meters away with 74% text similarity and automatically grouped them into an issue cluster to escalate maintenance attention."
6. Click **"Track Live Status"** to show the citizen tracking stepper.

---

## Part 3: Operations Map & Explainable Priority Scoring (2:00 – 3:15)

1. Click **"Operations Map"** on the navbar.
2. **Key Talking Point:**
   * Explain the interactive Leaflet map with color-coded pins:
     * Red: High Priority (&gt;70) or Safety Hazard
     * Amber: Moderate Priority (45–69)
     * Green: Resolved
   * Toggle to **"Table View"** to demonstrate accessibility when map tile providers are unavailable.
3. Click on the high-priority pothole issue:
   * Point to the **Explainable Priority Score (e.g., 81/100)**:
     > "Our priority engine is completely transparent. It breaks down the exact score: Base severity level 4 (+28 pts); Direct public safety hazard (+25 pts); Confirmed in a cluster of 2 reports (+3 pts); Category multiplier x1.2."
4. Transition the issue from `Submitted` $\rightarrow$ `Triaged` $\rightarrow$ `Assigned`.

---

## Part 4: Duplicate Clusters & Admin Deduplication Review (3:15 – 4:15)

1. Click **"Duplicate Clusters"** in the navigation bar.
2. **Key Talking Point:**
   * Show the Market Street Pothole Cluster.
   * Highlight the explainable link: `Located 35m apart; Same category; 74% text similarity; Composite score: 88%`.
   * Explain Section 4.3 compliance:
     > "We never silently delete complaints. Each report keeps its original record and timestamps. The administrator can click 'Confirm Duplicate' to coordinate a single repair crew, or 'Separate' if they are distinct defects."
3. Click **"Confirm Duplicate"**.

---

## Part 5: Field Worker Execution Console (4:15 – 5:15)

1. Use the **Role Switcher** in the navbar to click **"Worker"**.
2. Notice the view automatically switches to the **Field Worker Console**.
3. Select the assigned work order:
   * Add a field note: `Dispatched repair truck. Asphalt patch applied and compacted.`
   * Click **"Mark Work Completed (Resolved)"**.
4. The issue status immediately updates to `Resolved`, recording the resolution timestamp.

---

## Part 6: SLA Hotspots Analytics & PDF Report Generation (5:15 – 6:15)

1. Switch back to **"Admin"** and click **"Hotspots & SLA"**.
2. Point out the SLA KPI cards:
   * **Avg Time to Acknowledge:** `4.2 hrs` (Target &le; 24h)
   * **Avg Time to Resolve:** `36.5 hrs` (Target &le; 72h)
   * **Geographic Hotspots:** Shows Downtown Central with highest complaint density.
3. Click **"Exports"** tab.
4. Click **"Generate PDF Brief"**.
5. Once generated, click **"Download"**:
   * Open the generated PDF report.
   * Explain:
     > "This executive brief is rendered by the backend and stored privately in S3. It is served to authorized administrators via a short-lived, authenticated pre-signed URL."

---

## Part 7: Cloud Architecture & Viva Q&A (6:15 – 7:00)

* **Anticipated Viva Question 1:** *Why didn't you use AWS Lambda for the entire application?*
  * **Answer:** "The specification explicitly required an EC2 application host within a custom VPC to demonstrate traditional cloud networking, systemd service management, and persistent queue worker polling. Lambda is only suitable for small scheduled trigger tasks in this architecture."
* **Anticipated Viva Question 2:** *How is the database protected?*
  * **Answer:** "Amazon RDS is deployed in private subnets across two AZs with no public IP address. Its security group permits MySQL connections ONLY from the EC2 application host security group."
* **Anticipated Viva Question 3:** *Why is there no NAT Gateway in the architecture?*
  * **Answer:** "A NAT Gateway costs over $32/month. Because the EC2 instance resides in the public subnet with an Internet Gateway, it accesses AWS APIs and internet packages directly via its IAM instance profile, keeping the student architecture within Free Tier credits."
