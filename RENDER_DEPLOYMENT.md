# Render Deployment Guide for OpenPaw

## Quick Start - Single Service Deployment

Both Frontend and Backend run in the **same Render service**.

### 1. Push Code to GitHub
Make sure your repository is on GitHub (public or private):
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create Single Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `openpaw`
   - **Environment:** `Python 3`
   - **Region:** Oregon (or your preference)
   - **Plan:** Free (or Paid for better performance)
   - **Branch:** main
   - **Build Command:** `pip install -r requirements.txt && cd frontend && npm install && npm run build`
   - **Start Command:** `gunicorn --chdir backend app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`

5. **Add Environment Variables:**
   - `GROQ_API_KEY` = (get from https://console.groq.com/keys)
   - `CORS_ORIGINS` = `http://localhost:3000,http://localhost:4200,https://yourdomain.onrender.com`
   - `DEBUG` = `false`
   - `ENVIRONMENT` = `production`

6. Click **Create Web Service** and wait for deployment (~10-15 minutes)

### 3. Test Deployment

Once deployed, Render gives you a URL like: `https://openpaw-xxxxx.onrender.com`

- **Frontend:** Open https://openpaw-xxxxx.onrender.com
- **Backend API:** https://openpaw-xxxxx.onrender.com/api/chat
- **API Docs:** https://openpaw-xxxxx.onrender.com/api/docs
- **Health Check:** https://openpaw-xxxxx.onrender.com/api/health

---

## How It Works

The backend FastAPI server:
1. Serves API endpoints at `/api/*`
2. Serves built Angular frontend files as static content at `/`
3. Falls back to `index.html` for SPA routing

This is configured in `backend/app/main.py` using `SPAStaticFiles`.

---

## Environment Variables Reference

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `GROQ_API_KEY` | Yes | - | Get from https://console.groq.com/keys |
| `CORS_ORIGINS` | No | `["*"]` | Comma-separated URLs |
| `DEBUG` | No | `false` | Set to `false` in production |
| `ENVIRONMENT` | No | `development` | Set to `production` |
| `LLM_MODEL` | No | `llama-3.3-70b-versatile` | Groq model choice |
| `OAUTH_TOKEN_ENCRYPTION_KEY` | No | 32-char string | **CHANGE THIS** in production (min 32 chars) |

---

## Common Issues

### 1. **Frontend Shows Blank Page**
- Check browser console (F12) for errors
- Verify build completed: check Render logs for "npm run build"
- Clear browser cache (Ctrl+Shift+Delete)

### 2. **API Calls Return 404**
- Frontend is loading but can't reach `/api/*` endpoints
- Verify `GROQ_API_KEY` environment variable is set
- Check Render backend logs for errors

### 3. **Groq Rate Limit (429 Error)**
- Free tier limited to 100k tokens/day
- Solution: Wait until next day or upgrade at https://console.groq.com

### 4. **Build Fails: "Node not found"**
- Render needs Node.js for frontend build
- Add `NODE_VERSION=18` environment variable to Render service
- Or ensure `package.json` exists in repo root or `frontend/`

### 5. **Build Timeout**
- Free tier may timeout on large builds
- Solution: Upgrade to Paid plan or optimize dependencies

### 6. **Cold Start Delay**
- Free tier spins down after 15 min inactivity
- First request takes 30+ seconds
- Solution: Upgrade to Paid tier

---

## Upgrading to PostgreSQL

For production data persistence, use Render PostgreSQL:

### 1. Create PostgreSQL Database
- Render Dashboard → **New +** → **PostgreSQL**
- Follow setup wizard
- Copy internal connection string

### 2. Update Service Environment
Add:
```
DATABASE_URL=<your-postgres-connection-string>
```

### 3. Restart Service
Render auto-redeploys with new connection

---

## Monitoring & Logs

- **Logs:** Render Dashboard → Service → **Logs** tab
- **Build Output:** Check logs during deployment
- **Metrics:** Service → **Metrics** tab (Paid plans)
- **Manual Restart:** Service → **Settings** → **Restart**

---

## Cost Considerations

| Item | Free Tier | Paid Starting |
|------|-----------|---------------|
| Web Service | Yes (spins down) | $7/month |
| PostgreSQL | No | $15/month |

---

## Architecture

```
Browser
   ↓
[Render Web Service: openpaw]
   ├── GET / → Serves Angular frontend (dist/browser/index.html)
   ├── GET /api/* → FastAPI backend endpoints
   ├── Internal Database (SQLite or PostgreSQL)
   └── Groq LLM API (external)
```

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Create Web Service on Render
3. ✅ Add environment variables (especially GROQ_API_KEY)
4. ✅ Wait for build (~15 min)
5. ✅ Test frontend loads
6. ✅ Test API endpoints work
7. 📈 Monitor logs for errors

For questions: https://render.com/docs
