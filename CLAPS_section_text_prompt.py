# -*- coding: utf-8 -*-

import csv
import json
import os
import re
import base64 # to encode images in paper with Base64
from openai import OpenAI

CSV_PATH = ""
RESOURCE_PATH = "" # path where the section-segmented text data from paper is saved

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
    
# 表や図の言及（mention）を文字列中から抽出
def extract_fig_table_numbers(text: str):
    """
    正規表現により、特定のtxtから図表番号の言及を検出。
    sim内テキストから Figure 1 / Figure-1 / Figure- 1 のみ抽出。
    fig1, f1, figure1 は不可。

    variables:
        text: 対象テキスト
        pattern: 見つけたい内容を正規表現で表したもの
    """
    pattern = r"(Figure[\s-]*\d+|Table[\s-]*\d+)"
    return list(set(re.findall(pattern, text)))

# その番号に一致するファイル名を IMAGE_DIR から探す
def find_matching_images(label, image_dir):
    """
    正規表現により図表番号に一致するファイル名を指定ディレクトリから探し、リストにして返す。
    
    variables:
        label: "Table 7" or "Figure 2" のような文字列
        mage_dir: 画像ディレクトリ
    """

    # "Table 7" → ("Table", "7")
    match = re.match(r"(Table|Figure)\s*(\d+)", label, re.IGNORECASE)
    if not match:
        return []

    kind, num = match.group(1).capitalize(), match.group(2)
    pattern = re.compile(rf"\.{kind}{num}(_.*)?\.png$", re.IGNORECASE)

    return [
        os.path.join(image_dir, f)
        for f in os.listdir(image_dir)
        if pattern.search(f)
    ]
    

with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
        

sim_text = "" # Has a section-segmented quote from paper
encoded_images = [] # needs to list clipped pictures along figures and tables only MENTIONED within the corresponding section-segmented text


for i, row in enumerate(rows):
  english_text = row[0].strip() # text to be translated

  prompt = (f"Translate the following English sentence into Japanese. You may refer to the provided text and images which are extracted from the relevant scientific paper. Please note that this is not a summary task but just a translation task.\
        Requirements: - Return only the Japanese translation. - Do not add explanations, comments, notes, or the English source text. - Do not output empty lines or multiple lines.\
         \
         \
            English to translate: {english_text}\
            Text from scientific papers: {sim_text}\
            "
        )
  
  messages=[{
            "role": "user",
            "content": [{
                    "type": "input_text",
                    "text": prompt,
                },
  ]}]
  
  for b64 in encoded_images:
            messages[0]["content"].insert(
                0,
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"}
            )

            print("1 image added to prompt")

  response = client.responses.create(
                  model=MODEL,
                  input=messages,
                  temperature=0.0,
              )