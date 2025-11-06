# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- 8GB RAM minimum
- **OpenAI API key** (for AI features) OR 16GB+ RAM (for local LLM)

---

## Step 1: Clone & Setup

```bash
git clone https://github.com/komparedocers/Autonomous-Marketeer.git
cd Autonomous-Marketeer
bash setup.sh
```

---

## Step 2: Configure LLM Provider

### Option A: Use OpenAI (Recommended for Quick Start) ✅

Edit `.env` file and add your OpenAI API key:

```bash
# Open .env file
nano .env  # or use your preferred editor

# Find this line and add your API key:
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Save and exit
```

**That's it!** OpenAI is already enabled by default in the .env file.

### Option B: Use Local LLM (Advanced) ⚠️

**Requirements:**
- 16GB+ RAM
- 20GB+ free disk space
- Time for model download (7GB)

Edit `.env`:
```bash
LLM_PROVIDER=local
LLM_DEFAULT_PROVIDER=local
OPENAI_ENABLED=false
LOCAL_LLM_ENABLED=true
```

**Note:** First startup will be slow (10-15 minutes) as it downloads the Mistral-7B model.

---

## Step 3: Start the Platform

```bash
# Start all services
docker-compose up --build

# Wait for all services to start (2-3 minutes)
# Watch for "INFO:     Application startup complete" messages
```

**Expected startup sequence:**
1. ✅ PostgreSQL initializes (30 seconds)
2. ✅ Redis starts
3. ✅ ClickHouse initializes
4. ✅ MinIO starts
5. ✅ LLM Router loads (fast with OpenAI, slow with local)
6. ✅ API Gateway starts
7. ✅ Frontend builds and starts

---

## Step 4: Access the Dashboard

Open your browser:
```
http://localhost:5173
```

**Login:**
- Email: `admin@demo.com`
- Password: `demo123`

---

## 🐛 Troubleshooting

### Issue: PostgreSQL exits with "relation does not exist"
**Fix:** This is normal! Tables are created by the API service. Just restart:
```bash
docker-compose down
docker-compose up
```

### Issue: LLM Router fails with NumPy errors
**Fix:** This is fixed in the latest version. If you still see it:
```bash
docker-compose down
docker-compose build --no-cache llmrouter
docker-compose up
```

### Issue: Local LLM fails to load model
**Solution:** Use OpenAI instead (see Step 2, Option A) or:
1. Ensure you have 16GB+ RAM
2. Wait 10-15 minutes for model download
3. Check Docker logs: `docker-compose logs llmrouter`

### Issue: Frontend won't load
**Fix:** Wait 2-3 minutes for npm build, then refresh browser

### Issue: "Cannot connect to API"
**Fix:** Ensure API is running:
```bash
docker-compose logs api
# Should see: "Application startup complete"
```

---

## 🎯 Next Steps

Once logged in:

1. **Check LLM Status** → Go to "AI Agents" page
2. **Create a Campaign** → Go to "Campaigns" → Click "New Campaign"
3. **Run an Agent** → API: `POST /agents/run`
4. **View Analytics** → Go to "Analytics" page

---

## 📝 Configuration Guide

### Switch Between OpenAI and Local LLM

**In Dashboard:**
1. Go to Settings
2. Toggle LLM Provider
3. Restart services if needed

**In .env file:**
```bash
# Use OpenAI (fast, requires API key)
LLM_PROVIDER=openai
OPENAI_ENABLED=true
LOCAL_LLM_ENABLED=false

# Use Local LLM (slow first start, offline)
LLM_PROVIDER=local
OPENAI_ENABLED=false
LOCAL_LLM_ENABLED=true

# Use both (switch in dashboard)
LLM_PROVIDER=both
OPENAI_ENABLED=true
LOCAL_LLM_ENABLED=true
```

---

## 🔧 Common Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild everything
docker-compose down
docker-compose build --no-cache
docker-compose up

# Reset database
docker-compose down -v
docker-compose up
```

---

## ✅ System Health Checks

Once running, verify services:

- ✅ **API**: http://localhost:8080/health
- ✅ **LLM Router**: http://localhost:9090/health
- ✅ **Attribution**: http://localhost:8085/health
- ✅ **Analytics**: http://localhost:8086/health
- ✅ **Dashboard**: http://localhost:5173
- ✅ **MinIO Console**: http://localhost:9001 (minio/minio123)
- ✅ **Grafana**: http://localhost:3000 (admin/admin)

---

## 💡 Pro Tips

1. **For development**: Keep local LLM disabled to save resources
2. **For production**: Use OpenAI API for reliability
3. **For offline/privacy**: Use local LLM but allocate sufficient resources
4. **First time?** Start with OpenAI, experiment with local LLM later

---

## 📞 Need Help?

- Check full README.md for detailed documentation
- View logs: `docker-compose logs -f [service-name]`
- Reset everything: `docker-compose down -v && docker-compose up --build`

---

**Ready? Run `bash setup.sh` and get started!** 🚀
