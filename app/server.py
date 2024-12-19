from flask import Flask, request, jsonify, send_file

from ai_validation import EventParser
from calendar_connection import CalendarConnection
from insta_scraper import InstagramScraper
from data_retriever import DataRetriever 
import dotenv
import os

dotenv.load_dotenv()
scraper = InstagramScraper(os.getenv("INSTAGRAM_USERNAME"), os.getenv("INSTAGRAM_PASSWORD"))
parser = EventParser()
calendar = CalendarConnection()
retriever = DataRetriever()
app = Flask(__name__)




@app.route('/')
def home():
    print("Hello, World!")
    return jsonify({"message": "Hello, World!"})


@app.route("/<username>", methods=['GET', 'POST'])
def club_data(username):
    print("Fetching", username)
    try:
        return retriever.fetch_club_info(username)
    except FileNotFoundError:
        return jsonify({"message": "Club not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {e}"}), 500

@app.route("/<username>/posts", methods=['POST', 'GET'])
def club_post_data(username):
    try:
        return retriever.fetch_club_posts(username)
    except FileNotFoundError:
        return jsonify({"message": "Club not found"}), 404 
    except Exception as e:
        return jsonify({"message": f"Error: {e}"}), 500
   

@app.route("/<username>/calendar", methods=['POST', 'GET'])
def club_calender(username):
    calendar.create_calendar_file(username)
    return send_file(calendar.get_ics_path(username), download_name=f"{username}_calendar.ics", as_attachment=True)
    

if __name__ == "__main__":
    try:
        app.run(debug=True, host='127.0.0.1', port=5022)  # Change 5000 to your desired port

    finally:
        #scraper._driver_quit()
        pass