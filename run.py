import subprocess

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
    main()