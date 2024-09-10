from __future__ import annotations

import glob
import json
import os

from elasticsearch import Elasticsearch
from tqdm import tqdm


class ElasticSearch:
    """
    Class representing an interface for interacting with Elasticsearch,
    specifically for indexing and searching ASR (Automatic Speech Recognition)
    and OCR (Optical Character Recognition) data.

    Args:
        host (str, optional): The hostname of the Elasticsearch server.
            Defaults to 'localhost'.
        port (int, optional): The port of the Elasticsearch server.
            Defaults to 9200.

    Methods:
        indexer(index_name: str):
            Creates an index in Elasticsearch with the given index_name.
        add_asr(data_path: str, index_name: str):
            Indexes ASR data in data_path into the specified index.
        add_ocr(data_path: str, index_name: str):
            Indexes OCR data in data_path into the specified index.
        add_color(data_path, index_name:str):
            Indexes Color data in data_path into the specified index.
        add_object(data_path, index_name:str):
            Indexes object detection data into the specified index.
        search(index_name: str, query: str, topk: int):
            Searches the specified index for documents matching the query
                and returns the top 'topk' results.

        delete_index(index_name: str):
            Deletes the specified index from Elasticsearch.
    """

    def __init__(self, host='localhost', port=9200):
        """
        Initializes the ElasticSearch object and attempts to
        connect to the Elasticsearch server.
        """
        try:
            self.client = Elasticsearch(
                [{'host': host, 'port': port, 'scheme': 'http'}],
            )
            if not self.client.ping():
                raise ConnectionError('Could not connect to Elasticsearch')
            print('Connected to Elasticsearch')
        except ConnectionError as e:
            print(f'Error connecting to Elasticsearch: {e}')
            self.client = None

    def indexer(self, index_name):
        """
        Creates an index in Elasticsearch with the given index_name.
        Deletes the index if it already exists.

        Args:
            index_name (str): The name of the index to create.
        """
        if not self.client:
            print('No Elasticsearch client available')
            return

        es_client = self.client
        number_of_shards = 1
        es_params = {
            'settings': {
                'index': {
                    'number_of_shards': number_of_shards,
                    'number_of_replicas': 1,
                },
            },
        }
        if es_client.indices.exists(index=index_name):
            es_client.indices.delete(index=index_name)
        es_client.indices.create(index=index_name, body=es_params)

    def add_asr(self, data_path, index_name):
        """
        Indexes ASR (Automatic Speech Recognition) data
        from JSON files into Elasticsearch.

        Args:
            data_path (str): The path to the dir containing ASR JSON files.
            index_name (str): The name of the index to add the ASR data to.
        """
        if not self.client:
            print('No Elasticsearch client available')
            return
        asr_files = sorted(glob.glob(os.path.join(data_path, '*.json')))
        id_counter = 0
        for file in tqdm(asr_files):
            try:
                with open(file, encoding='utf-8') as json_file:
                    data = json.load(json_file)
            except UnicodeDecodeError as e:
                print(f'Error decoding {file}: {e}')
                continue

            video_id = os.path.basename(file).split('.')[0]
            segments = data.get('segments', [])
            for segment in segments:
                groups = segment.get('group', [])
                if not groups:
                    continue

                # Chọn keyframe ở giữa danh sách group
                mid_index = len(groups) // 2
                keyframe = groups[mid_index]
                frames_and_positions = [
                    {
                        'frame_id': f'{group["frame_id"]}',
                        'position': group['position'],
                    } for group in groups
                ]
                try:
                    response = self.client.index(
                        index=index_name,
                        id=id_counter,
                        document={
                            'frame': f'{keyframe["frame_id"]}',
                            'video_id': f'{video_id}',
                            'text': segment['text'],
                            'trans_text': segment['translate'],
                            'position': keyframe['position'],
                            'frames_and_positions': frames_and_positions,
                        },
                    )
                    if response['result'] == 'created':
                        pass
                        # print(f'Document {id_counter} ingested successfully')
                    else:
                        print(f'Document {id_counter} ingestion failed.')
                    id_counter += 1
                except Exception as e:
                    print(f'Error indexing document {file}: {e}')
                    continue

    def add_ocr(self, data_path, index_name):
        """
        Indexes OCR (Optical Character Recognition) data
        from JSON files into Elasticsearch.

        Args:
            data_path (str): The path to the dir containing OCR JSON files.
            index_name (str): The name of the index to add the OCR data to.
        """
        if not self.client:
            print('No Elasticsearch client available')
            return

        ocr_files = sorted(
            glob.glob(
                os.path.join(
                    data_path, '**', '*.json',
                ), recursive=True,
            ),
        )
        id_counter = 0
        for file in tqdm(ocr_files):
            try:
                with open(file, encoding='utf-8') as json_file:
                    # Lấy toàn bộ nội dung file JSON
                    data_list = json.load(json_file)
            except UnicodeDecodeError as e:
                print(f'Error decoding {file}: {e}')
                continue

            # Kiểm tra nếu dữ liệu là một danh sách
            if isinstance(data_list, list):
                for data in data_list:
                    groups = data.get('groups', {})
                    for group_id, text_list in groups.items():
                        group_text = ' '.join(text_list)
                        try:
                            response = self.client.index(
                                index=index_name,
                                id=id_counter,
                                document={
                                    'video_id': data['video_id'],
                                    'frame': data['frame_id'],
                                    'position': data['position'],
                                    'group_id': group_id,
                                    'text': group_text,
                                },
                            )
                            if response['result'] == 'created':
                                pass
                            else:
                                print(
                                    f'Document {id_counter} ingestion failed.',
                                )
                            id_counter += 1
                        except Exception as e:
                            print(f'Error indexing document {file}: {e}')
                            continue
            else:
                print(f'Unexpected data format in file {file}')

    def add_color(self, data_path, index_name):
        if not self.client:
            print('No Elasticsearch client available')
            return
        color_files = sorted(glob.glob(os.path.join(data_path, '**', '*.json')))
        id_counter = 0
        for file in tqdm(color_files):
            try:
                with open(file, encoding='utf-8') as json_file:
                    data = json.load(json_file)
            except UnicodeDecodeError as e:
                print(f'Error decoding {file}: {e}')
                continue
            for item in data:
                image_name = item.get('image_name', '')
                if not image_name:
                    print(f'No image_name found in {file}')
                    continue
                parts = image_name.split('_')
                if len(parts) < 3:
                    print(f'Unexpected image_name format in {file}')
                    continue
                frame_id = parts[0]
                video_id = '_'.join(parts[1:3])
                position = parts[3].split('.')[0]
                object_class_names = item.get('object_class_names', {})
                encoded_color_location = item.get('encoded_color_location', '')
                try:
                    response = self.client.index(
                        index=index_name,
                        id=id_counter,
                        document={
                            'frame_id': frame_id,
                            'video_id': video_id,
                            'position': position,
                            'object_class_names': object_class_names,
                            'encoded_color_location': encoded_color_location,
                        },
                    )
                    if response['result'] == 'created':
                        pass
                    else:
                        print(f'Document {id_counter} ingestion failed.')
                    id_counter += 1
                except Exception as e:
                    print(f'Error indexing document {file}: {e}')
                    continue

    def add_object(self, data_path, index_name):
        if not self.client:
            print('No Elasticsearch client available')
            return

        id_counter = 0
        # Loop through all JSON files in the provided directory
        data_files = sorted(
            glob.glob(
                os.path.join(
                    data_path, '**', '*.json',
                ), recursive=True,
            ),
        )
        for file in data_files:
            if file.endswith('.json'):
                file_path = os.path.join(data_path, file)
                print(file_path)
                with open(file_path, encoding='utf-8') as jsonfile:
                    data = json.load(jsonfile)

                for frame in tqdm(data.get('frames', [])):
                    video_id = data.get('video_id', '')
                    frame_id = frame.get('frame_id', '')
                    position = frame.get('position', '')

                    for obj in frame.get('object', []):
                        # Truy xuất label_name cuối cùng
                        final_label_name = obj.get('label_name', '')
                        # Retrieve the count before moving to the super_class
                        count = obj.get('count', 0)
                        while 'super_class' in obj:
                            obj = obj['super_class']
                            final_label_name = obj.get(
                                'label_name', final_label_name,
                            )
                        if not video_id or not frame_id:
                            print(
                                'Skipping frame with \
                                missing video_id or frame_id.',
                            )
                            continue
                        document = {
                            'video_id': video_id,
                            'frame_id': frame_id,
                            'position': position,
                            'object': {
                                'label_name': final_label_name,
                                'count': int(count),
                            },
                        }

                        try:
                            response = self.client.index(
                                index=index_name,
                                id=id_counter,
                                document=document,
                            )
                            if response['result'] == 'created':
                                pass
                            else:
                                print(
                                    f'Document {id_counter} ingestion failed.',
                                )
                            id_counter += 1
                        except Exception as e:
                            print(f'Error indexing document {id_counter}: {e}')
                            continue

    def search_asr(self, index_name, query, topk):
        """
        Searches the specified index for documents matching the query.

        Args:
            index_name (str): The name of the index to search.
            query (str): The search query string.
            topk (int): The number of top results to return.

        Returns:
            list: A list of search hits (results).
        """
        if not self.client:
            print('No Elasticsearch client available')
            return []
        search_query = {
            'size': topk,
            'query': {
                'bool': {
                    'should': [
                        {
                            'multi_match': {
                                'query': query,
                                'fields': ['text', 'trans_text'],
                                'fuzziness': 'AUTO',
                            },
                        },
                        {'wildcard': {'text': f'*{query}*'}},
                        {'wildcard': {'trans_text': f'*{query}*'}},
                    ],
                },
            },
        }
        search_results = self.client.search(
            index=index_name, body=search_query,
        )
        hits = search_results['hits']['hits']
        results = []
        for hit in hits:
            video_id = hit['_source']['video_id']
            frames_and_positions = hit['_source']['frames_and_positions']
            for item in frames_and_positions:
                results.append({
                    'frame_id': item['frame_id'],
                    'video_id': video_id,
                    'position': item['position'],
                })

        return results

    def search_color(self, index_name, query, topk):
        if not self.client:
            print('No Elasticsearch client available')
            return []
        search_query = {
            'size': topk,
            'query': {
                'bool': {
                    'should': [
                        {
                            'multi_match': {
                                'query': query,
                                'fields': [
                                    'encoded_color_location',
                                    'object_class_names',
                                ],
                            },
                        },
                        {'wildcard': {'encoded_color_location': f'*{query}*'}},
                        {'wildcard': {'object_class_names': f'*{query}*'}},
                    ],
                },
            },
        }
        search_results = self.client.search(
            index=index_name, body=search_query,
        )
        hits = search_results['hits']['hits']
        results = []
        for hit in hits:
            frame_id = hit['_source']['frame_id']
            video_id = hit['_source']['video_id']
            position = hit['_source']['position']
            results.append({
                'frame_id': frame_id,
                'video_id': video_id,
                'position': position,
            })

        return results

    def search_ocr(self, index_name, query, topk):
        if not self.client:
            print('No Elasticsearch client available')
            return []
        search_query = {
            'size': topk,
            'query': {
                'bool': {
                    'should': [
                        {
                            'match': {
                                'text': {
                                    'query': query,
                                    'fuzziness': 'AUTO',
                                },
                            },
                        },
                        {'wildcard': {'text': f'*{query}*'}},
                    ],
                },
            },
        }

        search_results = self.client.search(
            index=index_name, body=search_query,
        )
        hits = search_results['hits']['hits']
        results = []
        for hit in hits:
            frame_id = hit['_source']['frame']
            video_id = hit['_source']['video_id']
            position = hit['_source']['position']
            results.append({
                'frame_id': frame_id,
                'video_id': video_id,
                'position': position,
            })

        return results

    def search_od(self, index_name, query, min_count, max_count, topk):
        if not self.client:
            print('No Elasticsearch client available')
            return []

        search_query = {
            'size': topk,
            'query': {
                'bool': {
                    'must': [
                        {
                            'match': {
                                'object.label_name': query,
                            },
                        },
                        {
                            'range': {
                                'object.count': {
                                    'gte': min_count,
                                    'lte': max_count,
                                },
                            },
                        },
                    ],
                },
            },
        }

        search_results = self.client.search(
            index=index_name, body=search_query,
        )
        hits = search_results['hits']['hits']
        results = []
        for hit in hits:
            video_id = hit['_source']['video_id']
            frame_id = hit['_source']['frame_id']
            position = hit['_source']['position']
            results.append({
                'video_id': video_id,
                'frame_id': frame_id,
                'position': position,
            })

        return results

    def delete_index(self, index_name):
        """
        Deletes the specified index from Elasticsearch.

        Args:
            index_name (str): The name of the index to delete.
        """
        if not self.client:
            print('No Elasticsearch client available')
            return

        if self.client.indices.exists(index=index_name):
            self.client.indices.delete(index=index_name)

    def count_documents(self, index_name):
        if not self.client:
            print('No Elasticsearch client available')
            return 0
        try:
            count = self.client.count(index=index_name)['count']
            print(f'Total documents in "{index_name}": {count}')
            return count
        except Exception as e:
            print(f'Error counting documents in "{index_name}": {e}')
            return 0


es = ElasticSearch(host='localhost', port=9200)
