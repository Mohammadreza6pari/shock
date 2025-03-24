import zipfile
import os

def create_zip_file_of_folder(source_folder_path, destination_file_path):
    if os.path.exists(destination_file_path):
        return
    
    os.makedirs(source_folder_path, exist_ok=True)
    with zipfile.ZipFile(destination_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, source_folder_path))

