import ast
import os
import dotenv
from openai import OpenAI
import json
from typing import List, Dict
import time


class EventParser:
    def __init__(self):

        # Load environment variables (for OpenAI API key)
        dotenv.load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


    def validate_username(self, username)-> str:
        user_dir =  os.path.join(os.path.dirname(__file__), '..', 'data', username)
        if not os.path.exists(user_dir):
            raise FileNotFoundError(f"Directory for {username} not found")
        post_dir = os.path.join(user_dir, "posts")
        if not os.path.exists(post_dir):
            raise FileNotFoundError(f"Post Directory for {username} not found")
        if os.listdir(post_dir):
            return user_dir, post_dir
        else:
            raise FileNotFoundError(f"No posts found for {username}")


    def parse_post(self, post_path: str) -> List[Dict]:
        """
        Parses a post to extract event data using OpenAI's GPT-4 API.

        Args:
            post_path (str): Path to the post file.

        Returns:
            List[Dict]: Parsed events or an empty list if parsing fails.
        """
        MAX_RETRIES = 3  # Define the number of retries
        RETRY_DELAY = 2  # Delay (in seconds) between retries

        # Load the post data
        try:
            with open(post_path, 'r') as file:
                post_data = json.load(file)
            
            post_text = post_data['Description']
            post_date = post_data['Date']

            if 'Parsed' in post_data:
                raise Exception("Post has already been parsed.")

            # Retry mechanism for API calls
            for attempt in range(MAX_RETRIES):
                try:
                    print(f"Parsing attempt {attempt + 1}...")

                    # Send request to OpenAI API to extract dates
                    completion = self.client.chat.completions.create(
                        model="gpt-4o-mini",  # Ensure the model name is correct
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                        "You must strictly adhere to the following rules:\n"
    "1. Always respond in JSON format and ensure it is valid JSON. Do not include any extra text, markdown, or formatting outside of JSON.\n"
    "2. The response must not include any commentary, explanation, or additional notes.\n"
    "3. If the input cannot be parsed, return an empty JSON array: [].\n"
    "4. The JSON must be formatted as a list of dictionaries like this example:\n"
    "[{\"Name\": \"Event Name\", \"Date\": \"ISO date\", \"Details\": \"Event details\", \"Duration\": {\"estimated duration\": {\"days\": 0, \"hours\": 0}}}]\n"
    "5. If the event spans multiple dates, create one entry for the start date and another for the end date, each with a duration of 0."

                                )
                            },
                            {
                                "role": "user",
                                "content": f"{post_text} context date: {post_date}"
                            }
                        ],
                        temperature=0.3
                    )

                    # Process and validate the response
                    response = completion.choices[0].message.content
                    events = json.loads(response)  # Attempt to parse the JSON

                    # Check if the response format is valid
                    if isinstance(events, list) and all(isinstance(event, dict) for event in events):
                        print("Successful parse.")
                        return events

                    raise ValueError("Invalid API response format")

                except json.JSONDecodeError as e:
                    print(response)
                    print(f"JSON decoding error: {e}")
                except Exception as e:
                    print(f"Error during API call: {e}")

                if attempt < MAX_RETRIES - 1:
                    print(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)

            # If retries fail, log and return an empty list
            print("Failed to parse post after multiple attempts.")
            return []

        except (FileNotFoundError, KeyError) as e:
            print(f"Error loading post data: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def parse_all_posts(self, username):
        _, post_dir = self.validate_username(username)
        for post in os.listdir(post_dir):
            post_path = os.path.join(post_dir, post)
            parsed_info = self.parse_post(post_path)
            self.store_parsed_info(post_path, parsed_info)

    def store_parsed_info(self, post_path: str, parsed_info: list):
        try:
            with open(post_path, 'r') as file:
                post_data = json.load(file)
            if  parsed_info == []:
                return
            post_data['Parsed'] = parsed_info
            with open(post_path, 'w') as file:
                print(f"Successfully stored {post_path}")
                json.dump(post_data, file)
        except Exception as e:
            print(f"Error while storing parsed info: {e}\n response: {post_data}")
            

    def is_parsed(self, post_path: str):
        with open(post_path, 'r') as file:
            post_data = json.load(file)
        return 'Parsed' in post_data
    
    def check_if_first_is_parsed(self, username):
        _, post_dir = self.validate_username(username)
        post_paths = os.listdir(post_dir)
        return self.is_parsed(os.path.join(post_dir, post_paths[0]))
        
if __name__ == "__main__":
    # Example usage
    parser = EventParser()
    
    parser.parse_all_posts("vevocalists")
  

    



