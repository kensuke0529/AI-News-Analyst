# 🚂 Railway Deployment Troubleshooting

## 🚨 **"Error creating build plan with Railpack" - SOLVED**

This error occurs when Railway can't properly detect your build configuration. Here are the solutions:

## ✅ **Solution 1: Use Root Dockerfile (Recommended)**

I've created a Railway-optimized setup:

1. **Root Dockerfile**: `Dockerfile` in the root directory
2. **Railway config**: `railway.json` in the root directory
3. **Updated paths**: All file references updated for the new structure

### Deploy Steps:
1. **Commit and push** your changes to GitHub
2. **Connect to Railway** and select your repository
3. **Railway will automatically detect** the Dockerfile and railway.json
4. **Add environment variables**:
   - `OPENAI_API_KEY=your_api_key_here`
   - `DAILY_TOKEN_LIMIT=5000` (optional)

## ✅ **Solution 2: Alternative Railway Configuration**

If Docker still fails, try this approach:

### Option A: Use Procfile
Railway will automatically detect the `Procfile` and use it instead of Docker.

### Option B: Manual Railway Setup
1. **Go to Railway dashboard**
2. **Create new project**
3. **Select "Empty Project"**
4. **Connect your GitHub repo**
5. **Go to Settings → Build**
6. **Set Build Command**: `pip install -r config/requirements.txt`
7. **Set Start Command**: `python scripts/run_backend.py & python scripts/serve_frontend.py & wait`

## 🔧 **Common Railway Issues & Fixes**

### 1. **Build Fails - "Module not found"**
**Fix**: Ensure all files are committed to GitHub
```bash
git add .
git commit -m "Fix Railway deployment"
git push origin main
```

### 2. **Port Issues**
**Fix**: Railway automatically detects ports from Dockerfile
- Make sure `EXPOSE 8002 3000` is in Dockerfile
- Railway will use port 8002 for the backend

### 3. **Environment Variables Not Working**
**Fix**: Add variables in Railway dashboard
- Go to your project → Variables tab
- Add `OPENAI_API_KEY=your_key_here`
- Redeploy after adding variables

### 4. **Application Won't Start**
**Fix**: Check the start command
- Current: `python scripts/run_backend.py & python scripts/serve_frontend.py & wait`
- Make sure all script files exist in `scripts/` folder

## 🚀 **Step-by-Step Railway Deployment**

### Step 1: Prepare Repository
```bash
# Make sure all files are committed
git add .
git commit -m "Fix Railway deployment configuration"
git push origin main
```

### Step 2: Deploy to Railway
1. **Go to [railway.app](https://railway.app)**
2. **Sign in with GitHub**
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**
6. **Railway will auto-detect the configuration**

### Step 3: Configure Environment
1. **Go to Variables tab**
2. **Add**: `OPENAI_API_KEY=your_openai_api_key_here`
3. **Add**: `DAILY_TOKEN_LIMIT=5000` (optional)
4. **Save and redeploy**

### Step 4: Test Deployment
1. **Wait for build to complete** (2-3 minutes)
2. **Click on your project URL**
3. **Test the application**

## 📊 **Railway Configuration Files**

### `railway.json` (Root directory)
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python scripts/run_backend.py & python scripts/serve_frontend.py & wait",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### `Dockerfile` (Root directory)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*
COPY config/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/data/vector_db /app/storage/databases/chroma_db
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app
EXPOSE 8002 3000
CMD ["sh", "-c", "python scripts/run_backend.py & python scripts/serve_frontend.py & wait"]
```

## 🎯 **Expected Results**

After successful deployment:
- **Frontend**: `https://your-app.railway.app`
- **Backend API**: `https://your-app.railway.app:8002`
- **API Status**: `https://your-app.railway.app:8002/api/status`
- **Token tracking**: Working with 5000 daily limit

## 🆘 **Still Having Issues?**

### Check Railway Logs
1. **Go to your Railway project**
2. **Click on "Deployments"**
3. **Click on the latest deployment**
4. **Check the logs for specific errors**

### Common Error Messages
- **"Build failed"**: Check that all files are committed
- **"Port not found"**: Verify EXPOSE ports in Dockerfile
- **"Module not found"**: Check requirements.txt path
- **"Permission denied"**: Check file permissions

### Alternative Deployment
If Railway continues to fail, try:
- **Render**: Use `deployment/render.yaml`
- **DigitalOcean**: Use `deployment/.do/app.yaml`
- **Local Docker**: Use `deployment/deploy.sh`

---

**🎉 The Railway deployment should now work with the updated configuration!**
