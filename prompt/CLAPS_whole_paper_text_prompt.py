# -*- coding: utf-8 -*-

import csv
import base64 # to encode images in paper with Base64
from openai import OpenAI

CSV_PATH = ""
RESOURCE_PATH = "" # path where the whole text from paper is saved

API_KEY = "" # needs to set API_KEY, connecting via OpenAI's API
MODEL = "gpt-4.1-mini-2025-04-14" # which model is supposed to be in use

client = OpenAI(api_key=API_KEY)


def encode_image(image_path: str) -> str:
    """
    Encode an image file as a Base64 string.

    Args:
        image_path (str):
            Path to the image file.

    Returns:
        str:
            Base64-encoded representation of the image.

    Notes:
        The returned string can be embedded in a data URL and
        passed to the OpenAI API as image input.
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
    

with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

with open(RESOURCE_PATH, "r", encoding="utf-8") as f2:
        text = f2.read()


encoded_images_list = [] # needs to list all the clipped pictures along figures and tables in paper


for i, row in enumerate(rows):
  english_text = row[0].strip() # text to be translated

  prompt = (f"Translate the following English sentence into Japanese. You'll be provided text/images extracted from scientific papers in this conversation, so you may use it as contextual reference while translating. Do not use or refer to any other external information. Please note that this is not a summary task but just a translation task.\
            Requirements: - Return only the Japanese translation. - Do not add explanations, comments, notes, or the English source text. - Do not output empty lines or multiple lines.\
            English to translate: {english_text}\
            "
            )
  
  final_content = []
  
  # append all the clipped pictures along figures and tables in paper
  for b64 in encoded_images_list:
                final_content.append({
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{b64}",
                })
  
  # append the whole text extracted from paper             
  final_content.append({
                "type": "input_text",
                "text": text,
            })
  
  # append prompt
  final_content.append({
                "type": "input_text",
                "text": prompt,
            })
  
  messages = [{
                "role": "user",
                "content": final_content
            }]

  response = client.responses.create(
                  model=MODEL,
                  input=messages,
                  temperature=0.0,
              )