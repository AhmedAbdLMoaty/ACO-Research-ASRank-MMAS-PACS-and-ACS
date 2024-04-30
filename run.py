import subprocess
import os
import config

def run_all_tsp_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsp"):
            config.filename = os.path.join(folder_path, filename)
            main()

def main():
    algorithms = ["PACS", "mmas", "racs", "acs"]
    for algorithm in algorithms:
        print(f"Running {algorithm}...")
        result = subprocess.run(["python", f"{algorithm}.py"], capture_output=True, text=True)
        if result.stderr:
            print(f"Error running {algorithm}: {result.stderr}")
        else:
            with open(f"{algorithm}_output.txt", "a") as f:
                f.write(f"Results for {config.filename}:\n")
                f.write(result.stdout)
                f.write("\n")

if __name__ == "__main__":
    run_all_tsp_files_in_folder("./TSP files")