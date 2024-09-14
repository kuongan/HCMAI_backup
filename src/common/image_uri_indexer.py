import json
import os

def image_uri_indexer(dir_path: str, uri_to_index_file_path: str, idex_to_uri_file_path: str):
    """
    Load json file from ui_to_index_file_path and index the image uri to idex_to_uri_file_path
    If the file is not found, create a new one
    If the file is found, get the latest index and continue indexing from there
    """
    # Check if the json file doesn't exist, create a new one
    if not os.path.exists(uri_to_index_file_path):
        with open(uri_to_index_file_path, 'w') as file:
            json.dump({}, file)
    with open(uri_to_index_file_path, 'r') as file:
        uri_to_index = json.load(file)
    
    # Get the latest index
    try:
        latest_index = max(uri_to_index.values()) 
    except ValueError:
        latest_index = 0
    
    # Get the list of image files
    image_files = [f for f in os.listdir(dir_path) if f.endswith('.jpg')]
    image_files.sort(key=lambda x: int(x.split('_')[0]))

    # Index the image uri
    for image_file in image_files:
        latest_index += 1
        uri_to_index[image_file] = latest_index
    
    # Save the updated uri_to_index file
    with open(uri_to_index_file_path, 'w') as file:
        json.dump(uri_to_index, file)
    
    # Save the index_to_uri file
    index_to_uri = {v: k for k, v in uri_to_index.items()}
    with open(idex_to_uri_file_path, 'w') as file:
        json.dump(index_to_uri, file) 


if __name__ == "__main__":
    image_path = "src/app/static/image"    
    for _, dirs, _ in os.walk(image_path):
        dirs.sort()
        for video in dirs:
            for _, video_ids, _ in os.walk(os.path.join(image_path, video)):
                video_ids.sort()
                for video_id in video_ids:
                    dir_path = os.path.join(image_path, video, video_id)
                    print(dir_path)
                    image_uri_indexer(dir_path, 'src/app/static/data/uri_to_index.json', 'src/app/static/data/index_to_uri.json')
