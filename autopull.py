#!/usr/bin/env python3
import subprocess
import time
import os

REPO_PATH = os.path.dirname(os.path.realpath(__file__))  # Change to your repo path
BRANCH = "main"
CHECK_INTERVAL = 60  # seconds

def pull_repo():
    print("Fetching latest changes...")
    subprocess.run(["git", "fetch"], cwd=REPO_PATH)
    
    local = subprocess.check_output(["git", "rev-parse", BRANCH], cwd=REPO_PATH).strip()
    remote = subprocess.check_output(["git", "rev-parse", f"origin/{BRANCH}"], cwd=REPO_PATH).strip()
    
    if local != remote:
        print("New changes detected! Pulling...")
        subprocess.run(["git", "pull"], cwd=REPO_PATH)
    else:
        print("No new changes.")

if __name__ == "__main__":
    while True:
        pull_repo()
        time.sleep(CHECK_INTERVAL)
