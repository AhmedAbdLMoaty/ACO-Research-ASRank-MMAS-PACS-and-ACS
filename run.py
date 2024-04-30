import subprocess
import os
import config

def run_all_tsp_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsp"):
            absolute_path = os.path.join(os.getcwd(), folder_path, filename)
            config.filename = absolute_path
            main()

def main():
    algorithms = ["PACS", "mmas" , "racs" , "acs"]
    for algorithm in algorithms:
        print(f"Running {algorithm}...")
        print(f"Results for {os.path.basename(config.filename)}:")
        result = subprocess.run(["python", f"{algorithm}.py", config.filename], capture_output=True, text=True)
        if result.stderr:
            print(f"Error running {algorithm}: {result.stderr}")
        else:
            with open(f"{algorithm}_output.txt", "a") as f:
                f.write(f"Results for {os.path.basename(config.filename)}\n")
                f.write(result.stdout)
                f.write("\n")


if __name__ == "__main__":
    run_all_tsp_files_in_folder("./TSP files")