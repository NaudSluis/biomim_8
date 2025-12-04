from flask import Flask
import subprocess
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='/home/group8/biomim_8/flask_app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

@app.route('/run', methods=['POST'])
def run():
    app.logger.info("Starting the program...")
    
    # Run the script and capture the output
    result = subprocess.run(["/home/group8/biomim_8/run.sh"], capture_output=True, text=True)
    
    # Log the output
    app.logger.info(result.stdout)
    app.logger.error(result.stderr)
    
    if result.returncode == 0:
        app.logger.info("Program started successfully!")
        return "Program started successfully!", 200
    else:
        app.logger.error("Program failed to start. Check log for details.")
        return "Program failed to start. Check log for details.", 500

@app.route('/status', methods=['GET'])
def status():
    return "Raspberry Pi ready.", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
