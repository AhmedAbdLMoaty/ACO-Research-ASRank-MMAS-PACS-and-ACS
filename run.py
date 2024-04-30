import subprocess
import os
import csv
import config

def run_all_tsp_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsp"):
            absolute_path = os.path.join(os.getcwd(), folder_path, filename)
            config.filename = absolute_path
            main()

def write_to_csv(algorithm, filename, name, comment, dimensions, best_tour, best_distance):
    csv_filename = f"{algorithm}_output.csv"
    exists = os.path.isfile(csv_filename)
    with open(csv_filename, "a", newline='') as csvfile:
        fieldnames = ['Name', 'Comment', 'Dimensions', 'Filename', 'Best Tour', 'Best Distance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow({'Name': name, 'Comment': comment, 'Dimensions': dimensions, 'Filename': filename, 'Best Tour': best_tour, 'Best Distance': best_distance})

def main():
    algorithms = ["PACS", "mmas", "racs", "acs"]
    for algorithm in algorithms:
        print(f"Running {algorithm}...")
        print(f"Results for {os.path.basename(config.filename)}:")
        result = subprocess.run(["python", f"{algorithm}.py", config.filename], capture_output=True, text=True)
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

            write_to_csv(algorithm, os.path.basename(config.filename), name, comment, dimensions, best_tour, best_distance)


if __name__ == "__main__":
    run_all_tsp_files_in_folder("./TSP files")
