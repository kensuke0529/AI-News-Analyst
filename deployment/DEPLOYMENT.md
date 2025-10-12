# 🚀 AI News Analyst - Deployment Guide

This guide covers multiple deployment options for the AI News Analyst application with global token limiting.

## 📋 Prerequisites

- **OpenAI API Key**: Required for the application to function
- **Docker & Docker Compose**: For containerized deployment
- **Git**: For version control and cloud deployment

## 🏠 Local Deployment

### Option 1: Docker Compose (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd ai-news-analyst
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Deploy**:
   ```bash
   ./deploy.sh
   ```

4. **Access**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8002
   - API Status: http://localhost:8002/api/status

### Option 2: Direct Python

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

3. **Start services**:
   ```bash
   python start_production.py
   ```

## ☁️ Cloud Deployment

### Railway (Recommended for MVP)

1. **Connect your repository**:
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repository
   - Railway will auto-detect the `railway.json` configuration

2. **Set environment variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DAILY_TOKEN_LIMIT`: 5000 (or your preferred limit)

3. **Deploy**:
   - Railway will automatically build and deploy
   - Your app will be available at a Railway-provided URL

**Cost**: ~$5-10/month for basic usage

### Render

1. **Connect repository**:
   - Go to [Render.com](https://render.com)
   - Connect your GitHub repository
   - Select "Web Service"

2. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python start_production.py`
   - Environment: Python 3.11

3. **Set environment variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DAILY_TOKEN_LIMIT`: 5000

**Cost**: Free tier available, $7/month for paid plans

### DigitalOcean App Platform

1. **Create app**:
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Create new app from GitHub

2. **Configure**:
   - Use the `.do/app.yaml` configuration
   - Set environment variables in the dashboard

3. **Deploy**:
   - DigitalOcean will handle the deployment automatically

**Cost**: $5/month for basic plan

### Heroku

1. **Install Heroku CLI**:
   ```bash
   # Install Heroku CLI
   heroku login
   ```

2. **Create app**:
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set OPENAI_API_KEY="your_api_key_here"
   heroku config:set DAILY_TOKEN_LIMIT="5000"
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

**Cost**: $7/month for basic dyno

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | - | ✅ |
| `DAILY_TOKEN_LIMIT` | Daily token limit | 5000 | ❌ |
| `OPENAI_MODEL` | OpenAI model to use | gpt-4o-mini | ❌ |
| `VECTOR_DB_PATH` | Vector database path | ./data/vector_db | ❌ |

### Token Limits

The application includes a global daily token limit to control costs:

- **Default**: 5000 tokens per day
- **Cost**: ~$0.015-0.03 per day
- **Reset**: Daily at midnight (UTC)
- **Monitoring**: Check `/api/status` endpoint

## 📊 Monitoring & Maintenance

### Health Checks

- **Backend**: `GET /` returns 200 OK
- **API Status**: `GET /api/status` shows token usage
- **Frontend**: Serves static files on port 3000

### Logs

**Docker Compose**:
```bash
docker-compose logs -f
```

**Direct Python**:
```bash
python start_production.py
```

### Database Population

To populate the news database:

```bash
# Docker
docker-compose exec ai-news-analyst python src/data_ingestion/extract_and_store.py

# Direct Python
python src/data_ingestion/extract_and_store.py
```

## 🔒 Security Considerations

1. **API Key Protection**:
   - Never commit API keys to version control
   - Use environment variables or secure vaults
   - Rotate keys regularly

2. **Rate Limiting**:
   - Built-in token limiting prevents abuse
   - Consider additional rate limiting for production

3. **CORS Configuration**:
   - Currently allows all origins (`*`)
   - Restrict to your domain in production

## 🚨 Troubleshooting

### Common Issues

1. **"Daily token limit reached"**:
   - Check `/api/status` for current usage
   - Wait for daily reset or increase limit

2. **Backend not responding**:
   - Check if port 8002 is available
   - Verify environment variables are set
   - Check logs for errors

3. **Frontend not loading**:
   - Check if port 3000 is available
   - Verify backend is running
   - Check browser console for errors

4. **Docker build fails**:
   - Ensure Docker is running
   - Check if all files are present
   - Verify Dockerfile syntax

### Debug Commands

```bash
# Check service status
curl http://localhost:8002/api/status

# View container logs
docker-compose logs ai-news-analyst

# Check environment variables
docker-compose exec ai-news-analyst env

# Test API endpoints
curl -X POST http://localhost:8002/api/news/rag \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?"}'
```

## 📈 Scaling Considerations

### For Higher Traffic

1. **Increase token limits**:
   - Modify `DAILY_TOKEN_LIMIT` environment variable
   - Monitor costs and usage patterns

2. **Add caching**:
   - Implement Redis for response caching
   - Cache frequent queries

3. **Load balancing**:
   - Use multiple backend instances
   - Implement proper session management

4. **Database optimization**:
   - Use persistent volumes for ChromaDB
   - Implement database backups

## 💰 Cost Estimation

| Usage Level | Daily Tokens | Monthly Cost | Platform Cost |
|-------------|--------------|--------------|---------------|
| Light | 1,000 | ~$0.50 | $5-10 |
| Medium | 5,000 | ~$2.50 | $10-20 |
| Heavy | 20,000 | ~$10.00 | $20-50 |

## 🎯 Next Steps

1. **Choose deployment platform** based on your needs
2. **Set up monitoring** and alerting
3. **Configure custom domain** (optional)
4. **Set up automated backups**
5. **Implement additional security measures**

---

**Need help?** Check the troubleshooting section or create an issue in the repository.
