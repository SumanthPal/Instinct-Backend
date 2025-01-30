from io import BytesIO, StringIO
from flask import Flask, request, jsonify, send_file, abort
from app.tools.ai_validation import EventParser
from app.tools.calendar_connection import CalendarConnection
from app.tools.insta_scraper import InstagramScraper, multi_threaded_scrape
from app.tools.data_retriever import DataRetriever
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from threading import Lock
from flask_cors import CORS
import dotenv
import os
import sys
import atexit

# Load environment variables
dotenv.load_dotenv()
from tools.logger import logger

# Initialize dependencies
calendar = CalendarConnection()
retriever = DataRetriever()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins temporarily (adjust for production)

# Scheduler Configuration
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
scheduler = BackgroundScheduler(jobstores=jobstores, daemon=True)
job_running = False
job_lock = Lock()

# Job: Reload Data
def reload_data():
    global job_running
    with job_lock:
        if job_running:
            logger.info("Reload data job already running.")
            return
        job_running = True

    try:
        logger.info("Starting data reload...")
        parser = EventParser()
        clubs = retriever.fetch_club_instagram_from_manifest()
        multi_threaded_scrape(clubs, 3)

        for club in clubs:
            parser.parse_all_posts(club)
            calendar.create_calendar_file(club)

        logger.info("Data reload completed successfully.")
    except Exception as e:
        logger.error(f"Error during data reload: {e}")
    finally:
        with job_lock:
            job_running = False


# Job: File Cleanup
def file_cleanup():
    base_dir = "../data"
    for root, _, files in os.walk(base_dir):
        if not root.endswith("posts"):
            continue
        files = sorted(files, key=lambda f: os.path.getctime(os.path.join(root, f)))
        if len(files) > 10:
            extra_files = len(files) - 10
            logger.info(f"Cleaning {extra_files} extra files in {root}...")
            for file in files[:extra_files]:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    logger.info(f"Removed: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing file {file_path}: {e}")


# Add jobs to the scheduler
scheduler.add_job(
    reload_data, 'interval', days=2, misfire_grace_time=60, id='reload_data_job', replace_existing=True
)
scheduler.add_job(
    file_cleanup, 'interval', days=1, misfire_grace_time=60, id='file_cleanup_job', replace_existing=True
)

# Start Scheduler
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    scheduler.start()
atexit.register(lambda: scheduler.shutdown())


# Routes
@app.route('/')
def home():
    logger.info("Home endpoint called.")
    return jsonify({"message": "Welcome to the Club API"})


@app.route("/club", methods=['POST'])
def club():
    return jsonify({"message": "Club page"})


@app.route("/club/<username>", methods=['GET'])
def club_data(username):
    try:
        logger.info(f"Fetching data for club: {username}")
        return retriever.fetch_club_info(username)
    except FileNotFoundError:
        return jsonify({"message": "Club not found"}), 404
    except Exception as e:
        logger.error(f"Error fetching club data: {e}")
        return jsonify({"message": f"Error: {e}"}), 500


@app.route("/club/<username>/posts", methods=['GET'])
def club_post_data(username):
    try:
        logger.info(f"Fetching posts for club: {username}")
        return retriever.fetch_club_posts(username)
    except FileNotFoundError:
        return jsonify({"message": "Club posts not found"}), 404
    except Exception as e:
        logger.error(f"Error fetching club posts: {e}")
        return jsonify({"message": f"Error: {e}"}), 500


@app.route("/club-manifest", methods=['GET'])
def club_manifest():
    try:
        logger.info("Fetching club manifest.")
        return jsonify(retriever.fetch_manifest())
    except Exception as e:
        logger.error(f"Error fetching club manifest: {e}")
        return jsonify({"message": f"Error: {e}"}), 500


@app.route("/club/<username>/calendar.ics", methods=['GET'])
def club_calendar(username):
    try:
        logger.info(f"Fetching calendar for club: {username}")
        ics_content = retriever.fetch_club_calendar(username)
        ics_file = BytesIO(ics_content)
        return send_file(
            ics_file,  # File-like object containing the .ics content
            download_name=f"{username}_calendar.ics",  # Name of the file when downloaded
            as_attachment=False,  # Set to True if you want to force download
            mimetype='text/calendar',  # MIME type for .ics files
        )
        # calendar.create_calendar_file(username)
        # return send_file(
        #     calendar.get_ics_path(username),
        #     download_name=f"{username}_calendar.ics",
        #     as_attachment=False,
        #     mimetype='text/calendar',
        # )
    except FileNotFoundError as e:
        logger.error(f"Calendar file not found for {username}: {e}")
        abort(404, description="Calendar file not found")
    except Exception as e:
        logger.error(f"Error fetching calendar for {username}: {e}")
        abort(500, description="Internal Server Error")


@app.route("/job-status", methods=['GET'])
def job_status():
    response = {}
    for job_id in ['reload_data_job', 'file_cleanup_job']:
        job = scheduler.get_job(job_id)
        response[job_id] = {
            "job_id": job.id if job else "N/A",
            "next_run_time": str(job.next_run_time) if job else "N/A"
        }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5022)
