# 🚀 Deploy FinSage AI Backend to Render

## Prerequisites
- GitHub account with FinSage-AI repository
- Render account (sign up at https://render.com)
- TiDB Cloud database credentials
- OpenAI API key

## Step-by-Step Deployment Guide

### 1. Prepare Your Repository

Make sure all changes are committed and pushed to GitHub:

```bash
cd /Users/adityaprakash/Desktop/DESKTOP-MAIN/FinSage-AI
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Sign Up / Login to Render

1. Go to https://render.com
2. Click "Get Started" or "Sign In"
3. Connect your GitHub account

### 3. Create New Web Service

1. Click **"New +"** button in the top right
2. Select **"Web Service"**
3. Choose **"Build and deploy from a Git repository"**
4. Click **"Connect account"** if needed, then find **FinSage-AI** repository
5. Click **"Connect"**

### 4. Configure Service

**Basic Settings:**
- **Name:** `finsage-api` (or your preferred name)
- **Region:** Oregon (US West) - closest to TiDB Cloud AP-Northeast
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** `Python 3`
- **Build Command:** 
  ```
  pip install --upgrade pip && pip install -r requirements.txt
  ```
- **Start Command:**
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
  ```

**Plan:**
- Select **"Free"** plan (sufficient for testing)

### 5. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** for each:

#### Required Variables:

```bash
# Database Configuration
MYSQL_HOST=gateway01.ap-northeast-1.prod.aws.tidbcloud.com
MYSQL_PORT=4000
MYSQL_USER=EnDcAwr1qtnJ21c.root
MYSQL_PASSWORD=hgLVw7PhbDCP8nxN
MYSQL_DATABASE=test

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# JWT Security (Render can auto-generate)
JWT_SECRET_KEY=generate_with_openssl_rand_hex_32_or_let_render_generate
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (update after frontend deployed)
CORS_ORIGINS=*

# Application Settings
ENV=production
DEBUG=false
LOG_LEVEL=info
```

**Important:** 
- For `JWT_SECRET_KEY`, click "Generate" button in Render to create a secure random key
- Update `CORS_ORIGINS` after deploying your frontend (e.g., `https://your-frontend.vercel.app`)

### 6. Deploy

1. Review all settings
2. Click **"Create Web Service"** button
3. Render will start building your application

**Build Process (takes 5-10 minutes):**
- Installing Python dependencies
- Setting up environment
- Starting uvicorn server

### 7. Monitor Deployment

Watch the **Logs** tab for:
```
✅ MySQL database connected successfully
✅ Database tables created/verified (MySQL)
✅ Database ready
INFO:     Application startup complete.
```

### 8. Get Your API URL

Once deployed, your API will be available at:
```
https://finsage-api.onrender.com
```

Test it:
```bash
curl https://finsage-api.onrender.com/api/finance/health
```

### 9. Update Frontend

Update your frontend `.env` file:
```bash
VITE_API_URL=https://finsage-api.onrender.com
```

### 10. Test API Endpoints

Visit the API documentation:
```
https://finsage-api.onrender.com/docs
```

## Common Issues & Solutions

### Issue 1: Build Timeout (>15 minutes)

**Problem:** Prophet and PyTorch take too long to install on free tier

**Solution 1 - Use lighter requirements:**
Create `backend/requirements-render.txt` without heavy ML packages:
```bash
fastapi==0.119.0
uvicorn==0.38.0
pydantic==2.12.3
python-dotenv==1.1.1
PyJWT==2.8.0
SQLAlchemy==2.0.23
mysql-connector-python==8.2.0
PyMySQL==1.1.0
openai>=1.0.0
langchain>=0.1.0
langchain-core>=0.1.0
langchain-openai>=0.1.0
langgraph>=0.2.0
python-dateutil==2.9.0.post0
requests==2.32.5
```

Then update build command:
```
pip install --upgrade pip && pip install -r requirements-render.txt
```

**Solution 2 - Upgrade to paid plan** ($7/month for more build time)

### Issue 2: Database Connection Fails

**Check:**
- MySQL credentials are correct
- TiDB Cloud database is running
- SSL settings in `mysql_config.py` are configured

### Issue 3: Service Sleeps (Free Tier)

**Note:** Free tier services sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- Upgrade to paid plan for 24/7 uptime

### Issue 4: Import Errors

**Check logs for:**
```
ModuleNotFoundError: No module named 'xyz'
```

**Fix:** Add missing package to requirements.txt

### Issue 5: CORS Errors from Frontend

**Update CORS_ORIGINS:**
1. Go to Render Dashboard → finsage-api
2. Click "Environment"
3. Update `CORS_ORIGINS` to your frontend URL:
   ```
   https://your-frontend.vercel.app,https://finsage-ai.vercel.app
   ```
4. Click "Save Changes" (triggers redeploy)

## Performance Optimization

### For Production Use:

1. **Upgrade to Starter Plan ($7/month):**
   - More RAM and CPU
   - No sleep
   - Faster builds

2. **Enable Auto-Deploy:**
   - Already configured in render.yaml
   - Automatic deploys on git push

3. **Add Health Checks:**
   - Already configured: `/api/finance/health`
   - Render will restart if unhealthy

4. **Monitor Logs:**
   - Check logs regularly for errors
   - Set up email alerts in Render

## Security Checklist

- [ ] JWT_SECRET_KEY is auto-generated (not hardcoded)
- [ ] OPENAI_API_KEY is not exposed in logs
- [ ] MYSQL_PASSWORD is stored securely
- [ ] CORS is restricted to your frontend domain
- [ ] DEBUG is set to false
- [ ] HTTPS is enabled (automatic on Render)

## Post-Deployment

### Test All Endpoints:

```bash
# Health check
curl https://finsage-api.onrender.com/api/finance/health

# Register user
curl -X POST https://finsage-api.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'

# Create transaction (after getting token)
curl -X POST https://finsage-api.onrender.com/api/finance/transactions \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo_user_001","amount":5000,"type":"income","category":"Salary","description":"Test"}'
```

### Update Frontend:

1. Deploy frontend on Vercel with updated API URL
2. Test complete user flow:
   - Registration
   - Login
   - Transaction upload
   - Dashboard features

### Monitor Performance:

- Check Render metrics dashboard
- Monitor response times
- Watch for errors in logs

## Estimated Costs

### Free Tier:
- **Cost:** $0
- **Limitations:** 
  - 750 hours/month
  - Sleeps after 15 min inactivity
  - Slower build times
  - Limited resources

### Starter Plan:
- **Cost:** $7/month
- **Benefits:**
  - Always on (no sleep)
  - 2x faster builds
  - More RAM/CPU
  - Email support

## Alternative: Use Render Blueprint

If you prefer automated setup, Render can read the `render.yaml` file:

1. Go to Render Dashboard
2. Click "Blueprints" → "New Blueprint Instance"
3. Select FinSage-AI repository
4. Render will auto-detect `backend/render.yaml`
5. Add environment variables
6. Click "Apply"

## Support

If you encounter issues:

1. **Check Logs:** Render Dashboard → Logs tab
2. **Render Docs:** https://render.com/docs
3. **Community:** Render Community Forum
4. **Support:** support@render.com (paid plans)

## Success Indicators

✅ Build completes without errors  
✅ Service status shows "Live"  
✅ Health endpoint returns 200  
✅ API docs accessible at /docs  
✅ Database connection successful  
✅ No errors in logs  

## Next Steps

After backend is live:
1. Deploy frontend on Vercel
2. Update CORS settings
3. Test end-to-end flow
4. Set up monitoring
5. Configure custom domain (optional)

---

**Your backend will be live at:**
```
https://finsage-api.onrender.com
```

**API Documentation:**
```
https://finsage-api.onrender.com/docs
```

Good luck with your deployment! 🚀
