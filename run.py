import subprocess
import os
import config

def run_all_tsp_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsp"):
            config.filename = os.path.join(folder_path, filename)
            main()

def main():
    print("Running PACS...")
    subprocess.run(["python", "PACS.py"])
    print("Running MMAS...")
    subprocess.run(["python", "mmas.py"])
    print("Running RACS...")
    subprocess.run(["python", "racs.py"])
    print("Running ACS...")
    subprocess.run(["python", "acs.py"])

if __name__ == "__main__":
    run_all_tsp_files_in_folder("./TSP files")