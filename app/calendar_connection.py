from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import os
from ics import Calendar, Event
from data_retriever import DataRetriever

class CalendarConnection:
    def __init__(self):
        self.calendar = Calendar()
        self.retriever = DataRetriever()
        
    def create_calendar_file(self, username):
            # Define the path to the .ics file
   
            ics_path = os.path.join(self.retriever.get_user_dir(), username, "calendar_file.ics")
            
            # Load the calendar file if it exists
            if self.check_for_presence_of_file(ics_path):
                with open(ics_path, 'r') as f:
                    self.calendar = Calendar(f.read())

            # Fetch post information
            posts = self.retriever.fetch_club_posts(username)

            # Add events to the calendar
            for post in posts:
                for event in post['Parsed']:
                    try:
                        new_event = Event()
                        new_event.name = event['Name']
                        new_event.begin = event['Date']  # Ensure this is in ISO 8601 or datetime format
                        duration = event['Duration']['estimated duration']
                        
                        # Add duration if provided
                        if 'days' in duration or 'hours' in duration:
                            days = duration.get('days', 0)
                            hours = duration.get('hours', 0)
                            total_seconds = (days * 86400) + (hours * 3600)
                            new_event.duration = datetime.timedelta(seconds=total_seconds)
                        
                        # Check for duplicates and add the event
                        if not self.is_duplicate(new_event):
                            self.calendar.events.add(new_event)
                    except Exception as e:
                        print(f"Error while adding event: {e}")

            # Save the updated calendar to the .ics file
            with open(ics_path, 'w') as f:
                f.writelines(self.calendar)

            print("Calendar file successfully created/updated.")
        
 
    
    def check_for_presence_of_file(self, ics_path):
        return os.path.exists(ics_path)
    
    def get_ics_path(self, username):
        return os.path.join(self.retriever.get_user_dir(), username, "calendar_file.ics")
    

    def is_duplicate(self, new_event):
        """
        Check if the event already exists in the calendar.

        Args:
            new_event (Event): The event to check.

        Returns:
            bool: True if a duplicate exists, False otherwise.
        """
        for event in self.calendar.events:
            if (event.name == new_event.name and event.begin == new_event.begin):
                return True
        return False


if __name__ == "__main__":
    calendar = CalendarConnection()
    calendar.create_calendar_file("icssc.uci")
    
    