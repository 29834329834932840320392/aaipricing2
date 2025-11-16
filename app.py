"""
Flask application for Nissan competitive pricing analysis
"""
from flask import Flask, render_template, request, jsonify, send_file, session
import os
from dotenv import load_dotenv
from scraper import VehicleScraper
from ai_extractor import AIVehicleExtractor
import csv
from datetime import datetime
import threading
import time
from typing import Dict, List
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
VDP_LIMIT = int(os.getenv('VDP_LIMIT', 3))  # Default to 3 for testing

# Global storage for analysis results (in production, use Redis or database)
analysis_results = {}


class AnalysisJob:
    """Class to track analysis job progress"""

    def __init__(self, job_id: str, sitemap_urls: List[str], openai_api_key: str):
        self.job_id = job_id
        self.sitemap_urls = sitemap_urls
        self.openai_api_key = openai_api_key
        self.status = 'starting'
        self.progress = {
            'current_competitor': '',
            'total_competitors': len(sitemap_urls),
            'completed_competitors': 0,
            'current_vdp': 0,
            'total_vdps': 0,
            'processed_vdps': 0
        }
        self.results = []
        self.errors = []
        self.completed = False
        self.csv_path = None

    def update_progress(self, **kwargs):
        """Update progress information"""
        self.progress.update(kwargs)

    def add_result(self, result: Dict):
        """Add a result to the results list"""
        self.results.append(result)

    def add_error(self, error: str):
        """Add an error to the errors list"""
        self.errors.append(error)


def run_analysis(job: AnalysisJob):
    """Run the competitive analysis (runs in background thread)"""
    try:
        job.status = 'running'

        # Initialize scraper and AI extractor
        scraper = VehicleScraper(vdp_limit=VDP_LIMIT)
        ai_extractor = AIVehicleExtractor(api_key=job.openai_api_key)

        # Process each sitemap
        for idx, sitemap_url in enumerate(job.sitemap_urls, 1):
            try:
                # Update progress
                competitor_name = scraper.extract_competitor_name(sitemap_url)
                job.update_progress(
                    current_competitor=competitor_name,
                    completed_competitors=idx - 1,
                    current_vdp=0,
                    total_vdps=0
                )

                # Parse sitemap
                job.status = f'Parsing sitemap for {competitor_name}'
                vdp_urls = scraper.parse_sitemap(sitemap_url)

                job.update_progress(total_vdps=len(vdp_urls))

                # Process each VDP
                for vdp_idx, vdp_url in enumerate(vdp_urls, 1):
                    try:
                        job.update_progress(current_vdp=vdp_idx)
                        job.status = f'Processing {competitor_name} - VDP {vdp_idx}/{len(vdp_urls)}'

                        # Scrape VDP
                        vdp_data = scraper.scrape_vdp(vdp_url)

                        # Extract vehicle data using AI
                        vehicle_data = ai_extractor.extract_vehicle_data(
                            html_content=vdp_data['html_content'],
                            url=vdp_data['url'],
                            page_title=vdp_data.get('page_title', '')
                        )

                        # Combine data
                        result = {
                            'competitor': vdp_data['competitor'],
                            'url': vdp_data['url'],
                            'vin': vehicle_data['vin'],
                            'year': vehicle_data['year'],
                            'make': vehicle_data['make'],
                            'model': vehicle_data['model'],
                            'trim': vehicle_data['trim'],
                            'msrp': vehicle_data['msrp'],
                            'sale_price': vehicle_data['sale_price'],
                            'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }

                        job.add_result(result)
                        job.update_progress(processed_vdps=job.progress['processed_vdps'] + 1)

                        # Small delay to avoid overwhelming servers
                        time.sleep(1)

                    except Exception as e:
                        error_msg = f"Error processing {vdp_url}: {str(e)}"
                        job.add_error(error_msg)
                        print(error_msg)

                job.update_progress(completed_competitors=idx)

            except Exception as e:
                error_msg = f"Error processing sitemap {sitemap_url}: {str(e)}"
                job.add_error(error_msg)
                print(error_msg)

        # Generate CSV
        job.status = 'Generating CSV'
        csv_path = generate_csv(job.job_id, job.results)
        job.csv_path = csv_path

        # Mark as completed
        job.status = 'completed'
        job.completed = True

    except Exception as e:
        job.status = f'error: {str(e)}'
        job.add_error(f"Critical error: {str(e)}")
        print(f"Critical error in analysis: {e}")


def generate_csv(job_id: str, results: List[Dict]) -> str:
    """Generate CSV file from results"""
    os.makedirs('exports', exist_ok=True)
    csv_path = f'exports/{job_id}.csv'

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        if results:
            fieldnames = ['competitor', 'url', 'vin', 'year', 'make', 'model', 'trim', 'msrp', 'sale_price', 'date_scraped']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    return csv_path


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html', vdp_limit=VDP_LIMIT)


@app.route('/api/start-analysis', methods=['POST'])
def start_analysis():
    """Start a new analysis job"""
    data = request.json

    # Validate inputs
    sitemap_urls = [
        data.get('gunn_nissan_url', '').strip(),
        data.get('ingram_park_url', '').strip(),
        data.get('boerne_url', '').strip(),
        data.get('champion_nb_url', '').strip()
    ]

    # Filter out empty URLs
    sitemap_urls = [url for url in sitemap_urls if url]

    if not sitemap_urls:
        return jsonify({'error': 'At least one sitemap URL is required'}), 400

    openai_api_key = data.get('openai_api_key', '').strip()
    if not openai_api_key:
        return jsonify({'error': 'OpenAI API key is required'}), 400

    # Create job
    job_id = str(uuid.uuid4())
    job = AnalysisJob(job_id, sitemap_urls, openai_api_key)
    analysis_results[job_id] = job

    # Start analysis in background thread
    thread = threading.Thread(target=run_analysis, args=(job,))
    thread.daemon = True
    thread.start()

    return jsonify({
        'job_id': job_id,
        'message': 'Analysis started successfully'
    })


@app.route('/api/job-status/<job_id>')
def job_status(job_id):
    """Get status of an analysis job"""
    job = analysis_results.get(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify({
        'job_id': job_id,
        'status': job.status,
        'progress': job.progress,
        'completed': job.completed,
        'total_results': len(job.results),
        'total_errors': len(job.errors),
        'errors': job.errors[-10:]  # Last 10 errors
    })


@app.route('/api/download-csv/<job_id>')
def download_csv(job_id):
    """Download CSV file for completed job"""
    job = analysis_results.get(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if not job.completed or not job.csv_path:
        return jsonify({'error': 'Job not completed or CSV not available'}), 400

    return send_file(
        job.csv_path,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'nissan_pricing_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'vdp_limit': VDP_LIMIT})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
