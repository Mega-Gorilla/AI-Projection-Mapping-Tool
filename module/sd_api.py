import base64
import requests
from PIL import Image
from io import BytesIO
import sys,os

try:
    # まず通常のインポートを試みる
    from config import config
except ImportError:
    current_script_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_script_path)
    parent_directory = os.path.dirname(current_directory)
    sys.path.append(parent_directory)
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
        filename = f'{config.sam_mask_output_path}/mask_image_{i}.png'
        image.save(filename)
        mask_file_list.append(filename)
    return mask_file_list

def img2img_dpth_api(prompt,ng_prompt,input_image_path,mask_image_path,batch_size=1,width=1920,height=1080,steps=30,cfg_scale=7,denoising_strength=0.6):
    url = config.server_address + "sdapi/v1/img2img"
    init_image = filename_to_base64(input_image_path).decode()
    mask = filename_to_base64(mask_image_path).decode()
    unit1 = {
        "image": init_image,
        "mask_image": None,
        "control_mode": "Balanced",
        "enabled": True,
        "generated_image": None,
        "guidance_end": 1,
        "guidance_start": 0,
        "pixel_perfect": True,
        "processor_res": 512,
        "resize_mode": "Crop and Resize",
        "threshold_a": 0.5,
        "threshold_b": 0.5,
        "weight": 1,
        "module": "depth_midas",
        "model": "diffusers_xl_depth_full [2f51180b]",
        "save_detected_map": False,
        "hr_option": "Both"
    }
    payload = {
        "alwayson_scripts": {"ControlNet": {"args": [unit1]}},
        "seed":-1,
        "batch_size": batch_size,
        "cfg_scale": cfg_scale,
        "comments": {},
        "denoising_strength": denoising_strength,
        "disable_extra_networks": False,
        "do_not_save_grid": False,
        "do_not_save_samples": False,
        "width": width,
        "height": height,
        "image_cfg_scale": 1.5,
        "init_images": [
            init_image
        ],
        "initial_noise_multiplier": 1,
        "inpaint_full_res": 0,
        "inpaint_full_res_padding": 32,
        "inpainting_fill": 1,
        "inpainting_mask_invert": 0,
        "mask": mask,
        "mask_blur": 4,
        "mask_blur_x": 4,
        "mask_blur_y": 4,
        "mask_round": True,
        "n_iter": 1,
        "negative_prompt": ng_prompt,
        "override_settings": {},
        "override_settings_restore_afterwards": True,
        "prompt": prompt,
        "resize_mode": 0,
        "restore_faces": False,
        "s_churn": 0,
        "s_min_uncond": 0,
        "s_noise": 1,
        "s_tmax": None,
        "s_tmin": 0,
        "sampler_name": "DPM++ 2M Karras",
        "script_args": [],
        "script_name": None,
        "seed": 1062019337,
        "seed_enable_extras": True,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        "steps": steps,
        "styles": [],
        "subseed": -1,
        "subseed_strength": 0,
        "tiling": False
        }
    
    print(F"generate Img:\nPrompt- {prompt}\nNG Prompt- {ng_prompt}")
    response = requests.post(url, json=payload)
    reply = response.json()
    img_file_list = []
    for i,item in zip(range(len(reply['images'])),reply['images']):
        image_data = base64.b64decode(item)
        image = Image.open(BytesIO(image_data))
        filename = f'{config.output_path}/output_image_{i}.png'
        image.save(filename)
        img_file_list.append(filename)
    return img_file_list

if __name__ == "__main__":
    image_data = img2img_dpth_api("best quality, masterpiece, ultra-detailed, 8k, high resolution, very aesthetic, absurdres,gorilla",
                                  "negativeXL_D,(worst quality:1.4),(low quality:1.4),(monochrome:1.3),(bad anatomy, bad hands:1.4),(watermark, username:1.2),lowres,text,error,missing fingers,extra digit,fewer digits,cropped,normal quality,jpeg artifacts,nsfw,, negativeXL_D,(worst quality:1.4),(low quality:1.4),(monochrome:1.3),(bad anatomy, bad hands:1.4),(watermark, username:1.2),lowres,text,error,missing fingers,extra digit,fewer digits,cropped,normal quality,jpeg artifacts,nsfw,",
                     "./images/i2i_image.jpg",
                     "./images/output/masks/output_image_0.png",
                     1)
    