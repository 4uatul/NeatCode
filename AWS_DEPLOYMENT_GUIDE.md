# AWS Deployment Guide for NeatCode

## Overview
This guide covers deploying NeatCode on AWS using:
- **Frontend:** AWS S3 + CloudFront (CDN)
- **Backend:** AWS App Runner or Elastic Container Registry (ECR) + App Runner

## Cost Estimate
- **S3 + CloudFront:** ~$1-3/month (depending on traffic)
- **App Runner:** ~$7-25/month (based on usage)
- **Total:** ~$10-30/month

---

## Prerequisites

1. **AWS Account** - [Sign up here](https://aws.amazon.com/)
2. **AWS CLI** - [Install guide](https://aws.amazon.com/cli/)
3. **Docker** - [Install Docker](https://www.docker.com/products/docker-desktop/)
4. **Git** - Your code should be committed

---

## Part 1: Deploy Backend (Flask API) - AWS App Runner

### Step 1: Install AWS CLI and Configure

```bash
# Install AWS CLI (if not installed)
# Windows: Download from https://aws.amazon.com/cli/
# Mac: brew install awscli
# Linux: sudo apt-get install awscli

# Configure AWS credentials
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Output format: `json`

**Get credentials from AWS Console:**
1. Go to AWS Console → IAM → Users → Your User
2. Security Credentials → Create Access Key

---

### Step 2: Build and Push Docker Image to ECR

```bash
# Navigate to backend directory
cd Backend

# Create ECR repository
aws ecr create-repository --repository-name neatcode-backend --region us-east-1

# Get login command (authenticate Docker to ECR)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build Docker image
docker build -t neatcode-backend .

# Tag the image
docker tag neatcode-backend:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/neatcode-backend:latest

# Push to ECR
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/neatcode-backend:latest
```

**Find your Account ID:**
```bash
aws sts get-caller-identity --query Account --output text
```

---

### Step 3: Deploy with AWS App Runner

#### Option A: Using AWS Console (Easier)

1. Go to **AWS Console** → **App Runner**
2. Click **Create service**
3. Choose **Container registry** → **Amazon ECR**
4. Select your image: `neatcode-backend:latest`
5. Click **Next**
6. **Service settings:**
   - Service name: `neatcode-backend`
   - Port: `5000`
   - CPU: 1 vCPU
   - Memory: 2 GB
7. **Environment variables** (IMPORTANT):
   - Key: `GEMINI_API_KEY`
   - Value: `AIzaSyDk0vFZ9UFaYwLPJnZ0UdsQqhG0kGSglOw`
   - Key: `GEMINI_MODEL`
   - Value: `gemini-2.5-flash`
   - Key: `PORT`
   - Value: `5000`
8. Click **Next** → **Create & Deploy**

#### Option B: Using AWS CLI

```bash
# Create apprunner.yaml configuration
# This is done automatically by the service

# Deploy using CLI (requires apprunner.yaml)
aws apprunner create-service \
  --service-name neatcode-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/neatcode-backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "5000",
        "RuntimeEnvironmentVariables": {
          "GEMINI_API_KEY": "AIzaSyDk0vFZ9UFaYwLPJnZ0UdsQqhG0kGSglOw",
          "GEMINI_MODEL": "gemini-2.5-flash"
        }
      }
    }
  }' \
  --instance-configuration '{
    "Cpu": "1024",
    "Memory": "2048"
  }' \
  --region us-east-1
```

**Your backend will be live at:** `https://<random-id>.us-east-1.awsapprunner.com`

---

## Part 2: Deploy Frontend (React) - S3 + CloudFront

### Step 1: Build React App

```bash
# From project root
npm install
npm run build
```

This creates a `build/` folder with optimized static files.

---

### Step 2: Create S3 Bucket

```bash
# Create bucket (must be globally unique name)
aws s3 mb s3://neatcode-app-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://neatcode-app-frontend \
  --index-document index.html \
  --error-document index.html
```

---

### Step 3: Update Frontend API URL

Before building, update your frontend to use the App Runner backend URL:

1. Find your App Runner URL from AWS Console or:
```bash
aws apprunner list-services --region us-east-1
```

2. Update your React app's API endpoint (in your fetch calls):
```javascript
// Change from:
const API_URL = 'http://localhost:5000'

// To:
const API_URL = 'https://<your-app-runner-url>.awsapprunner.com'
```

3. Rebuild:
```bash
npm run build
```

---

### Step 4: Upload to S3

```bash
# Upload build folder to S3
cd build
aws s3 sync . s3://neatcode-app-frontend --acl public-read

# Or upload from root
aws s3 sync build/ s3://neatcode-app-frontend --acl public-read
```

---

### Step 5: Set S3 Bucket Policy (Make Public)

Create a file `bucket-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::neatcode-app-frontend/*"
    }
  ]
}
```

Apply it:
```bash
aws s3api put-bucket-policy --bucket neatcode-app-frontend --policy file://bucket-policy.json
```

**Your frontend is now live at:**
`http://neatcode-app-frontend.s3-website-us-east-1.amazonaws.com`

---

### Step 6: (Optional) Add CloudFront CDN for HTTPS & Speed

1. Go to **AWS Console** → **CloudFront** → **Create Distribution**
2. **Origin Domain:** Select your S3 bucket
3. **Default Root Object:** `index.html`
4. **Viewer Protocol Policy:** Redirect HTTP to HTTPS
5. Click **Create Distribution**

**CloudFront URL:** `https://<random-id>.cloudfront.net`

This gives you:
- HTTPS support
- Global CDN (faster loading)
- Custom domain support

---

## Part 3: Configure CORS for Backend

Your Flask backend needs to allow requests from your S3/CloudFront URL.

Update [Backend/app.py](Backend/app.py):

```python
# Change CORS configuration
CORS(app, origins=[
    "http://neatcode-app-frontend.s3-website-us-east-1.amazonaws.com",
    "https://<your-cloudfront-id>.cloudfront.net",
    "http://localhost:3000"  # for local development
])
```

Rebuild and redeploy backend:
```bash
cd Backend
docker build -t neatcode-backend .
docker tag neatcode-backend:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/neatcode-backend:latest
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/neatcode-backend:latest

# Trigger new App Runner deployment
aws apprunner start-deployment --service-arn <your-service-arn>
```

---

## Part 4: Custom Domain (Optional)

### For Frontend (S3/CloudFront):
1. Buy domain on Route 53 or use existing domain
2. Create CloudFront distribution (if not done)
3. Add CNAME record pointing to CloudFront URL
4. Add SSL certificate using AWS Certificate Manager (free)

### For Backend (App Runner):
1. Go to App Runner → Custom Domains
2. Add your domain (e.g., `api.neatcode.com`)
3. Update DNS with provided CNAME records

---

## Monitoring & Costs

### Check Costs:
- AWS Console → Billing Dashboard
- Set up billing alerts

### Monitor App Runner:
- AWS Console → App Runner → Metrics
- View logs in CloudWatch

### Estimate:
- **App Runner:** $0.007/vCPU-hour + $0.0008/GB-hour
  - 1 vCPU, 2GB, always-on: ~$7-10/month
- **S3:** $0.023/GB storage + $0.09/GB transfer
  - Small app: ~$1-2/month
- **CloudFront:** $0.085/GB for first 10TB
  - Low traffic: ~$1-3/month

**Total: $10-15/month for basic usage**

---

## Updating Your App

### Update Backend:
```bash
cd Backend
docker build -t neatcode-backend .
docker tag neatcode-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/neatcode-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/neatcode-backend:latest

# App Runner auto-deploys on new image push
```

### Update Frontend:
```bash
npm run build
aws s3 sync build/ s3://neatcode-app-frontend --delete

# Invalidate CloudFront cache (if using CloudFront)
aws cloudfront create-invalidation --distribution-id <distribution-id> --paths "/*"
```

---

## Alternative: Simpler AWS Deployment (Elastic Beanstalk)

If you want an even simpler approach:

### Backend with Elastic Beanstalk:
```bash
# Install EB CLI
pip install awsebcli

cd Backend

# Initialize EB
eb init -p docker neatcode-backend --region us-east-1

# Create environment and deploy
eb create neatcode-backend-env

# Set environment variables
eb setenv GEMINI_API_KEY=your-key GEMINI_MODEL=gemini-2.5-flash

# Deploy updates
eb deploy
```

Frontend stays the same (S3 + CloudFront).

---

## Troubleshooting

### Backend not starting:
- Check App Runner logs in CloudWatch
- Verify environment variables are set
- Test Docker image locally: `docker run -p 5000:5000 -e GEMINI_API_KEY=your-key neatcode-backend`

### CORS errors:
- Update CORS origins in app.py
- Redeploy backend

### Frontend can't reach backend:
- Verify API URL in frontend code
- Check App Runner security settings (should allow public access)

---

## Security Best Practices

1. **Never commit .env files** - Use AWS Secrets Manager for production
2. **Use IAM roles** instead of access keys when possible
3. **Enable CloudFront** for HTTPS
4. **Set up WAF** (Web Application Firewall) for protection
5. **Rotate Gemini API key** regularly
6. **Monitor costs** with billing alerts

---

## Summary of URLs

After deployment:
- **Backend API:** `https://<random-id>.us-east-1.awsapprunner.com`
- **Frontend (S3):** `http://neatcode-app-frontend.s3-website-us-east-1.amazonaws.com`
- **Frontend (CloudFront):** `https://<random-id>.cloudfront.net`

---

## Need Help?

- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [AWS S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [AWS CloudFront](https://docs.aws.amazon.com/cloudfront/)

Good luck with your deployment!
