from __future__ import annotations

import glob
import json
import os
import sys
import torch
import faiss
import numpy as np
from tqdm import tqdm


os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'


class FaissDatabase:
    def __init__(self):
        self.indexes = {}
        self.dimensions = {}
        self.metadata = {}

    def indexer(self, name, dimension):
        if name in self.indexes:
            raise ValueError(f'Index với tên {name} đã tồn tại.')
        self.dimensions[name] = dimension
        # Inner Product index
        self.indexes[name] = faiss.IndexFlatIP(dimension)
        self.metadata[name] = []

    def create_database(self, directory_path, model_name):
        if model_name not in self.indexes:
            raise ValueError(f'Index với tên {model_name} chưa được tạo.')

        vectors = []
        meta_info = []

        json_files = sorted(
            glob.glob(
                os.path.join(
                    directory_path, '**', '*.json',
                ), recursive=True,
            ),
        )

        for json_file in json_files:
            with open(json_file) as f:
                data = json.load(f)

                for entry in data['data']:
                    vectors.append(entry['embedding'])
                    meta_info.append({
                        'video_id': data['video_id'],
                        'frame_id': entry['frame_id'],
                        'position': entry['position'],
                    })

        vectors = np.array(vectors, dtype=np.float32)

        # Thêm vectors vào index
        for vector in tqdm(vectors, desc=f'Indexing for {model_name}'):
            self.indexes[model_name].add(np.expand_dims(vector, axis=0))

        # Lưu metadata
        self.metadata[model_name].extend(meta_info)

    def save_index(self, name, path):
        if name not in self.indexes:
            raise ValueError(f'Index with name {name} does not exist.')

        if not os.path.isdir(os.path.dirname(path)):
            raise FileNotFoundError(
                f'Directory does not exist: {os.path.dirname(path)}',
            )

        if not path.endswith('.index'):
            path = path + '.index'

        try:
            faiss.write_index(self.indexes[name], path)
            print(f'Index saved to {path}')
            metadata_path = path.replace('.index', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(self.metadata[name], f)
            print(f'Metadata saved to {metadata_path}')
        except Exception as e:
            print(f'Failed to save index: {e}')

    def load_index(self, name, path):
        self.indexes[name] = faiss.read_index(path)

        self.dimensions[name] = self.indexes[name].d

        metadata_path = path.replace('.index', '_metadata.json')
        try:
            with open(metadata_path) as f:
                self.metadata[name] = json.load(f)
            print(f'Metadata loaded from {metadata_path}')
        except FileNotFoundError:
            print(
                f'Metadata file not found at {metadata_path}.',
            )
            self.metadata[name] = []

        print(f'Index {name} đã được tải từ {path}')

    def search(self, name, query_vector, k=5):
        if name not in self.indexes:
            raise ValueError(f'Index với tên {name} không tồn tại.')

        # Check if query_vector is a tensor (assumes PyTorch)
        if isinstance(query_vector, torch.Tensor):
            query_vector = query_vector.cpu().numpy()  # Convert tensor to NumPy
        elif isinstance(query_vector, list):
            query_vector = np.array(query_vector)
        # Check if query_vector is 1D or 2D, and reshape if needed
        if query_vector.ndim == 1:
            # If 1D, reshape to (1, d)
            query_vector = np.expand_dims(query_vector, axis=0)
        elif query_vector.ndim != 2:
            raise ValueError(f'Query vector has an unexpected number of dimensions: {query_vector.ndim}')

        print(f'Query vector shape: {query_vector.shape}')  # Debug print

        print(f'Number of entries for {name}: {len(self.metadata[name])}')
        print(self.dimensions[name])

        # Ensure the query vector has the correct dimensions
        if query_vector.shape[1] != self.dimensions[name]:
            raise ValueError(
                f'Query vector has wrong dimensions. \
        Expected {self.dimensions[name]}, but got {query_vector.shape[1]}.',
            )

        distances, indices = self.indexes[name].search(query_vector, k)

        results = []
        for i in range(k):
            idx = indices[0][i]
            result = self.metadata[name][idx]
            result['distance'] = distances[0][i]
            results.append(result)

        return results