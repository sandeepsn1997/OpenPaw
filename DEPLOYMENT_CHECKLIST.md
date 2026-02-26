# OpenPaw Render Deployment Checklist

## ✅ Code Changes Made

### New Files Created
- ✅ `render.yaml` - Single web service configuration for Render
- ✅ `Procfile` - Backup deployment configuration  
- ✅ `.env.example` - Environment variables template
- ✅ `RENDER_DEPLOYMENT.md` - Complete deployment guide with troubleshooting

### Files Updated
- ✅ `requirements.txt` - Added `gunicorn` for production deployment
- ✅ `backend/app/config.py` - Added `environment` setting for production awareness

### Configuration Ready
- ✅ `backend/app/main.py` - Serves both API and frontend static files
- ✅ `frontend/package.json` - Build script ready
- ✅ `.gitignore` - `.env` already protected
- ✅ `frontend/proxy.conf.json` - Ready for local development

---

## 📋 Single Service Deployment in Render Portal

### Step 1: Prepare GitHub Repository
```bash
cd d:\Projects\OpenPaw
git add .
git commit -m "Prepare for Render deployment (single service)"
git push origin main
```

### Step 2: Create Web Service on Render
1. Go to https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Connect GitHub repo (select `OpenPaw`)
4. Configure:
   - **Name:** `openpaw`
   - **Environment:** Python 3
   - **Region:** Oregon (or your preference)
   - **Plan:** Free (recommended for testing)
   - **Branch:** main
   - **Build Command:** `pip install -r requirements.txt && cd frontend && npm install && npm run build`
   - **Start Command:** `gunicorn --chdir backend app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`

5. Add Environment Variables:
   ```
   GROQ_API_KEY = [your-groq-api-key]
   CORS_ORIGINS = http://localhost:3000,http://localhost:4200,https://yourdomain.onrender.com
   DEBUG = false
   ENVIRONMENT = production
   NODE_VERSION = 18
   ```

6. Click **Create Web Service**
7. Wait for build to complete (~15 minutes)
   - Python dependencies install
   - Frontend builds with `npm run build`
   - Backend starts with gunicorn

---

## 🧪 Testing After Deployment

Once deployed, Render provides a URL like: `https://openpaw-xxxxx.onrender.com`

### Access the Service
- **Frontend:** https://openpaw-xxxxx.onrender.com
- **API Docs:** https://openpaw-xxxxx.onrender.com/api/docs
- **Health Check:** https://openpaw-xxxxx.onrender.com/api/health

### Test in Browser
1. Open frontend URL
2. Should see OpenPaw chat interface
3. Test echo: Type "Echo hello" in chat
4. Should see "hello" as response

---

## ⚙️ Important Environment Variables

| Variable | Required | Value |
|----------|----------|-------|
| `GROQ_API_KEY` | Yes | From https://console.groq.com/keys |
| `NODE_VERSION` | Yes | `18` (for frontend build) |
| `CORS_ORIGINS` | No | Your domain URL |
| `DEBUG` | No | `false` |
| `ENVIRONMENT` | No | `production` |

---

## 🆘 Troubleshooting

### Build Fails: "Node not found"
- **Fix:** Add `NODE_VERSION = 18` to Environment Variables

### Build Timeout (~30 minutes)
- **Cause:** Free tier build limit
- **Fix:** Optimize dependencies or upgrade to Paid plan

### Frontend Shows Blank Page
- Clear browser cache (Ctrl+Shift+Delete)
- Check browser console (F12) for errors
- Check Render logs for build/runtime errors

### API Returns 404
- Verify `GROQ_API_KEY` is set
- Check backend logs for startup errors
- Ensure build step included frontend build

### API calls fail with 429 (Rate Limited)
- Groq free tier: 100k tokens/day
- Solution: Wait until next day or upgrade Groq tier

### Cold Start Delay (30+ seconds)
- Free tier Render spins down after 15 min inactivity
- First request wakes it up (slow)
- Solution: Upgrade to Paid tier

---

## 📚 Deployment Architecture

```
Browser
   ↓
Render Web Service: openpaw
├── GET / → Serves Angular SPA (frontend)
├── GET /api/* → FastAPI backend
├── SQLite Database (or PostgreSQL)
└── Calls to Groq LLM API
```

---

## 📚 Additional Resources

- **Render Docs:** https://render.com/docs
- **Groq Console:** https://console.groq.com
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/concepts/
- **Angular Build:** https://angular.io/guide/build

---

## 🎉 Success Indicators

✅ Build completes without errors
✅ Service starts and shows "Running"
✅ Can access frontend at service URL
✅ Frontend displays without blank page
✅ Echo commands work without errors
✅ API docs accessible at `/api/docs`
✅ No 404 or CORS errors in browser console

Once all checks pass, your OpenPaw system is live on Render! 🚀
