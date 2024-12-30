import os
import sys
import dotenv
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from app import server



    
if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        server.scheduler.start()
    server.app.run(debug=True, host='127.0.0.1', port=5022)