import os
import json
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import dotenv

class DataRetriever:
    def __init__(self):
        dotenv.load_dotenv()
        # Initialize the S3 client
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-west-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'instinct-club-data')
        self.working_path = os.path.join(os.path.dirname(__file__), '..')


    def club_data_exists(self, club_name):
        """
        Check if the club's data exists in S3.
        """
        try:
            # Check if club_info.json exists
            self.s3.head_object(Bucket=self.bucket_name, Key=f"data/{club_name}/club_info.json")
            # Check if the posts directory exists
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=f"data/{club_name}/posts/")
            return 'Contents' in response
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def fetch_club_info(self, club_name):
        """
        Fetch club info from S3.
        """
        if not self.club_data_exists(club_name):
            raise FileNotFoundError(f"Directory for {club_name} not found")

        try:
            # Fetch club_info.json from S3
            response = self.s3.get_object(Bucket=self.bucket_name, Key=f"data/{club_name}/club_info.json")
            club_data = json.loads(response['Body'].read().decode('utf-8'))
            return club_data
        except ClientError as e:
            raise FileNotFoundError(f"Failed to fetch club info for {club_name}: {e}")

    def fetch_club_posts(self, club_name):
        """
        Fetch all posts for a club from S3.
        """
        if not self.club_data_exists(club_name):
            raise FileNotFoundError(f"Directory for {club_name} not found")

        try:
            # List all posts in the club's posts directory
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=f"data/{club_name}/posts/")
            if 'Contents' not in response:
                raise FileNotFoundError(f"No posts found for {club_name}")

            posts_data = []
            for obj in response['Contents']:
                # Fetch each post file
                post_response = self.s3.get_object(Bucket=self.bucket_name, Key=obj['Key'])
                post_data = json.loads(post_response['Body'].read().decode('utf-8'))
                posts_data.append(post_data)

            return posts_data
        except ClientError as e:
            raise FileNotFoundError(f"Failed to fetch posts for {club_name}: {e}")

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
    retriever = DataRetriever()
    print(retriever.fetch_club_info('icssc.uci'))
    print(retriever.fetch_club_posts('icssc.uci'))
    
    