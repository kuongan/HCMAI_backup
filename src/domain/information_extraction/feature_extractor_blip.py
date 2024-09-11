from __future__ import annotations

import json
import os

import torch
from src.domain.information_extraction .feature_extractor import FeatureExtractor
from lavis.models import load_model_and_preprocess
from PIL import Image
from tqdm import tqdm


class FeatureExtractorBLIP(FeatureExtractor):
    def __init__(
        self,
        device='cuda',
        model_name='blip2',
        model_type='coco',
        batch_size=16,
    ):
        self.device = torch.device(device)
        self.model_name = model_name
        self.model_type = model_type
        self.batch_size = batch_size
        self.model, self.vis_processors, self.txt_processors = \
            load_model_and_preprocess(
                name=self.model_name,
                model_type=self.model_type,
                is_eval=True,
                device=self.device,
            )

    def embed_single_image(
        self,
        uri_image: str,

    ):
        try:
            image = Image.open(uri_image)
            image_processed = self.vis_processors['eval'](
                image,
            ).unsqueeze(0).to(self.device)
            image_features = self.model.extract_features(
                {'image': image_processed}, mode='image',
            )['image_embeds'][:, 0, :]
            return image_features
        except Exception as e:
            print(f'Error processing image {uri_image}: {e}')
            return None

    def embed_images(
        self,
        uri_images: list[str],
    ):
        embeddings = []
        for i in range(0, len(uri_images), self.batch_size):
            batch_uris = uri_images[i:i+self.batch_size]
            batch_images = []
            for uri in batch_uris:
                try:
                    image = Image.open(uri)
                    image_processed = self.vis_processors['eval'](
                        image,
                    ).unsqueeze(0).to(self.device)
                    batch_images.append(image_processed)
                except Exception as e:
                    print(f'Error loading image {uri}: {e}')
                    continue
            if not batch_images:
                continue
            batch_images = torch.cat(batch_images, dim=0)
            batch_features = self.model.extract_features(
                {'image': batch_images}, mode='image',
            )['image_embeds'][:, 0, :]
            # Move to CPU to save GPU memory
            embeddings.append(batch_features.cpu())
            del batch_images, batch_features  # Free memory
            torch.cuda.empty_cache()  # Clear cache

        if embeddings:
            # Combine all batches into one tensor
            return torch.cat(embeddings, dim=0)
        return None

    def embed_query(
        self,
        query: str,
    ):
        try:
            # Process the query string using the text processor
            query_processed = self.txt_processors['eval'](query)
            print(f"Processed query: {query_processed}")

            # Ensure the processed query is not None
            if query_processed is None:
                raise ValueError("Query processing returned None.")

            # Extract features using the model
            query_embedding = self.model.extract_features(
                {'text_input': query_processed}, mode='text'
            )['text_embeds'][:, 0, :]

            return query_embedding

        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            return None

    def embed_documents(
        self,
        documents: list[str],
    ):
        embeddings = []
        for doc in documents:
            try:
                doc_processed = self.txt_processors['eval'](
                    doc,
                ).unsqueeze(0).to(self.device)
                doc_embedding = self.model.extract_features(
                    {'text': doc_processed}, mode='text',
                )['text_embeds'][:, 0, :]
                # Move to CPU to save GPU memory
                embeddings.append(doc_embedding.cpu())
            except Exception as e:
                print(f'Error processing document {doc}: {e}')
                continue
        if embeddings:
            return torch.vstack(embeddings)
        return None

    def embed_to_json(
        self,
        keyframes_path,
        save_path,
    ):
        """
        Save the feature representations in the directory to JSON files.

        Args:
            keyframes_path (str): The directory containing the images.
            save_path (str): The directory where the JSON files will be saved.
        """
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Dictionary to hold video data
        video_data = {}

        for root, video_ids, _ in os.walk(keyframes_path):
            for video_id in tqdm(sorted(video_ids), desc='Processing videos'):
                video_path = os.path.join(root, video_id)
                uris = []
                metadata = []
                for _, _, frame_ids in os.walk(video_path):
                    for frame_id in tqdm(
                        sorted(frame_ids),
                        desc=f'Processing frames for video {video_id}',
                    ):
                        keyframe_path = os.path.join(video_path, frame_id)
                        uris.append(keyframe_path)
                        frame_parts = frame_id.split('_')
                        _position = frame_parts[-1].split('.')[0]
                        _frame_id = frame_parts[0]
                        metadata.append((_frame_id, _position))

                embeddings = self.embed_images(uris)
                if embeddings is not None:
                    data = []
                    for idx, (_frame_id, _position) in enumerate(metadata):
                        data.append({
                            'frame_id': _frame_id,
                            'position': _position,
                            'embedding': embeddings[idx].tolist(),
                        })

                    video_data = {
                        'video_id': video_id,
                        'data': data,
                    }

                    json_file_path = os.path.join(
                        save_path, f'{video_id}.json',
                    )
                    with open(json_file_path, 'w', encoding='utf-8') \
                            as f:
                        json.dump(
                            video_data, f,
                            ensure_ascii=False, indent=4,
                        )
                        print(f'Saved JSON embedding: {json_file_path}')