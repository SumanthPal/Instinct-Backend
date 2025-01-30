# Instinct-Backend
The backend for the Instinct Club Connect Protocol.

# Setup Instructions

1. Set up Python venv and start.
```shell
python -m venv venv
activate
```
2. Download dependencies
```shell
pip install -r requirements.txt
```
3. Create a `.env` file and put the following:
```txt
OPEN_AI_KEY=
INSTAGRAM_USERNAME=
INSTAGRAM_PASSWORD=
COOKIE=(base64 encoded instagram cookie) [can be generated from  `InstagramScraper`
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
S3_BUCKET_NAME=
```
4. Run `gunicorn main:app` to test
5. A server should be running on http://localhost:8000/


