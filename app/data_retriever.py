import os
import json
class DataRetriever:
    def __init__(self):
        self.working_path = os.path.join(os.path.dirname(__file__), '..', 'data')

    def get_user_dir(self):
        return self.working_path
    
    def club_data_exists(self, club_name):
        return os.path.exists(os.path.join(self.working_path, club_name)) and os.path.exists(os.path.join(self.working_path, club_name, "posts"))
    
    def fetch_club_info(self, club_name):
        if not self.club_data_exists(club_name):
            raise FileNotFoundError(f"Directory for {club_name} not found")
        
        # Load the club data
        with open(os.path.join(self.working_path, club_name, 'club_info.json'), 'r') as file:
            club_data = json.load(file)
        
        return club_data
    
    def fetch_club_posts(self, club_name):
        if not self.club_data_exists(club_name):
            raise FileNotFoundError(f"Directory for {club_name} not found")
        
        if not os.listdir(os.path.join(self.working_path, club_name, "posts")):
            raise FileNotFoundError(f"No posts found for {club_name}")
        
        posts_data = []
        for post in os.listdir(os.path.join(self.working_path, club_name, "posts")):
            with open(os.path.join(self.working_path, club_name, "posts", post), 'r') as file:
                post_data = json.load(file)
            
            posts_data.append(post_data)
            
        return posts_data
            

            
        
      
    
    
    