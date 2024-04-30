import subprocess
import os
import csv
import config
import psutil

def run_all_tsp_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsp"):
            absolute_path = os.path.join(os.getcwd(), folder_path, filename)
            config.filename = absolute_path
            main()

def main():
    algorithms = ["PACS", "mmas", "racs", "acs"]
    for algorithm in algorithms:
        print(f"Running {algorithm}...")
        print(f"Results for {os.path.basename(config.filename)}:")
        
        # Measure CPU consumption before running the algorithm
        before_cpu = psutil.cpu_percent(interval=0.1)

        result = subprocess.run(["python", f"{algorithm}.py", config.filename], capture_output=True, text=True)
        
        # Measure CPU consumption after running the algorithm
        after_cpu = psutil.cpu_percent(interval=0.1)

        if result.stderr:
            print(f"Error running {algorithm}: {result.stderr}")
        else:
            output_lines = result.stdout.splitlines()
            name = None
            comment = None
            dimensions = None
            best_tour = None
            best_distance = None

            for line in output_lines:
                if line.startswith("NAME"):
                    name = line.split(":")[1].strip()
                elif line.startswith("COMMENT"):
                    comment = line.split(":")[1].strip()
                elif line.startswith("DIMENSION"):
                    dimensions = line.split(":")[1].strip()
                elif line.startswith("Best tour"):
                    best_tour = line.split(":")[1].strip()
                elif line.startswith("Best distance"):
                    best_distance = line.split(":")[1].strip()

            memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # Memory usage in MB
            cpu_usage = after_cpu - before_cpu  # CPU consumption in percent

            write_to_csv(algorithm, os.path.basename(config.filename), name, comment, dimensions, best_tour, best_distance, memory_usage, cpu_usage)

def write_to_csv(algorithm, filename, name, comment, dimensions, best_tour, best_distance, memory_usage, cpu_usage):
    csv_filename = f"{algorithm}_output.csv"
    exists = os.path.isfile(csv_filename)
    with open(csv_filename, "a", newline='') as csvfile:
        fieldnames = ['Name', 'Comment', 'Dimensions', 'Filename', 'Best Tour', 'Best Distance', 'Memory Usage (MB)', 'CPU Consumption (%)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow({'Name': name, 'Comment': comment, 'Dimensions': dimensions, 'Filename': filename, 'Best Tour': best_tour, 'Best Distance': best_distance, 'Memory Usage (MB)': memory_usage, 'CPU Consumption (%)': cpu_usage})


if __name__ == "__main__":
    run_all_tsp_files_in_folder("./TSP files")
