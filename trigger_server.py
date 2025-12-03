from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run():
    # Run the script
    subprocess.Popen(["/home/group8/biomim_8/run.sh"])
    return "Program started!", 200

@app.route('/status', methods=['GET'])
def status():
    return "Raspberry Pi ready.", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
