# ⚡ AI News Analyst - Quick Start

Get your AI News Analyst up and running in 5 minutes!

## 🚀 Fastest Deployment (Docker)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd ai-news-analyst

# 2. Set up environment
cp config/env.example .env
# Edit .env and add your OpenAI API key

# 3. Deploy
./deployment/deploy.sh
```

**That's it!** Your app will be running at:
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend: http://localhost:8002

## ☁️ Cloud Deployment (Railway)

1. **Push to GitHub** (if not already)
2. **Go to [Railway.app](https://railway.app)**
3. **Connect your repository**
4. **Add environment variable**: `OPENAI_API_KEY=your_key_here`
5. **Deploy!**

Railway will automatically detect the configuration and deploy your app.

## 🔑 Required Setup

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com)
2. Create an API key
3. Add it to your `.env` file or cloud platform environment variables

### Token Limits
- **Default**: 5000 tokens per day (~$0.02/day)
- **Adjustable**: Change `DAILY_TOKEN_LIMIT` in environment
- **Monitoring**: Check `/api/status` endpoint

## 📱 Using the Application

1. **Open the frontend** (http://localhost:3000)
2. **Ask questions** about recent news or general knowledge
3. **Monitor usage** via the status bar at the top
4. **View news articles** in the grid below

## 🛠️ Useful Commands

```bash
# Check status
curl http://localhost:8002/api/status

# View logs (Docker)
docker-compose -f deployment/docker-compose.yml logs -f

# Stop services (Docker)
docker-compose -f deployment/docker-compose.yml down

# Populate news database
python src/data_ingestion/extract_and_store.py
```

## 🆘 Need Help?

- **Full documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: Check the troubleshooting section
- **Support**: Create an issue in the repository

---

**Ready to deploy?** Choose your method above and you'll be running in minutes! 🎉
