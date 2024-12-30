from flask import Flask, request, jsonify, send_file

from ai_validation import EventParser
from calendar_connection import CalendarConnection
from insta_scraper import InstagramScraper, multi_threaded_scrape
from data_retriever import DataRetriever 
from apscheduler.schedulers.background import BackgroundScheduler

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
   

@app.route("/club/<username>/calendar", methods=['GET'])
def club_calender(username):
    calendar.create_calendar_file(username)
    return send_file(calendar.get_ics_path(username), download_name=f"{username}_calendar.ics", as_attachment=True)

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
    

def reload_data():
    print("reloading")
    logger.info("reloading started")
    parser = EventParser()
    clubs = ['icssc.uci', 'fusionatuci','productuci', 'accounting.uci','asuci_','ucirvine']
    multi_threaded_scrape(clubs,3)
    for club in clubs:
        parser.parse_all_posts(club)
        calendar.create_calendar_file(club)
   
schedular = BackgroundScheduler(daemon=True)
schedular.add_job(reload_data, 'interval', minutes=1)
schedular.start()


    
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5022)  # Change 5000 to your desired porta
    