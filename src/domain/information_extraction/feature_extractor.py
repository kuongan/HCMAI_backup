from __future__ import annotations
import json
import os

from langchain_experimental.open_clip import OpenCLIPEmbeddings


class FeatureExtractor:
    """
    Class representing a feature extractor for information extraction.
    Args:
        model_name (str, optional): The name of the model
            to use for embeddings.
        Defaults to 'ViT-B-32'.

        checkpoint (str, optional): The checkpoint to use for the model.
        Defaults to 'laion2b_s34b_b79k'.

        device (str, optional): The device to use for computation.
        Defaults to 'cpu'.
    Methods:
        embed_single_image(uri_image: str):
            Embeds a single image and returns its feature representation.
        embed_image(uri_images: list[str]):
            Embeds a list of images and returns their feature representations.
        embed_query(query: str) -> np.ndarray:
            Embeds a query string and returns its feature representation.
        embed_documents(documents: list[str]):
            Embeds a list of documents and returns
                their feature representations.
    """

    def __init__(
        self,
        model_name='ViT-B-32',
        checkpoint='laion2b_s34b_b79k',
        device='cpu',
    ):
        self.clipemd = OpenCLIPEmbeddings(model_name = model_name, 
                                          checkpoint = checkpoint,
                                          device= device)

    def embed_single_image(
        self,
        uri_image: str,
    ):
        """
        Embeds a single image and returns its feature representation.
        Args:
            uri_image (str): The URI of the image.
        Returns:
            np.ndarray: The feature representation of the image.
        """
        image_feature = self.clipemd.embed_image(uri_image)[0]
        return image_feature

    def embed_images(
        self,
        uri_images: list[str],
    ):
        """
        Embeds a list of images and returns their feature representations.
        Args:
            uri_images (list[str]): The URIs of the images.
        Returns:
            np.ndarray: The feature representations of the images.
        """
        images_feature = self.clipemd.embed_image(uri_images)
        return images_feature

    def embed_query(
        self,
        query: str,
    ):
        """
        Embeds a query string and returns its feature representation.
        Args:
            query (str): The query string.
        Returns:
            np.ndarray: The feature representation of the query.
        """
        query_feature = self.clipemd.embed_query(query)
        return query_feature

    def embed_documents(
        self,
        documents: list[str],
    ):
        """
        Embeds a list of documents and returns their feature representations.
        Args:
            documents (list[str]): The documents.
        Returns:
            np.ndarray: The feature representations of the documents.
        """
        documents_feature = self.clipemd.embed_documents(documents)
        return documents_feature

    def embed_to_json(self, keyframes_path, save_path):
        for root, video_ids, _ in os.walk(keyframes_path):
            for video_id in video_ids:
                video_path = os.path.join(root, video_id)
                uri = []
                metadata = []
                data = []
                for _, _, frame_ids in os.walk(video_path):
                    for frame_id in frame_ids:
                        keyframe_path = os.path.join(video_path, frame_id)
                        uri.append(keyframe_path)
                        frame_parts = frame_id.split('_')
                        _position = frame_parts[-1].split('.')[0]
                        _frame_id = frame_parts[0]
                        metadata.append((_frame_id, _position))
                embeddings = self.embed_images(uri)
                for idx, (_frame_id, _postion) in enumerate(metadata):
                    data.append(
                        {
                            'frame_id': _frame_id,
                            'position': _postion,
                            'embedding': embeddings[idx]
                        }
                    )
                json_data = {
                    'video_id': video_id,
                    'data': data
                }
                with open(os.join(save_path, f'{video_id}.json'), 'w') as f:
                    json.dump(json_data, f, indent=4)

clip = FeatureExtractor()