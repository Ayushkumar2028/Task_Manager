# Clean Render Deployment via Blueprint (Infrastructure as Code)
Deploying this entire full-stack application (both Django Backend and React Frontend) takes less than 2 minutes using **Render Blueprints**. 

I have generated a rigorous `render.yaml` specification right at the root of your project. This file automatically provisions a PostgreSQL database, mounts your Django Web Service, fires up your React Static website, sets up zero-downtime routing overrides, and seamlessly connects your application layers without you touching a single environment variable manually.

---

## 🚀 1-Click Deployment Guide

### Step 1: Push to GitHub
Commit and push your entire codebase (containing `backend/`, `frontend/`, and `render.yaml`) to your personal GitHub account.

### Step 2: Go to Render
1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. On the top right of the dashboard, click the **"New"** button and select **"Blueprint"**.

### Step 3: Deploy the Blueprint
1. Render will prompt you to connect a Git repository. Select the repository you pushed to in Step 1.
2. Render will instantly parse the `render.yaml` file natively.
3. Click the **"Apply"** button at the bottom of the screen.

### Step 4: Sit back and watch!
Render will now simultaneously:
- Provision a private `taskmanager-db` PostgreSQL instance.
- Build and spin up `taskmanager-backend` automatically populating its Database URLs and securely routing the API. It runs database migrations via `build.sh` before booting up.
- Compile and hook up your `taskmanager-frontend` static site, natively pulling the live backend URL into your React build and mapping React-Router overrides (`/*` -> `/index.html`) out of the box.

Important: this backend currently depends on `Django 6.x`, so the backend service must use Python `3.12+`. The included `render.yaml` sets `PYTHON_VERSION` accordingly.

Within 2 to 3 minutes, your unified production architecture will be 100% online and ready to accept users! 

*(Note: Log in utilizing the credentials `admin` / `Admin@123` right at your shiny new Frontend URL!)*
