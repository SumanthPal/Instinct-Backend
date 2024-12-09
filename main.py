import os

import dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

from app import ai_validation, calendar_connection
from app.insta_scraper import InstagramScraper


def main():
    dotenv.load_dotenv()
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    print(f"Username: {username}\nPassword: {password}")
    club_username = "ucibadminton"

    scraper = InstagramScraper(username, password)
    # scraper.login()
    club_info = scraper.get_club_info(club_username)
    post_links = club_info["Posts"]
    information = scraper.get_post_info(post_links)
    scraper._driver_quit()



    iso_objects = [scraper.convert_to_datetime(date_str).isoformat() for date_str in information[1]]

    for date in iso_objects:
        print(date)

    ai_list = []
    for iso in range(len(iso_objects)):
        try:
            ai_list.append(ai_validation.parse_date(information[0][iso], iso_objects[iso]))

        except ValueError:
            print("Error parsing file data. Please look at the information yourself.")
            print(information[0][iso])


    ai_list = [sublist for sublist in ai_list if sublist]
    # Build the Calendar API service
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file('./auth/cred.json', SCOPES)
    creds = flow.run_local_server(port=8080)

    # Build the Calendar API service
    service = calendar_connection.build('calendar', 'v3', credentials=creds)
    print(ai_list)

    for event in ai_list:
        calendar_connection.create_events_from_list(service, event)


if __name__ == "__main__":
    main()