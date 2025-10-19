# 🚀 Frontend Deployment Guide

This guide covers deploying the FinSage AI frontend to popular platforms.

## 📋 Prerequisites

1. GitHub repository with your code pushed
2. Account on deployment platform (Vercel/Netlify/etc.)
3. Backend API deployed and accessible (optional for initial deployment)

---

## 🎯 Option 1: Deploy to Vercel (Recommended)

### Why Vercel?
- ✅ Built specifically for React/Vite apps
- ✅ Automatic deployments from GitHub
- ✅ Free SSL certificates
- ✅ Global CDN
- ✅ Zero configuration needed

### Steps:

#### 1. Install Vercel CLI (Optional)
```bash
npm install -g vercel
```

#### 2. Deploy via Web Interface (Easiest)

1. Go to [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Connect your GitHub account
4. Select `FinSage-AI` repository
5. Configure project:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
6. Add Environment Variable:
   - **Name:** `VITE_API_URL`
   - **Value:** `http://localhost:8000` (update after backend deployment)
7. Click "Deploy"

#### 3. Deploy via CLI
```bash
cd frontend
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name? finsage-ai-frontend
# - Which directory? ./
# - Override build settings? No
```

#### 4. Set Environment Variables
```bash
vercel env add VITE_API_URL

# Enter value when prompted:
# Production: https://your-backend-url.com
```

#### 5. Redeploy with Environment Variables
```bash
vercel --prod
```

### Your app will be live at:
```
https://finsage-ai-frontend.vercel.app
```

---

## 🎯 Option 2: Deploy to Netlify

### Steps:

1. Go to [netlify.com](https://netlify.com)
2. Click "Add new site" → "Import an existing project"
3. Connect to GitHub
4. Select `FinSage-AI` repository
5. Configure:
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `frontend/dist`
6. Add Environment Variable:
   - Go to Site settings → Environment variables
   - Add `VITE_API_URL` with backend URL
7. Click "Deploy site"

### Using Netlify CLI:
```bash
npm install -g netlify-cli
cd frontend
netlify init
netlify deploy --prod
```

---

## 🎯 Option 3: Deploy to GitHub Pages

### Steps:

1. Install gh-pages package:
```bash
cd frontend
npm install --save-dev gh-pages
```

2. Update `package.json`:
```json
{
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d dist"
  },
  "homepage": "https://Aditya-Prakash14.github.io/FinSage-AI"
}
```

3. Update `vite.config.js`:
```javascript
export default defineConfig({
  base: '/FinSage-AI/',
  // ... rest of config
})
```

4. Deploy:
```bash
npm run deploy
```

---

## 🎯 Option 4: Deploy to Render

1. Go to [render.com](https://render.com)
2. Click "New" → "Static Site"
3. Connect GitHub repository
4. Configure:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Publish Directory:** `frontend/dist`
5. Add environment variable `VITE_API_URL`
6. Click "Create Static Site"

---

## 🔧 Build Locally First (Testing)

Before deploying, test the production build locally:

```bash
cd frontend

# Build for production
npm run build

# Preview the build
npm run preview
```

This will:
1. Create optimized production bundle in `dist/`
2. Start preview server at `http://localhost:4173`

### Check build output:
```bash
ls -lh dist/

# Should see:
# - index.html
# - assets/ (CSS, JS chunks)
# - vite.svg
```

---

## 🌐 Environment Variables

### Development (`.env.development`)
```env
VITE_API_URL=http://localhost:8000
```

### Production (`.env.production`)
```env
VITE_API_URL=https://your-backend-url.com
```

### Set on Deployment Platform:
- **Vercel:** Project Settings → Environment Variables
- **Netlify:** Site Settings → Environment Variables
- **Render:** Environment tab

---

## 🔒 CORS Configuration (Backend)

After deploying frontend, update backend CORS to allow your domain:

In `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://finsage-ai-frontend.vercel.app",  # Add your Vercel domain
        "https://yourdomain.com",  # Add custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Post-Deployment Checklist

- [ ] Frontend accessible at deployed URL
- [ ] Dark mode toggle works
- [ ] Landing page loads correctly
- [ ] Dashboard navigation functional
- [ ] Sample data generation works
- [ ] Charts render properly
- [ ] Responsive on mobile devices
- [ ] SSL certificate active (https://)
- [ ] Custom domain configured (optional)
- [ ] Backend API connected (if deployed)

---

## 🐛 Troubleshooting

### Build fails with "command not found"
```bash
# Ensure you're in frontend directory
cd frontend
npm install
npm run build
```

### API calls fail (404/CORS)
1. Check `VITE_API_URL` environment variable
2. Update backend CORS to allow frontend domain
3. Ensure backend is deployed and accessible

### Blank page after deployment
1. Check browser console for errors
2. Verify `dist/` directory was deployed
3. Check routing configuration (vercel.json/netlify.toml)

### Environment variables not working
1. Ensure variables start with `VITE_`
2. Rebuild after adding environment variables
3. Clear cache and redeploy

---

## 🎨 Custom Domain (Optional)

### Vercel:
1. Go to Project Settings → Domains
2. Add your domain
3. Update DNS records as instructed

### Netlify:
1. Go to Site Settings → Domain Management
2. Add custom domain
3. Configure DNS

---

## 🚀 Continuous Deployment

Both Vercel and Netlify automatically deploy when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "feat: Add new feature"
git push origin main

# Deployment triggers automatically!
```

---

## 📈 Performance Optimization

### Already Implemented:
- ✅ Vite code splitting
- ✅ Tree shaking
- ✅ Asset optimization
- ✅ Lazy loading routes

### Additional (Optional):
```bash
# Analyze bundle size
npm run build -- --mode analyze

# PWA support
npm install vite-plugin-pwa
```

---

## 🔗 Useful Links

- **Vercel Docs:** https://vercel.com/docs
- **Netlify Docs:** https://docs.netlify.com
- **Vite Production:** https://vitejs.dev/guide/build.html
- **GitHub Pages:** https://pages.github.com

---

## 💡 Recommended: Vercel + Railway

**Frontend (Vercel):** Free, fast, auto-deploy from GitHub
**Backend (Railway):** $5/month, easy Python deployment, PostgreSQL included

This combination gives you:
- Production-ready infrastructure
- Automatic SSL
- Global CDN
- CI/CD pipeline
- Easy scaling

---

## ✅ Quick Deploy (5 minutes)

```bash
# 1. Build and test locally
cd frontend
npm run build
npm run preview

# 2. Commit and push
git add .
git commit -m "chore: Prepare for deployment"
git push origin main

# 3. Deploy to Vercel
vercel --prod

# Done! 🎉
```
