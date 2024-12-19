import ast
import os
import dotenv
from openai import OpenAI
import json


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


    def parse_post(self, post_path: str):
        # Load the post data
        try:
            with open(post_path, 'r') as file:
                post_data = json.load(file)
            
           
            # Extract the text from the post data
            post_text = post_data['Description']
            post_date = post_data['Date']

            if 'Parsed' in post_data:
                raise Exception("Post has already been parsed.")

            """Parse dates from the text using OpenAI's GPT-4 API."""

            # Send request to OpenAI API to extract dates
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Correct model name
                messages=[
                    {
                        "role": "system",
                        "content": "I want you to parse a description and a context date to give me information on an event listed in it."
                        "I want you to return the ISO date with time for a piece of text and what you think the estimated duration of the event is(if long, just put sign up)."
                        "There could be multiple dates and times listed, so if there are multiple, "
                        "I want all occurences. I will also give a context date in iso format, and if a "
                        "day of the week is given, use the context date. Simply output a list of dictionaries in the format "
                        "[{Name: \"What you think the event name is \", Date: \"iso date\", Details: \"what the event is with any links provided\", Duration: {\"estimated duration\" ex. \"days:\"...:, \"hours:\":...,}}...]. No duplicates, no newlines, no json starting."
                    },
                    {
                        "role": "user",
                        "content": f"{post_text} context date: {post_date}"
                    }
    ],
    temperature=0.5  # Adjust the creativity level
) 

            # Return parsed date results
            print("Successful parse.")
            return json.loads(completion.choices[0].message.content)

        except AttributeError as e:
            print(f"File cannot find correct attributes {e}")
            return []
        except Exception as e:
            print(f"Error while parsing: {e}")
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
                print("Successfully stored")
                json.dump(post_data, file)
        except Exception as e:
            print(f"Error while storing parsed info: {e}")

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
    parser.parse_all_posts("merageleads")



