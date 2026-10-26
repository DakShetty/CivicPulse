# ==============================================================================
# CivicPulse Master Automated AWS Deployment Script
# Automatically provisions VPC, Security Groups, IAM, S3, SQS, SNS, RDS, & EC2
# ==============================================================================
$ErrorActionPreference = "Stop"

# Detect Region from AWS CLI or fallback to ap-south-1
$REGION = aws configure get region
if (-not $REGION) {
    $REGION = "ap-south-1"
}

$ENV_NAME = "civicpulse-demo"
$AMI_ID = "ami-082a1ff88c78c6290" # Ubuntu 22.04 LTS in ap-south-1
if ($REGION -eq "us-east-1") {
    $AMI_ID = "ami-0c7217cdde317cfec"
}

# Generate secure random DB password
$DB_PASSWORD = "CP" + (-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})) + "!"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " CivicPulse Cloud Infrastructure Automated Deployment" -ForegroundColor Cyan
Write-Host " Target Region: $REGION" -ForegroundColor Cyan
Write-Host " Environment:   $ENV_NAME" -ForegroundColor Cyan
Write-Host " Base AMI:       $AMI_ID" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Step 0: Validate CloudFormation Templates
Write-Host "==> [0/5] Validating CloudFormation templates..." -ForegroundColor Yellow
aws cloudformation validate-template --template-body file://infrastructure/cloudformation/01-vpc-network.yaml --region $REGION | Out-Null
aws cloudformation validate-template --template-body file://infrastructure/cloudformation/02-security-iam.yaml --region $REGION | Out-Null
aws cloudformation validate-template --template-body file://infrastructure/cloudformation/03-storage-messaging.yaml --region $REGION | Out-Null
aws cloudformation validate-template --template-body file://infrastructure/cloudformation/04-ec2-rds-app.yaml --region $REGION | Out-Null
Write-Host "  Templates validated successfully.`n" -ForegroundColor Green

# Step 1: Deploy VPC & Networking
Write-Host "==> [1/5] Deploying Stack 1: Custom VPC, Subnets, and IGW..." -ForegroundColor Yellow
aws cloudformation deploy `
  --template-file infrastructure/cloudformation/01-vpc-network.yaml `
  --stack-name "$ENV_NAME-vpc" `
  --parameter-overrides EnvironmentName=$ENV_NAME `
  --no-fail-on-empty-changeset `
  --region $REGION

$VPC_ID = (aws cloudformation describe-stacks --stack-name "$ENV_NAME-vpc" --query "Stacks[0].Outputs[?OutputKey=='VpcId'].OutputValue" --output text --region $REGION).Trim()
$PUBLIC_SUBNET_ID = (aws cloudformation describe-stacks --stack-name "$ENV_NAME-vpc" --query "Stacks[0].Outputs[?OutputKey=='PublicSubnetId'].OutputValue" --output text --region $REGION).Trim()
$DB_SUBNET_GROUP = (aws cloudformation describe-stacks --stack-name "$ENV_NAME-vpc" --query "Stacks[0].Outputs[?OutputKey=='DBSubnetGroupName'].OutputValue" --output text --region $REGION).Trim()
Write-Host "  VPC Deployed: $VPC_ID`n" -ForegroundColor Green

# Step 2: Deploy Security Groups & IAM Role
Write-Host "==> [2/5] Deploying Stack 2: Security Groups and IAM Instance Profile..." -ForegroundColor Yellow
aws cloudformation deploy `
  --template-file infrastructure/cloudformation/02-security-iam.yaml `
  --stack-name "$ENV_NAME-security" `
  --parameter-overrides EnvironmentName=$ENV_NAME VpcId=$VPC_ID `
  --capabilities CAPABILITY_IAM `
  --no-fail-on-empty-changeset `
  --region $REGION

$EC2_SG_ID = (aws cloudformation describe-stacks --stack-name "$ENV_NAME-security" --query "Stacks[0].Outputs[?OutputKey=='EC2SecurityGroupId'].OutputValue" --output text --region $REGION).Trim()
$RDS_SG_ID = (aws cloudformation describe-stacks --stack-name "$ENV_NAME-security" --query "Stacks[0].Outputs[?OutputKey=='RDSSecurityGroupId'].OutputValue" --output text --region $REGION).Trim()
$EC2_PROFILE_NAME = (aws cloudformation describe-stacks --stack-name "$ENV_NAME-security" --query "Stacks[0].Outputs[?OutputKey=='EC2InstanceProfileName'].OutputValue" --output text --region $REGION).Trim()
Write-Host "  Security Groups & Profile Deployed.`n" -ForegroundColor Green

# Step 3: Deploy Private S3, SQS & SNS
Write-Host "==> [3/5] Deploying Stack 3: Private S3 Bucket, SQS Queue, and SNS Topic..." -ForegroundColor Yellow
aws cloudformation deploy `
  --template-file infrastructure/cloudformation/03-storage-messaging.yaml `
  --stack-name "$ENV_NAME-storage" `
  --parameter-overrides EnvironmentName=$ENV_NAME `
  --no-fail-on-empty-changeset `
  --region $REGION

$BUCKET_NAME = (aws cloudformation describe-stacks --stack-name "$ENV_NAME-storage" --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text --region $REGION).Trim()
$SQS_QUEUE_URL = (aws cloudformation describe-stacks --stack-name "$ENV_NAME-storage" --query "Stacks[0].Outputs[?OutputKey=='JobsQueueUrl'].OutputValue" --output text --region $REGION).Trim()
$SNS_TOPIC_ARN = (aws cloudformation describe-stacks --stack-name "$ENV_NAME-storage" --query "Stacks[0].Outputs[?OutputKey=='AlertsTopicArn'].OutputValue" --output text --region $REGION).Trim()
Write-Host "  Storage & Messaging Deployed. S3: $BUCKET_NAME`n" -ForegroundColor Green

# Step 4: Save Database Password to SSM Parameter Store
Write-Host "==> [4/5] Storing RDS master secret in AWS Parameter Store..." -ForegroundColor Yellow
aws ssm put-parameter `
  --name "/$ENV_NAME/prod/DB_PASSWORD" `
  --value $DB_PASSWORD `
  --type "SecureString" `
  --overwrite `
  --region $REGION | Out-Null
Write-Host "  Stored password SecureString at /$ENV_NAME/prod/DB_PASSWORD`n" -ForegroundColor Green

# Step 5: Deploy Private RDS MySQL & EC2 Application Host
Write-Host "==> [5/5] Deploying Stack 4: Private RDS MySQL, EC2 App Host, & CloudWatch..." -ForegroundColor Yellow
Write-Host "  (Note: RDS instance creation takes approximately 8-12 minutes to initialize)" -ForegroundColor DarkGray
aws cloudformation deploy `
  --template-file infrastructure/cloudformation/04-ec2-rds-app.yaml `
  --stack-name "$ENV_NAME-app" `
  --parameter-overrides `
      EnvironmentName=$ENV_NAME `
      VpcId=$VPC_ID `
      PublicSubnetId=$PUBLIC_SUBNET_ID `
      DBSubnetGroupName=$DB_SUBNET_GROUP `
      EC2SecurityGroupId=$EC2_SG_ID `
      RDSSecurityGroupId=$RDS_SG_ID `
      EC2InstanceProfileName=$EC2_PROFILE_NAME `
      AlertsTopicArn=$SNS_TOPIC_ARN `
      DBPassword=$DB_PASSWORD `
      AmiId=$AMI_ID `
  --no-fail-on-empty-changeset `
  --region $REGION

$RDS_ENDPOINT = (aws cloudformation describe-stacks --stack-name "$ENV_NAME-app" --query "Stacks[0].Outputs[?OutputKey=='RDSEndpoint'].OutputValue" --output text --region $REGION).Trim()
$EC2_PUBLIC_IP = (aws cloudformation describe-stacks --stack-name "$ENV_NAME-app" --query "Stacks[0].Outputs[?OutputKey=='EC2PublicIP'].OutputValue" --output text --region $REGION).Trim()

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host " CivicPulse AWS Cloud Infrastructure Successfully Deployed!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host " EC2 Public IP:       $EC2_PUBLIC_IP" -ForegroundColor White
Write-Host " Private RDS MySQL:   $RDS_ENDPOINT (Private, no public IP)" -ForegroundColor White
Write-Host " Private S3 Bucket:   $BUCKET_NAME" -ForegroundColor White
Write-Host " SQS Job Queue:       $SQS_QUEUE_URL" -ForegroundColor White
Write-Host " SNS Alerts Topic:    $SNS_TOPIC_ARN" -ForegroundColor White
Write-Host " Region:              $REGION" -ForegroundColor White
Write-Host "============================================================`n" -ForegroundColor Green
