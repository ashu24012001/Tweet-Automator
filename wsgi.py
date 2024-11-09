import subprocess
from app.main import app

# Start tweet.py as a background process
subprocess.Popen(["python", "tweet.py"])

if __name__ == "__main__":
    app.run()