import os
import json
from pathlib import Path
import dropbox
import dotenv
import dropbox.exceptions

class DataRetriever:
    def __init__(self):
        dotenv.load_dotenv()
        self.working_path = os.path.join(os.path.dirname(__file__), '..')
        self.dbx = dropbox.Dropbox(os.getenv('DROPBOX_API_KEY'))

    def get_user_dir(self):
        return os.path.join(self.working_path, 'data')
    
    def club_data_exists(self, club_name):
        try:
            self.dbx.files_get_metadata(f'/data/{club_name}')
            self.dbx.files_get_metadata(f'/data/{club_name}/posts')
            return True
        except dropbox.exceptions.ApiError as e:
            return False
        #return os.path.exists(os.path.join(self.working_path, 'data', club_name)) and os.path.exists(os.path.join(self.working_path, 'data', club_name, "posts"))
    
    def fetch_club_info(self, club_name):
        if not self.club_data_exists:
            raise FileNotFoundError(f"Directory for {club_name} not found")
        
        _, res = self.dbx.files_download(f'/data/{club_name}/club_info.json')
        club_data = json.loads(res.content)
        
        return club_data

            
        # if not self.club_data_exists(club_name):
        #     raise FileNotFoundError(f"Directory for {club_name} not found")
        
        # # Load the club data
        # with open(os.path.join(self.working_path, 'data', club_name, 'club_info.json'), 'r') as file:
        #     club_data = json.load(file)
        
        # return club_data
    

    
    def fetch_club_posts(self, club_name):
        if not self.club_data_exists:
            raise FileNotFoundError(f"Directory for {club_name} not found")
        
        try:
            res = self.dbx.files_list_folder(f'/data/{club_name}/posts')
            if not res.entries:
                raise FileNotFoundError(f"No posts found for {club_name}")
        except dropbox.exceptions.ApiError as e:
            raise FileNotFoundError(f"No posts found for {club_name}")
        
        posts_data = []
        for entry in res.entries:
            _, res = self.dbx.files_download(entry.path_lower)
            post_data = json.loads(res.content)
            posts_data.append(post_data)
                
        return posts_data
        # if not self.club_data_exists(club_name):
        #     raise FileNotFoundError(f"Directory for {club_name} not found")
        
        # if not os.listdir(os.path.join(self.working_path, 'data', club_name, "posts")):
        #     raise FileNotFoundError(f"No posts found for {club_name}")
        
        # posts_data = []
        # for post in os.listdir(os.path.join(self.working_path, 'data', club_name, "posts")):
        #     with open(os.path.join(self.working_path, 'data', club_name, "posts", post), 'r') as file:
        #         post_data = json.load(file)
            
        #     posts_data.append(post_data)
            
        # return posts_data
    
    def check_if_post_exists(self, post_name) -> bool:
        try:
            self.dbx.files_get_metadata(post_name)
            return True
        except dropbox.exceptions.ApiError as e:
            return False
        #return Path(post_name).exists()
    
    def fetch_manifest(self) -> json:
        with open(os.path.join(self.working_path, 'manifest.json'), 'r') as f:
            club_data = json.load(f)
            
        return club_data

    def fetch_club_instagram_from_manifest(self) -> list[str]:
        clubs = []
        for c in self.fetch_manifest():
            clubs.append(c['instagram'])
        
        return clubs
    
if __name__ == "__main__":
    retriver = DataRetriever();
    print(retriver.fetch_club_instagram_from_manifest())
        
        

            
        
      
    
    
    