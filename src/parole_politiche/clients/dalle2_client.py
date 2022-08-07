from dalle2 import Dalle2
from pyuploadcare import Uploadcare, File
import os
from parole_politiche.models.exhibition import Piece
from parole_politiche import db
from typing import List


class Dalle2Client(object):
    dalle_api_key = os.getenv("DALLE2_API_KEY", "")
    uploadcare_public_api_key = os.getenv("UPLOADCARE_PUBLIC_KEY", "mock_key")
    uploadcare_private_api_key = os.getenv("UPLOADCARE_SECRET_KEY", "")
    dalle = Dalle2(dalle_api_key)
    uploadcare = Uploadcare(public_key=uploadcare_public_api_key, secret_key=uploadcare_private_api_key)

    @staticmethod
    def generate_image_and_store(piece: Piece):
        if piece.input_translated is None:
            return
        print(f"Generating images for {piece} with prompt {piece.input_translated}")
        generations = Dalle2Client.dalle.generate(piece.input_translated)
        print(generations)
        ucare_urls: List[str] = []
        for generation in generations:
            image_path = generation['generation']['image_path']
            ucare_url: File = Dalle2Client.uploadcare.upload(image_path)
            ucare_urls.append(ucare_url)

        print(ucare_urls)
        assert(len(ucare_urls) == 4)
        piece.artifact_url_1 = ucare_urls[0]
        piece.artifact_url_2 = ucare_urls[1]
        piece.artifact_url_3 = ucare_urls[2]
        piece.artifact_url_4 = ucare_urls[3]

        db.session.commit()

    @staticmethod
    def generate_image(piece: Piece):
        if piece.input_translated is None:
            return
        print(f"Generating images for {piece} with prompt {piece.input_translated}")
        generations = []
        try:
            generations = Dalle2Client.dalle.generate(piece.input_translated)
        except Exception as e:
            print(f"Something went wrong when generating images {e}")

        print(generations)
        ucare_urls: List[str] = []
        for generation in generations:
            image_path = generation['generation']['image_path']
            ucare_url: File = Dalle2Client.uploadcare.upload(image_path)
            ucare_urls.append(ucare_url)

        print(ucare_urls)
        assert(len(ucare_urls) == 4)

        return ucare_urls