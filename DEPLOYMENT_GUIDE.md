# Deployment Guide - Nissan Competitive Pricing Analyzer

This guide provides step-by-step instructions for deploying the Nissan Competitive Pricing Analyzer to free cloud hosting services.

## Table of Contents
1. [Replit Deployment (Recommended)](#replit-deployment-recommended)
2. [Render.com Deployment](#rendercom-deployment)
3. [Railway.app Deployment](#railwayapp-deployment)
4. [Local Development Setup](#local-development-setup)
5. [Post-Deployment Configuration](#post-deployment-configuration)

---

## Replit Deployment (Recommended)

Replit is the easiest and fastest way to deploy this application with zero configuration.

### Prerequisites
- GitHub account with this repository
- Replit account (free)

### Step-by-Step Instructions

#### 1. Push Code to GitHub
```bash
# If you haven't already, initialize git and push to GitHub
git add .
git commit -m "Initial commit - Nissan Pricing Analyzer"
git push origin main
```

#### 2. Create Replit Account
1. Go to https://replit.com
2. Click **"Sign up"**
3. Sign up with GitHub (recommended) or email

#### 3. Import from GitHub
1. Click **"Create Repl"** button
2. Select **"Import from GitHub"**
3. Paste your repository URL (e.g., `https://github.com/yourusername/aaipricing2`)
4. Click **"Import from GitHub"**
5. Wait for Replit to import and analyze your project

#### 4. Configure Secrets (Environment Variables)
1. In your Repl, look for the **"Tools"** icon in the left sidebar
2. Click on **"Secrets"** (looks like a lock icon)
3. Add the following secrets:

| Key | Value | Description |
|-----|-------|-------------|
| `FLASK_SECRET_KEY` | `your-random-secret-key-12345` | Any random string (change this!) |
| `VDP_LIMIT` | `3` | Number of VDPs to process per sitemap (testing mode) |
| `PORT` | `5000` | Port for the Flask server |

**To generate a secure secret key:**
```python
# Run this in Replit's Shell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 5. Run the Application
1. Click the **"Run"** button at the top
2. Replit will automatically:
   - Install Python dependencies from `requirements.txt`
   - Start the Flask server
   - Open a webview showing your application

#### 6. Access Your Application
1. Your app will be available at: `https://your-repl-name.your-username.repl.co`
2. Click **"Open in new tab"** to view in full browser
3. Bookmark this URL for easy access

#### 7. Test the Application
1. Enter test sitemap URLs (or use the examples in README.md)
2. Enter your OpenAI API key
3. Click "Run Analysis"
4. Verify the progress tracking works
5. Download the CSV report when complete

### Replit Tips
- **Always On**: Free tier keeps your app running
- **Auto-restart**: App automatically restarts if it crashes
- **Editing**: You can edit code directly in Replit and it will auto-reload
- **Logs**: Check the Console tab for error messages

---

## Render.com Deployment

Render is a good alternative with automatic deployments from GitHub.

### Prerequisites
- GitHub account with this repository
- Render.com account (free)

### Step-by-Step Instructions

#### 1. Create Render Account
1. Go to https://render.com
2. Click **"Get Started"**
3. Sign up with GitHub (recommended)

#### 2. Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already connected
3. Select your repository (`aaipricing2`)
4. Click **"Connect"**

#### 3. Configure Web Service
Fill in the following settings:

| Field | Value |
|-------|-------|
| **Name** | `nissan-pricing-analyzer` |
| **Region** | Choose closest to you |
| **Branch** | `main` (or your default branch) |
| **Root Directory** | (leave blank) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | `Free` |

#### 4. Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

| Key | Value |
|-----|-------|
| `FLASK_SECRET_KEY` | Your random secret key |
| `VDP_LIMIT` | `3` |
| `PORT` | `10000` (Render uses port 10000) |
| `PYTHON_VERSION` | `3.11.0` |

#### 5. Deploy
1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies
   - Build and deploy your app
3. Wait 5-10 minutes for first deployment

#### 6. Access Your Application
1. Your app will be available at: `https://nissan-pricing-analyzer.onrender.com`
2. Render provides a free SSL certificate automatically

### Render Tips
- **Auto-deploy**: Pushes to GitHub automatically trigger new deployments
- **Sleep Mode**: Free tier sleeps after 15 minutes of inactivity
- **Logs**: Check the "Logs" tab for debugging
- **Custom Domain**: Can add custom domain (free)

---

## Railway.app Deployment

Railway offers easy deployment with generous free tier.

### Prerequisites
- GitHub account with this repository
- Railway.app account (free)

### Step-by-Step Instructions

#### 1. Create Railway Account
1. Go to https://railway.app
2. Click **"Sign Up"**
3. Sign up with GitHub

#### 2. Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Select your repository (`aaipricing2`)
4. Railway will auto-detect it as a Python app

#### 3. Configure Environment Variables
1. Click on your service
2. Go to **"Variables"** tab
3. Click **"New Variable"**

Add these variables:

| Key | Value |
|-----|-------|
| `FLASK_SECRET_KEY` | Your random secret key |
| `VDP_LIMIT` | `3` |
| `PORT` | `5000` |

#### 4. Deploy
1. Railway automatically deploys on push
2. Wait for deployment to complete (check "Deployments" tab)

#### 5. Access Your Application
1. Go to **"Settings"** tab
2. Click **"Generate Domain"**
3. Your app will be available at the generated domain
4. Example: `https://aaipricing2.up.railway.app`

### Railway Tips
- **Free Tier**: $5 credit per month
- **Auto-deploy**: Automatic deployments from GitHub
- **Database**: Easy to add PostgreSQL if needed later
- **Logs**: Real-time logs in dashboard

---

## Local Development Setup

For testing and development on your local machine.

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git

### Step-by-Step Instructions

#### 1. Clone Repository
```bash
git clone <your-repo-url>
cd aaipricing2
```

#### 2. Create Virtual Environment (Recommended)
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your favorite editor
nano .env  # or vim, code, etc.
```

Edit `.env` and set:
```env
FLASK_SECRET_KEY=your-local-secret-key
VDP_LIMIT=3
PORT=5000
```

#### 5. Run Application
```bash
python app.py
```

#### 6. Access Application
Open your browser to:
```
http://localhost:5000
```

#### 7. Development Tips
- **Hot Reload**: Flask will auto-reload on code changes
- **Debugging**: Set `debug=True` in `app.py` for detailed errors
- **Testing**: Test with example VDPs from README.md

---

## Post-Deployment Configuration

### Testing Mode → Production Mode

By default, the app processes only 3 VDPs per sitemap for testing. To increase this:

#### Option 1: Change Environment Variable
1. Update `VDP_LIMIT` in your hosting platform:
   - **Replit**: Update in Secrets
   - **Render**: Update in Environment Variables
   - **Railway**: Update in Variables
2. Set to desired number (e.g., `10`, `50`, `100`, or `10000` for unlimited)
3. Restart the application

#### Option 2: Modify Code
Edit `app.py` line 18:
```python
# Change from:
VDP_LIMIT = int(os.getenv('VDP_LIMIT', 3))

# To:
VDP_LIMIT = int(os.getenv('VDP_LIMIT', 10000))  # High default
```

### Obtaining Sitemap URLs

To find competitor sitemap URLs:

1. **Common patterns**:
   - `https://www.example.com/sitemap.xml`
   - `https://www.example.com/sitemap_index.xml`
   - `https://www.example.com/sitemap/new-inventory.xml`

2. **Check robots.txt**:
   - Go to `https://www.example.com/robots.txt`
   - Look for `Sitemap:` directives

3. **Google Search**:
   - Search: `site:example.com sitemap.xml`

### Getting OpenAI API Key

1. Go to https://platform.openai.com
2. Sign up or log in
3. Navigate to **"API Keys"** (https://platform.openai.com/api-keys)
4. Click **"Create new secret key"**
5. Copy the key (starts with `sk-`)
6. Add billing information (required for usage)
7. **Important**: Keep this key secure and never share it

### Monitoring Usage

#### OpenAI API Costs
- Check usage at: https://platform.openai.com/usage
- Set usage limits at: https://platform.openai.com/account/billing/limits
- Estimated cost: $0.0001-0.0003 per VDP

#### Hosting Costs
- **Replit Free**: Unlimited (with ads)
- **Render Free**: 750 hours/month
- **Railway Free**: $5 credit/month

### Security Best Practices

1. **Never commit secrets**:
   - `.env` is in `.gitignore`
   - Use environment variables only

2. **Rotate keys regularly**:
   - Change `FLASK_SECRET_KEY` monthly
   - Rotate OpenAI API key if compromised

3. **Enable HTTPS**:
   - All cloud platforms provide free SSL
   - Never use HTTP in production

4. **Monitor logs**:
   - Check for unusual API usage
   - Watch for failed scraping attempts

---

## Troubleshooting

### Application won't start
1. Check all environment variables are set
2. Verify Python version is 3.11+
3. Check logs for error messages
4. Ensure all dependencies installed correctly

### Scraping fails
1. Verify sitemap URLs are accessible
2. Check if sites block scrapers (User-Agent)
3. Increase timeout in scraper.py if needed
4. Check internet connection

### OpenAI errors
1. Verify API key is valid
2. Check you have available credits
3. Ensure API key has GPT-4 access
4. Check OpenAI status page

### CSV download fails
1. Check exports/ directory exists and is writable
2. Verify job completed successfully
3. Check browser console for errors

---

## Next Steps

After successful deployment:

1. ✅ Test with example VDPs
2. ✅ Verify CSV export works
3. ✅ Test with real competitor sitemaps
4. ✅ Adjust VDP_LIMIT as needed
5. ✅ Set up monitoring (if using in production)
6. ✅ Share app URL with team
7. ✅ Document your specific sitemap URLs
8. ✅ Schedule regular analysis runs

---

## Support

If you encounter issues:
1. Check the main README.md troubleshooting section
2. Review application logs
3. Verify all environment variables are correct
4. Test with example VDPs first
5. Open an issue on GitHub with error details

---

**Happy Analyzing!** 🚗📊
