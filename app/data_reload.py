
from insta_scraper import multi_threaded_scrape
from data_retriever import DataRetriever
from calendar_connection import CalendarConnection
from ai_validation import EventParser
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import logger
import time
def main():
    logger.info("setting up objects...")
    retriver = DataRetriever()
    clubs = retriver.fetch_club_instagram_from_manifest()
    parser = EventParser()
    cc = CalendarConnection()
    logger.info("objects have been initiated")
    
    logger.info("initiating scraping with 3 threads")
    #multi_threaded_scrape(clubs, 3)
    logger.info('successful scrape!')
    
    logger.info("initiating ai and calendar file creation")
    for club in clubs:
        parser.parse_all_posts(club)
        cc.create_calendar_file(club)
    
    logger.info("completed.")
        
if __name__ == "__main__":
    starttime = time.time()
    main()
    logger.info(f"Elapsed time: {time.time() - starttime}")

    
    
        
        
        
    