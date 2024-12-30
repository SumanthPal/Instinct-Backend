from flask import Flask, request, jsonify, send_file, abort

from ai_validation import EventParser
from calendar_connection import CalendarConnection
from insta_scraper import InstagramScraper, multi_threaded_scrape
from data_retriever import DataRetriever 
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Lock
import dotenv
import os
import sys
dotenv.load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import logger

calendar = CalendarConnection()
retriever = DataRetriever()
app = Flask(__name__)




@app.route('/')
def home():
    print("Hello, World!")
    return jsonify({"message": "Hello, World!"})

@app.route("/club", methods=['POST'])
def club():
    return jsonify({"message": "Club page"})

@app.route("/club/<username>", methods=['GET'])
def club_data(username):
    print("Fetching", username)
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
    except FileNotFoundError:
        return jsonify({"message": "Club not found"}), 404 
    except Exception as e:
        return jsonify({"message": f"Error: {e}"}), 500
   

@app.route("/club/<username>/calendar.ics", methods=['GET'])
def club_calender(username):
    try:
        calendar.create_calendar_file(username)
        return send_file(calendar.get_ics_path(username), 
                        download_name=f"{username}_calendar.ics", 
                        as_attachment=False,
                        mimetype='text/calendar',
                        )
    except Exception as e:
        logger.error(f"Error generating or serving the .ics file for {username}: {str(e)}")
        abort(500, description="Internal Server Error")

@app.route("/club/consolidate", methods=['POST'])
def consolidate_clubs():
    data = request.json
    # Check if club is legit
    club_name = data.get('name')
    club_genre = data.get('genre')
    
    if not club_name or not club_genre:
        return jsonify({"message": "Invalid club data"}), 400
    
    existing_clubs = retriever.retrieve_club_list()
    if club_name in existing_clubs:
        return jsonify({"message": "Club already exists"}), 409
    
    existing_clubs[club_name] = {'name': club_name, 'genre': club_genre}
    
    return jsonify({"message": "Club successfully added"}), 201
    
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
        clubs = ['icssc.uci', 'fusionatuci', 'productuci', 'accounting.uci', 'asuci_', 'ucirvine']
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

# Initialize the scheduler
scheduler = BackgroundScheduler(daemon=True)

# Add job with misfire grace time to handle skipped runs gracefully
scheduler.add_job(
    reload_data,
    'interval',
    days=2,
    misfire_grace_time=1 # Skip missed executions if the job overlaps
)

    
if __name__ == "__main__":
    
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        scheduler.start()
    app.run(debug=True, host='127.0.0.1', port=5022)  # Change 5000 to your desired porta
    