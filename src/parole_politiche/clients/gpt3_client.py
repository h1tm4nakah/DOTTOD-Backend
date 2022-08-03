import openai as gpt3
import os
import re


class GPT3Client(object):
    gpt3.api_key = os.getenv("OPENAI_API_KEY", "")
    completion = gpt3.Completion()

    @staticmethod
    def get_translation(prompt: str):
        response = GPT3Client.completion.create(
            prompt=prompt + "\ntranslate italian to english.",
            engine="text-davinci-002",
            temperature=0.3,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        return re.sub('\n', '', response["choices"][0]["text"])
