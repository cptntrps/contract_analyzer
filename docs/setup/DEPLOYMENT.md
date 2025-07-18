# Contract Analyzer Deployment Guide

This guide covers deployment of the **refactored Contract Analyzer** with its new modular architecture. The application is now fully containerized and production-ready.

## 🏗️ Architecture Overview

The refactored application uses:
- **Flask Application Factory** pattern
- **Domain-Driven Design** architecture
- **Environment-based configuration**
- **RESTful API** endpoints
- **Comprehensive health checks**

## 🚀 Quick Deployment Options

### Option 1: Render (Recommended - Free)
1. Create account at https://render.com
2. Connect your GitHub repository
3. Select "New Web Service"
4. Use the `render.yaml` file included
5. Add environment variable: `OPENAI_API_KEY`
6. Deploy!

**Free tier includes:**
- 750 hours/month
- Auto-deploy from GitHub
- Custom domains

### Option 2: Railway
1. Install Railway CLI: `npm i -g @railway/cli`
2. Run: `railway login`
3. Run: `railway up`
4. Set environment variables in Railway dashboard

### Option 3: Heroku
```bash
# Install Heroku CLI first
heroku create your-contract-analyzer
heroku config:set OPENAI_API_KEY=your-key-here
git push heroku main
```

### Option 4: Docker Deployment

**Local Docker:**
```bash
# Build the image
docker build -t contract-analyzer .

# Run with environment variables
docker run -p 5000:5000 \
  -e OPENAI_API_KEY=your-key \
  -e FLASK_ENV=production \
  -e DEBUG=false \
  contract-analyzer
```

**Docker Compose (Development):**
```bash
# Start the full development stack
docker-compose up --build

# Access the application
open http://localhost:5000
```

**Google Cloud Run:**
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR-PROJECT/contract-analyzer

# Deploy to Cloud Run
gcloud run deploy --image gcr.io/YOUR-PROJECT/contract-analyzer --platform managed
```

**AWS ECS:**
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR-ECR-URI
docker build -t contract-analyzer .
docker tag contract-analyzer:latest YOUR-ECR-URI/contract-analyzer:latest
docker push YOUR-ECR-URI/contract-analyzer:latest
```

## 🔧 Environment Variables

### Required for all deployments:
```bash
OPENAI_API_KEY=your-openai-api-key     # Required for AI analysis
FLASK_ENV=production                    # Environment setting
DEBUG=false                            # Disable debug mode in production
```

### Optional configuration:
```bash
# Application settings
FLASK_HOST=0.0.0.0                     # Host binding (default: 127.0.0.1)
FLASK_PORT=5000                        # Port (default: 5000)
LOG_LEVEL=INFO                         # Logging level (DEBUG, INFO, WARNING, ERROR)

# LLM configuration
LLM_PROVIDER=openai                    # LLM provider (default: openai)
OPENAI_MODEL=gpt-4o                    # OpenAI model (default: gpt-4o)
LLM_TEMPERATURE=0.1                    # Temperature setting (default: 0.1)
LLM_MAX_TOKENS=512                     # Max tokens (default: 512)
LLM_TIMEOUT=30                         # Request timeout (default: 30)

# File handling
MAX_CONTENT_LENGTH=52428800            # Max file size in bytes (default: 50MB)
ALLOWED_EXTENSIONS=docx,doc            # Allowed file extensions

# Storage paths (for custom deployment)
UPLOAD_FOLDER=data/uploads             # Upload directory
TEMPLATES_FOLDER=data/templates        # Templates directory
REPORTS_FOLDER=data/reports            # Reports directory
```

### Platform-specific variables:
```bash
# For Render, Railway, Heroku (they set PORT automatically)
PORT=5000                              # Platform-assigned port

# For Google Cloud Run
FLASK_HOST=0.0.0.0                     # Required for GCR
PORT=8080                              # GCR default port
```

## 📝 Pre-deployment Checklist

1. **Update configuration for production:**
   - Set `DEBUG=False`
   - Use environment variables for secrets
   - Configure proper CORS if needed

2. **Security considerations:**
   - Enable HTTPS (most platforms do this automatically)
   - Set secure headers
   - Validate file uploads
   - Rate limiting

3. **Database considerations:**
   - Currently uses file system for storage
   - Consider cloud storage (S3, GCS) for production
   - Or use a database for metadata

## 🌐 Quick Deploy Buttons

### Deploy to Render
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Deploy to Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Deploy to Heroku
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## 🔒 Production Recommendations

1. **Use cloud storage** instead of local file system:
   - AWS S3
   - Google Cloud Storage
   - Azure Blob Storage

2. **Add authentication**:
   - Basic auth for simple protection
   - OAuth for enterprise use

3. **Set up monitoring**:
   - Application logs
   - Error tracking (Sentry)
   - Uptime monitoring

4. **Configure backups**:
   - Regular backups of uploaded files
   - Database backups if using one

## 📊 Estimated Costs

- **Render**: Free tier available, $7/month for starter
- **Railway**: $5/month after free tier
- **Heroku**: ~$7/month for hobby dyno
- **Google Cloud Run**: ~$5-20/month based on usage
- **AWS**: Variable, typically $10-50/month

## 🆘 Troubleshooting

**Port issues:**
- Most platforms assign their own port via environment variable
- Use `PORT` or `FLASK_PORT` environment variable

**File upload issues:**
- Ensure write permissions for upload directories
- Consider using cloud storage for production

**LLM connectivity:**
- Ollama won't work on most cloud platforms
- Use OpenAI API for cloud deployments

**Memory issues:**
- Large DOCX files may require more memory
- Increase instance size if needed