from flask import Flask, request, jsonify, send_file, abort
from ai_validation import EventParser
from calendar_connection import CalendarConnection
from insta_scraper import InstagramScraper, multi_threaded_scrape
from data_retriever import DataRetriever 
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from threading import Lock
from flask_cors import CORS

import dotenv
import os
import sys
import atexit

dotenv.load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import logger

calendar = CalendarConnection()
retriever = DataRetriever()
app = Flask(__name__)
#CORS(app, origins=["http://www.google.com"])  # Replace with your frontend URL

# Initialize the scheduler with a SQLAlchemy job store
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
scheduler = BackgroundScheduler(jobstores=jobstores, daemon=True)

# Global flag to track if the job is running
job_running = False
job_lock = Lock()

def reload_data():
    global job_running

    with job_lock:
        if job_running:
            logger.info("Job is already running, skipping this execution.")
            return  # Skip execution if the job is already running
        job_running = True

    try:
        logger.info("Reloading data started.")

        # Simulated tasks
        parser = EventParser()
        clubs = retriever.fetch_club_instagram_from_manifest()
            
        multi_threaded_scrape(clubs, 3)

        for club in clubs:
            parser.parse_all_posts(club)
            calendar.create_calendar_file(club)

        logger.info("Reloading data completed.")
    except Exception as e:
        logger.error(f"An error occurred during data reloading: {e}")
    finally:
        with job_lock:
            job_running = False  # Reset the flag to allow the next execution

def file_cleanup():
    """
    Cleans up club data files. Ensures each `data/clubname/posts/` directory
    has at most 10 posts, removing the oldest files if necessary.
    """
    base_dir = "../data"  # Root directory containing club data
    for root, dirs, files in os.walk(base_dir):
        # Skip the base directory and focus on `posts` subdirectories
        if not root.endswith("posts"):
            continue

        # Sort files by creation time (oldest first)
        files = sorted(files, key=lambda f: os.path.getctime(os.path.join(root, f)))

        # If there are more than 10 files, remove the oldest ones
        if len(files) > 10:
            extra_files = len(files) - 10
            logger.info(f"Directory {root} has {len(files)} files, cleaning up {extra_files}...")
            for file in files[:extra_files]:  # Remove the oldest files
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    logger.info(f"Removed old file: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing file {file_path}: {e}")


# Add job with misfire grace time to handle skipped runs gracefully
scheduler.add_job(
    reload_data,
    'interval',
    days=2,
    misfire_grace_time=60,  # 60 seconds grace time for missed executions
    id='reload_data_job',
    replace_existing=True
)

# Add the file_cleanup job
scheduler.add_job(
    file_cleanup,
    'interval',
    days=1,  # Run daily
    misfire_grace_time=60,  # 60 seconds grace time for missed executions
    id='file_cleanup_job',
    replace_existing=True
)

# Start the scheduler when the application starts
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def home():
    logger.info("Hello, World!")
    return jsonify({"message": "Hello, World!"})

@app.route("/club", methods=['POST'])
def club():
    return jsonify({"message": "Club page"})

@app.route("/club/<username>", methods=['GET'])
def club_data(username):
    logger.info("Fetching", username)
    try:
        return retriever.fetch_club_info(username)
    except FileNotFoundError:
        return jsonify({"message": "Club not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {e}"}), 500

@app.route("/club/<username>/posts", methods=['GET'])
def club_post_data(username):
    try:
        return retriever.fetch_club_posts(username)
    except FileNotFoundError as e:
        return jsonify({f"message": f"Club not found {e.filename}", }), 404 
    except Exception as e:
        return jsonify({"message": f"Error: {e}"}), 500
@app.route("/job-status", methods=['GET'])
def job_status():
    reload_data_job = scheduler.get_job('reload_data_job')
    file_cleanup_job = scheduler.get_job('file_cleanup_job')

    response = {}

    if reload_data_job:
        response["reload_data_job"] = {
            "job_id": reload_data_job.id,
            "next_run_time": str(reload_data_job.next_run_time),
            "pending": reload_data_job.pending,
            "running": job_running  # Use the global flag for reload_data job
        }
    else:
        response["reload_data_job"] = {"message": "Job not found"}

    if file_cleanup_job:
        response["file_cleanup_job"] = {
            "job_id": file_cleanup_job.id,
            "next_run_time": str(file_cleanup_job.next_run_time),
            "pending": file_cleanup_job.pending,
            "running": False  # Add a flag if you want to track running state for this job
        }
    else:
        response["file_cleanup_job"] = {"message": "Job not found"}

    return jsonify(response)
@app.route("/club-manifest", methods=['GET'])
def club_manifest():
    """club manifest features all clubs w/ relevant information"""
    return retriever.fetch_manifest()
@app.route("/club/<username>/calendar.ics", methods=['GET'])
def club_calendar(username):
    """Route for getting the ics file for a club"""
    try:
        # Generate the .ics file
        calendar.create_calendar_file(username)
        
        # Serve the .ics file with the correct MIME type
        return send_file(
            calendar.get_ics_path(username),
            download_name=f"{username}_calendar.ics",
            as_attachment=False,
            mimetype='text/calendar',
        )
    except Exception as e:
        logger.error(f"Error generating or serving the .ics file for {username}: {str(e)}")
        abort(500, description="Internal Server Error")
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5022)  