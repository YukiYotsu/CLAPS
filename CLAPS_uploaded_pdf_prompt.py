# -*- coding: utf-8 -*-

import csv
from openai import OpenAI

CSV_PATH = ""
PDF_PATH - ""

API_KEY = "" # needs to set API_KEY, connecting via OpenAI's API
MODEL = "gpt-4.1-mini-2025-04-14" # which model is supposed to be in use

client = OpenAI(api_key=API_KEY)


with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

file = client.files.create(
    file=open(PDF_PATH, "rb"),
    purpose="user_data"
)

for i, row in enumerate(rows):
  english_text = row[0].strip() # text to be translated

  prompt = (
            f"Translate the following English sentence into Japanese. You'll be provided a PDF file of scientific papers in this conversation, so you may use it as contextual reference while translating. Do not use or refer to any other external information. Please note that this is not a summary task but just a translation task.\
            Requirements: - Return only the Japanese translation. - Do not add explanations, comments, notes, or the English source text. - Do not output empty lines or multiple lines.\
            English to translate: {english_text}\
            "
        )
  
  messages=[{
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": file.id,
                },
                {
                    "type": "input_text",
                    "text": prompt,
                },
            ]
        }]

  response = client.responses.create(
                  model=MODEL,
                  input=messages,
                  temperature=0.0,
              )