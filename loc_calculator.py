import os
import time

def count_lines_of_code(file_path):
    with open(file_path, 'r') as file:
        return sum(1 for line in file if line.strip() and not (line.strip().startswith('#') or line.strip().startswith('//') or line.strip().startswith('<!--') or line.strip().startswith('/*')))

def calculate_loc(root_dir):
    total_loc = 0
    # Define folders for each file extension
    folders = {
        ".py": "actions",
        ".yml": "data",
        ".html": "templates",
        ".css": "static/css",
        ".js": "static/js"
    }
    for ext, folder in folders.items():
        folder_path = os.path.join(root_dir, folder)
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith(ext):
                    file_path = os.path.join(root, file_name)
                    loc = count_lines_of_code(file_path)
                    total_loc += loc
    
    # Include .py and .yml files in the root directory
    for file_name in os.listdir(root_dir):
        if file_name.endswith(".py") or file_name.endswith(".yml"):
            file_path = os.path.join(root_dir, file_name)
            loc = count_lines_of_code(file_path)
            total_loc += loc
            
    # Write total_loc to loc.txt file
    with open("loc.txt", "w") as f:
        f.write(str(total_loc))

    # print(f"Total LOC: {total_loc}")

if __name__ == "__main__":
    root_directory = "E:/Study2024/rasaFinancial"
    
    # Run continuously
    while True:
        calculate_loc(root_directory)
        time.sleep(5)  
