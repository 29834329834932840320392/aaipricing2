# Nissan Competitive Pricing Analyzer

A cloud-hosted web application that automates competitive pricing analysis for Nissan dealerships. This tool scrapes competitor websites, uses AI to extract pricing data, and generates comprehensive CSV reports.

## Features

- **Automated Sitemap Parsing**: Extracts new Nissan vehicle VDP URLs from competitor XML sitemaps
- **Intelligent Data Extraction**: Uses OpenAI GPT-4 to intelligently extract vehicle data regardless of website structure
- **Real-time Progress Tracking**: Monitor analysis progress with live updates
- **CSV Export**: Download comprehensive pricing reports
- **Error Handling**: Robust error handling with detailed error logs
- **Testing Mode**: Process limited VDPs for testing (configurable)

## Data Extracted

For each vehicle, the tool extracts:
- Competitor Name
- VDP URL
- VIN (Vehicle Identification Number)
- Year
- Make (Nissan)
- Model (Altima, Rogue, Sentra, etc.)
- Trim (SV, SL, Platinum, etc.)
- MSRP
- Sale Price (final customer price after all discounts)
- Date Scraped

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Local Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd aaipricing2
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and set your FLASK_SECRET_KEY
```

4. **Run the application**
```bash
python app.py
```

5. **Open your browser**
```
http://localhost:5000
```

## Deployment to Replit (Recommended for Free Hosting)

### Step 1: Create a Replit Account
1. Go to [Replit.com](https://replit.com)
2. Sign up for a free account

### Step 2: Import Project
1. Click **"Create Repl"**
2. Select **"Import from GitHub"**
3. Paste your GitHub repository URL
4. Click **"Import from GitHub"**

### Step 3: Configure Environment Variables
1. In your Repl, click on **"Secrets"** (lock icon in the left sidebar)
2. Add the following secrets:
   - Key: `FLASK_SECRET_KEY`, Value: `your-random-secret-key-here`
   - Key: `VDP_LIMIT`, Value: `3` (for testing)
   - Key: `PORT`, Value: `5000`

### Step 4: Run the Application
1. Click the **"Run"** button
2. Replit will automatically install dependencies and start the server
3. Your app will be available at the URL shown in the webview (e.g., `https://your-repl-name.your-username.repl.co`)

### Step 5: Access Your Application
1. Click the URL in the webview or click **"Open in new tab"**
2. You should see the Nissan Competitive Pricing Analyzer interface

## Deployment to Other Free Hosting Services

### Render.com

1. Create a free account at [Render.com](https://render.com)
2. Click **"New +" → "Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: nissan-pricing-analyzer
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add environment variables in the "Environment" section
6. Click **"Create Web Service"**

### Railway.app

1. Create a free account at [Railway.app](https://railway.app)
2. Click **"New Project" → "Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect Python and deploy
5. Add environment variables in the "Variables" tab
6. Your app will be available at the provided URL

## Configuration

### Testing Mode (Default)

By default, the application processes only **3 VDPs per sitemap** for testing purposes. This is controlled by the `VDP_LIMIT` environment variable.

**To change the limit:**

1. **In .env file** (for local development):
```env
VDP_LIMIT=3  # Change to desired number or remove for unlimited
```

2. **In Replit Secrets** (for Replit deployment):
   - Edit the `VDP_LIMIT` secret
   - Change value to desired number (e.g., `10`, `50`, `100`)
   - Or remove it entirely for unlimited processing

3. **Restart the application** after making changes

### Production Mode (Unlimited VDPs)

To process all VDPs without limit:

1. Set `VDP_LIMIT` to a very high number (e.g., `10000`) or
2. Modify `app.py` line 18 to:
```python
VDP_LIMIT = int(os.getenv('VDP_LIMIT', 10000))  # High default
```

## Usage

1. **Navigate to the application URL**

2. **Enter Competitor Sitemap URLs**
   - At least one sitemap URL is required
   - Example sitemaps:
     - Gunn Nissan: `https://www.gunnnissan.com/sitemap.xml`
     - Ingram Park: `https://www.ingramparknissan.com/sitemap.xml`
     - Nissan of Boerne: `https://www.nissanboerne.com/sitemap.xml`
     - Champion Nissan: `https://www.championnissannb.com/sitemap.xml`

3. **Enter OpenAI API Key**
   - Your API key is used only for this session
   - It is never stored on disk
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

4. **Click "Run Analysis"**
   - The application will start processing
   - Real-time progress will be displayed
   - Errors (if any) will be shown in the errors section

5. **Download CSV Report**
   - When complete, click "Download CSV Report"
   - The CSV contains all extracted vehicle data

6. **Run New Analysis**
   - Click "New Analysis" to start over

## Example VDPs (for Testing)

Use these VDP URLs to test the scraper with different website structures:

- **Gunn Nissan**: https://www.gunnnissan.com/new-San+Antonio-2025-Nissan-Sentra-SV-3N1AB8CV2SY404093
- **Ingram Park**: https://www.ingramparknissan.com/inventory/new-2025-nissan-rogue-sv-fwd-4d-sport-utility-5n1bt3ba1sc851633/
- **Nissan of Boerne**: https://www.nissanboerne.com/viewdetails/new/5n1dr3ba5sc293857/2025-nissan-pathfinder-sport-utility
- **Champion Nissan NB**: https://www.championnissannb.com/auto/new-2025-nissan-murano-sl-new-braunfels-tx/111738776/

## Project Structure

```
aaipricing2/
├── app.py                 # Main Flask application
├── scraper.py            # Web scraping and sitemap parsing logic
├── ai_extractor.py       # OpenAI integration for data extraction
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in git)
├── .env.example          # Environment variables template
├── .replit               # Replit configuration
├── .gitignore           # Git ignore file
├── templates/
│   └── index.html       # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css    # Styles
│   └── js/
│       └── main.js      # Frontend JavaScript
├── exports/             # CSV exports (auto-created)
└── README.md            # This file
```

## API Endpoints

### `GET /`
Renders the main application interface

### `POST /api/start-analysis`
Starts a new pricing analysis job

**Request Body:**
```json
{
  "gunn_nissan_url": "https://...",
  "ingram_park_url": "https://...",
  "boerne_url": "https://...",
  "champion_nb_url": "https://...",
  "openai_api_key": "sk-..."
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "message": "Analysis started successfully"
}
```

### `GET /api/job-status/<job_id>`
Gets the current status of an analysis job

**Response:**
```json
{
  "job_id": "uuid",
  "status": "running",
  "progress": {
    "current_competitor": "Gunn Nissan",
    "total_competitors": 4,
    "completed_competitors": 1,
    "current_vdp": 2,
    "total_vdps": 3,
    "processed_vdps": 5
  },
  "completed": false,
  "total_results": 5,
  "total_errors": 0,
  "errors": []
}
```

### `GET /api/download-csv/<job_id>`
Downloads the CSV report for a completed job

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "vdp_limit": 3
}
```

## Troubleshooting

### Issue: "Failed to parse sitemap"
- **Solution**: Verify the sitemap URL is correct and accessible
- Try opening the sitemap URL in your browser to confirm it's valid XML

### Issue: "AI extraction error"
- **Solution**: Verify your OpenAI API key is valid and has available credits
- Check that your API key has access to GPT-4 models

### Issue: "No VDPs found"
- **Solution**: The sitemap may not contain new Nissan vehicle URLs
- Try using a different sitemap or verify the sitemap contains new inventory

### Issue: Application not loading on Replit
- **Solution**: Check that all environment variables are set in Replit Secrets
- Click "Run" again to restart the application
- Check the console for error messages

## Cost Considerations

### OpenAI API Costs
- The application uses GPT-4o-mini for cost efficiency
- Approximate cost: $0.0001-0.0003 per VDP processed
- For 12 VDPs (4 competitors × 3 VDPs): ~$0.001-0.004
- For 400 VDPs (production): ~$0.04-0.12

### Free Hosting Limits
- **Replit Free Tier**: Always-on, unlimited projects, 1GB RAM
- **Render Free Tier**: 750 hours/month, sleeps after 15 min inactivity
- **Railway Free Tier**: $5 credit/month, pay-as-you-go after

## Security Notes

- OpenAI API keys are stored only in session memory
- Never commit `.env` file to version control
- Use strong `FLASK_SECRET_KEY` in production
- HTTPS is automatically enabled on Replit/Render/Railway

## Future Enhancements

- [ ] Database storage for historical pricing data
- [ ] Price trend analysis and alerts
- [ ] Email reports
- [ ] Multi-region support
- [ ] Scheduled automated runs
- [ ] Price comparison charts and visualizations

## License

MIT License - feel free to modify and use for your dealership needs!

## Support

For issues or questions, please open an issue on GitHub or contact your development team.

---

**Built with**: Flask, OpenAI GPT-4, BeautifulSoup, and deployed on free cloud hosting.
