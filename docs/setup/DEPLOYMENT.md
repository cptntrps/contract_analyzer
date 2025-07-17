# Contract Analyzer Deployment Guide

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
docker build -t contract-analyzer .
docker run -p 8080:8080 -e OPENAI_API_KEY=your-key contract-analyzer
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

Required for all deployments:
```
FLASK_HOST=0.0.0.0
FLASK_PORT=8080 (or platform-specific)
OPENAI_API_KEY=your-openai-api-key
LLM_PROVIDER=openai
```

Optional:
```
DEBUG=false
FLASK_ENV=production
MAX_CONTENT_LENGTH=16777216
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