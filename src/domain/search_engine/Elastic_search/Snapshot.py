from elasticsearch import Elasticsearch

# Kết nối với Elasticsearch
es = Elasticsearch("http://localhost:9200")

# 1. Tạo repository để lưu trữ snapshot trên ổ E:
repository_settings = {
    "type": "fs",
    "settings": {
        "location": "E:\\backup_elastic",  # Thư mục trên ổ E:\ để lưu snapshot
        "compress": True
    }
}

# Tạo repository với tên 'my_backup'
es.snapshot.create_repository(name="my_backup", repository=repository_settings)

# 2. Tạo snapshot cho index 'ocr_index'
snapshot_body = {
    "indices": "ocr_index",  # Tên index cần sao lưu
    "ignore_unavailable": True,
    "include_global_state": False
}

# Tạo snapshot với tên 'ocr_snapshot' trong repository 'my_backup'
es.snapshot.create(repository="my_backup", snapshot="ocr_snapshot", body=snapshot_body, wait_for_completion=True)

# 3. Kiểm tra danh sách các snapshot trong repository 'my_backup'
snapshots = es.snapshot.get(repository="my_backup", snapshot="_all")
print("Available Snapshots:")
for snap in snapshots['snapshots']:
    print(f"Snapshot: {snap['snapshot']}, State: {snap['state']}")

# 4. Phục hồi snapshot 'ocr_snapshot' (nếu cần)
restore_body = {
    "indices": "ocr_index",  # Tên index cần phục hồi
    "ignore_unavailable": True,
    "include_global_state": False,
    "allow_no_indices": True,
    "rename_pattern": "ocr_index",
    "rename_replacement": "restored_ocr_index"  # Tên mới cho index được phục hồi
}

# Phục hồi snapshot với tên 'ocr_snapshot'
es.snapshot.restore(repository="my_backup", snapshot="ocr_snapshot", body=restore_body, wait_for_completion=True)

print("Snapshot restored successfully.")
