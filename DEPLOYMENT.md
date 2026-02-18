# Deploying Clinical Study to Railway

Your app is ready to deploy. Follow these steps:

---

## Prerequisites

1. **GitHub account** – Railway deploys from GitHub
2. **Railway account** – Sign up at [railway.app](https://railway.app) (free to start)

---

## Step 1: Push your code to GitHub

If you haven't already, initialize git and push to GitHub:

```bash
cd "/Users/dishagupta/Library/Mobile Documents/com~apple~CloudDocs/ClinicalStudy"

# Initialize git (skip if already a repo)
git init

# Add all files (gitignore excludes venv, uploads, .db)
git add .

# Commit
git commit -m "Ready for deployment"

# Create a repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/clinical-study.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Choose **"Deploy from GitHub repo"**
4. Select your `clinical-study` repository (or connect GitHub if needed)
5. Railway will auto-detect the Python app and deploy
6. Once deployed, click **"Generate Domain"** to get a public URL (e.g. `your-app.up.railway.app`)

---

## Step 3: Add persistent storage (important)

Without this, your database and uploaded images will be lost on every redeploy.

1. In your Railway project, click your service
2. Go to the **"Variables"** tab
3. Click **"+ New Variable"**
4. Add: `DATA_DIR` = `/data`
5. Go to the **"Settings"** tab
6. Under **"Volumes"**, click **"+ Add Volume"**
7. Mount path: `/data`
8. Redeploy the service (Railway will do this automatically when you add the volume)

---

## Done

Your app will be live at the URL Railway provides. Open it in your browser and start uploading ultrasound images.

---

## Alternative: Deploy to Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Click **"Create Web Service"**
6. For persistent data: Upgrade to a paid plan and add a **Persistent Disk** (mount at `/data`), then set `DATA_DIR=/data`

---

## Troubleshooting

- **App won't start:** Check the logs in Railway/Render dashboard
- **Uploads or data lost:** Make sure you added the volume and `DATA_DIR` (Step 3)
- **AI API errors:** The external AI API must be reachable from the server (it should work by default)
