# CivicPulse Cost & Lifecycle Management Guide

**Pricing Reference Date:** October 2026  
**Reference Region:** `us-east-1` (US East - N. Virginia)  
**Target Environment:** Academic Demonstration / Free Tier Eligible

---

## 1. Monthly Cost Estimate Breakdown

| Resource / Component | Specification | Free Tier Allowance | Est. Monthly Cost (Free Tier Active) | Est. Monthly Cost (Post-Free Tier) |
| :--- | :--- | :--- | :--- | :--- |
| **Amazon EC2** | 1x `t3.micro` or `t4g.micro` (Ubuntu Linux) | 750 hours/month | **$0.00** | ~$7.45 |
| **EBS Storage** | 20 GB gp3 root volume | 30 GB/month | **$0.00** | ~$1.60 |
| **Public IPv4 Address** | 1 In-use public IPv4 on EC2 | Not included in Free Tier | ~$3.65 ($0.005/hr) | ~$3.65 |
| **Amazon RDS for MySQL** | 1x `db.t4g.micro` or `db.t3.micro` (Single-AZ) | 750 hours/month | **$0.00** | ~$12.41 |
| **RDS Storage** | 20 GB General Purpose SSD (gp3) | 20 GB/month | **$0.00** | ~$2.30 |
| **Amazon S3** | 1 GB storage, 5,000 PUT/GET requests | 5 GB storage, 20,000 GETs | **$0.00** | ~$0.05 |
| **Amazon SQS** | ~10,000 queue operations/month | 1,000,000 requests/month | **$0.00** | **$0.00** |
| **Amazon SNS** | ~500 email alerts/month | 1,000 emails, 1M notifications | **$0.00** | **$0.00** |
| **Amazon CloudWatch** | 1 Alarm, 500 MB logs (14d retention) | 10 alarms, 5 GB log ingestion | **$0.00** | **$0.00** |
| **NAT Gateway** | *Deliberately Omitted* | No Free Tier | **$0.00 (Saved ~$32.85/mo)** | **$0.00** |
| **Estimated Total** | | | **~$3.65 / month** | **~$27.46 / month** |

> [!NOTE]
> AWS charges $0.005/hr for in-use public IPv4 addresses (~$3.65/month). To achieve $0.00 out-of-pocket cost, complete the demonstration within AWS Academy learner credits or teardown the EC2 instance when not in active evaluation.

---

## 2. Intentional Cost-Optimization Decisions

1. **No NAT Gateway:** A NAT Gateway costs ~$0.045/hour plus data processing fees (~$32.85/month minimum). In CivicPulse, the EC2 instance resides in a public subnet with an Internet Gateway, allowing direct package downloads and AWS API calls via an IAM instance profile without requiring a NAT Gateway.
2. **Single-AZ RDS Deployment:** Multi-AZ RDS doubles the instance and storage cost. For student demonstrations, single-AZ in private subnets with automated 1-day backup is selected.
3. **Log Retention Limits:** CloudWatch log groups are explicitly capped at 14 days retention to prevent silent billing creep.
4. **S3 Multipart Lifecycle:** Incomplete uploads expire after 2 days to prevent hidden uncompleted chunks.

---

## 3. AWS Budgets Setup Instructions

To prevent accidental credit exhaustion:
1. Open the **AWS Billing and Cost Management Console**.
2. Select **Budgets** $\rightarrow$ **Create budget**.
3. Choose **Cost budget (Recommended)**.
4. Set the budget amount to **$5.00 USD / month**.
5. Configure an alert threshold at **80% ($4.00)** and **100% ($5.00)** with notification to your student email address.

---

## 4. Complete Teardown & Resource Destruction Guide

When your grading or presentation is complete, delete the cloud resources in reverse order to ensure no ongoing charges:

### Step 1: Empty the S3 Bucket
Before CloudFormation can delete an S3 bucket, it must be empty:
```bash
aws s3 rm s3://civicpulse-demo-storage-<account-id> --recursive
```

### Step 2: Delete CloudFormation Stacks
```bash
# 1. Delete application & database stack
aws cloudformation delete-stack --stack-name civicpulse-app

# 2. Delete storage & messaging stack
aws cloudformation delete-stack --stack-name civicpulse-storage

# 3. Delete security & IAM stack
aws cloudformation delete-stack --stack-name civicpulse-security

# 4. Delete VPC & networking stack
aws cloudformation delete-stack --stack-name civicpulse-vpc
```

### Step 3: Verify Deletion in AWS Console
Check the following dashboards to ensure 0 active resources remain:
* **EC2 Dashboard:** Instances = 0, Volumes = 0, Elastic IPs = 0.
* **RDS Dashboard:** Databases = 0, Automated Backups cleaned.
* **S3 Dashboard:** Bucket removed.
