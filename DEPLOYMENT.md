# 🚀 OmniGrab 24/7 Cloud Deployment Guide

OmniGrab is packaged and pre-configured for **1-click cloud deployment** on free and affordable hosting platforms.

---

## Option 1: Render.com (Recommended Free Hosting)

Render provides free hosting with automatic Docker builds straight from GitHub.

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for OmniGrab"
   # Create a repository on github.com and link it:
   git remote add origin https://github.com/<your-username>/omnigrab.git
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com/).
   - Click **New +** -> **Web Service**.
   - Select your GitHub repository.
   - Render will detect the `render.yaml` and `Dockerfile` automatically!
   - Instance Type: **Free**.
   - Click **Create Web Service**.

Your site will be live at `https://omnigrab-xxxx.onrender.com` with free automated SSL.

---

## Option 2: Railway.app

1. Go to [railway.app](https://railway.app/).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select this repo — Railway will read `railway.json` and build the `Dockerfile` automatically.
4. Click **Generate Domain** under Settings.

---

## Option 3: Hugging Face Spaces (Docker Free Tier)

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and create a **New Space**.
2. Select **Docker** (Blank).
3. Push this project code to the Space's Git repository.
4. OmniGrab will run permanently with unlimited free uptime.
