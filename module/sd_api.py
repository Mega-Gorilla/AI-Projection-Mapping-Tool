import base64
import requests
from PIL import Image
from io import BytesIO
from config import config

def filename_to_base64(filename):
    with open(filename, "rb") as fh:
        return base64.b64encode(fh.read())
    
def sam_predict(image_path,prompt,dino_enabled=True,dino_preview_checkbox=False):
    url = config.server_address + "sam/sam-predict"

    payload = {
        "input_image": filename_to_base64(image_path).decode(),
        "dino_enabled": dino_enabled,
        "dino_text_prompt": prompt,
        "dino_preview_checkbox": dino_preview_checkbox,
    }
    response = requests.post(url, json=payload)
    reply = response.json()
    mask_file_list = []
    for i,item in zip(range(len(reply['masks'])),reply['masks']):
        image_data = base64.b64decode(item)
        image = Image.open(BytesIO(image_data))
        filename = f'{config.sam_mask_output_path}/output_image_{i}.png'
        image.save(filename)
        mask_file_list.append(filename)
    return mask_file_list