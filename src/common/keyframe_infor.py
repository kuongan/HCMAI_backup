import os
import csv

def extract_info_from_filename(filename):
    # Tách filename và bỏ đuôi .jpg
    name_parts = filename.replace('.jpg', '').split('_')
    if len(name_parts) == 4:
        frame_id = name_parts[0]
        video_id = f"{name_parts[1]}_{name_parts[2]}"
        position = name_parts[3]
        return frame_id, video_id, position
    return None

def traverse_and_save_to_csv(folder_path, output_csv):
    counter = 1
    data = []

    # Duyệt qua các thư mục và file trong folder_path
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.jpg'):
                result = extract_info_from_filename(file)
                if result:
                    frame_id, video_id, position = result
                    data.append([counter, frame_id, video_id, position])
                    counter += 1
    
    # Lưu vào file CSV
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'frame_id', 'video_id', 'position'])  # Ghi tiêu đề cột
        writer.writerows(data)  # Ghi dữ liệu

# Đường dẫn đến folder và file CSV
folder_path = r'C:\Users\User\hcmaic\HCMAI_backup\src\app\static\image'  # Thay đổi đường dẫn đến folder chứa các video
output_csv = r'C:\Users\User\hcmaic\HCMAI_backup\src\app\static\data\keyframe_info.csv'

# Gọi hàm để duyệt qua thư mục và lưu vào CSV
traverse_and_save_to_csv(folder_path, output_csv)