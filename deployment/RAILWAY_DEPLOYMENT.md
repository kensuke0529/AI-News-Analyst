# 🚂 Railway Deployment Guide

This guide will help you deploy the AI News Analyst to Railway successfully.

## 🚀 Quick Railway Deployment

### Step 1: Prepare Your Repository

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Organize project structure and add Railway deployment"
   git push origin main
   ```

### Step 2: Deploy to Railway

1. **Go to [Railway.app](https://railway.app)**
2. **Sign in** with your GitHub account
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your AI News Analyst repository**
6. **Railway will automatically detect the configuration**

### Step 3: Configure Environment Variables

1. **Go to your project dashboard**
2. **Click on "Variables" tab**
3. **Add the following environment variables**:

| Variable | Value | Description |
|----------|-------|-------------|
| `OPENAI_API_KEY` | `your_openai_api_key_here` | **Required** - Your OpenAI API key |
| `DAILY_TOKEN_LIMIT` | `5000` | Daily token limit (optional) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use (optional) |
| `VECTOR_DB_PATH` | `/app/data/vector_db` | Vector database path (optional) |

### Step 4: Deploy

1. **Railway will automatically start building**
2. **Wait for the build to complete** (usually 2-3 minutes)
3. **Your app will be available at the Railway-provided URL**

## 🔧 Troubleshooting Railway Deployment

### Common Issues and Solutions

#### 1. **"Error creating build plan with Railpack"**

**Problem**: Railway can't detect the build configuration.

**Solution**: 
- Make sure `railway.json` is in the root directory
- Verify the Dockerfile path in `railway.json` is correct
- Check that all required files are committed to GitHub

#### 2. **Build Fails During Docker Build**

**Problem**: Docker build process fails.

**Solution**:
- Check that `config/requirements.txt` exists
- Verify all file paths in Dockerfile are correct
- Ensure all source files are present

#### 3. **Application Won't Start**

**Problem**: App builds but doesn't start properly.

**Solution**:
- Check environment variables are set correctly
- Verify `OPENAI_API_KEY` is valid
- Check Railway logs for error messages

#### 4. **Port Issues**

**Problem**: Railway can't connect to the application.

**Solution**:
- Railway automatically detects ports from Dockerfile
- Make sure `EXPOSE 8002 3000` is in Dockerfile
- Check that the start command is correct

## 📊 Railway Configuration Details

### Current Configuration (`railway.json`)

```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "deployment/Dockerfile"
  },
  "deploy": {
    "startCommand": "python scripts/run_backend.py & python scripts/serve_frontend.py & wait",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Environment Variables Required

- **`OPENAI_API_KEY`** (Required): Your OpenAI API key
- **`DAILY_TOKEN_LIMIT`** (Optional): Default 5000 tokens/day
- **`OPENAI_MODEL`** (Optional): Default gpt-4o-mini
- **`VECTOR_DB_PATH`** (Optional): Default /app/data/vector_db

## 🎯 Railway-Specific Features

### Automatic Deployments
- Railway automatically deploys when you push to GitHub
- No manual deployment needed
- Automatic rollback on deployment failures

### Custom Domain
1. **Go to your project settings**
2. **Click "Domains"**
3. **Add your custom domain**
4. **Configure DNS records as instructed**

### Monitoring
- **Logs**: Available in Railway dashboard
- **Metrics**: CPU, memory, and network usage
- **Health checks**: Automatic health monitoring

## 💰 Railway Pricing

### Free Tier
- **$5 credit monthly**
- **512MB RAM**
- **1GB storage**
- **Perfect for development and small projects**

### Pro Plan
- **$5/month per service**
- **8GB RAM**
- **100GB storage**
- **Better for production use**

## 🔍 Post-Deployment

### 1. Test Your Deployment

Visit your Railway URL and test:
- **Frontend**: `https://your-app.railway.app`
- **Backend API**: `https://your-app.railway.app:8002`
- **API Status**: `https://your-app.railway.app:8002/api/status`

### 2. Populate News Database

```bash
# SSH into your Railway instance (if needed)
railway shell

# Run the data ingestion script
python src/data_ingestion/extract_and_store.py
```

### 3. Monitor Usage

- **Check token usage** via the status bar in the UI
- **Monitor logs** in Railway dashboard
- **Set up alerts** for high usage or errors

## 🆘 Getting Help

### Railway Support
- **Documentation**: [docs.railway.app](https://docs.railway.app)
- **Discord**: [Railway Discord](https://discord.gg/railway)
- **GitHub**: [Railway GitHub](https://github.com/railwayapp)

### Common Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# View logs
railway logs

# Open shell
railway shell
```

---

**🎉 Your AI News Analyst should now be successfully deployed on Railway!**

If you're still having issues, check the Railway logs in your dashboard for specific error messages.
