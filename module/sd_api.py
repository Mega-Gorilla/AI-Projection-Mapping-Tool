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

def img2img_dpth_api(prompt,ng_prompt,input_image_path,mask_image_path,batch_size=1,width=1920,height=1080,steps=30,cfg_scale=7,denoising_strength=0.6):
    url = config.server_address + "sdapi/v1/img2img"
    init_image = filename_to_base64(input_image_path).decode()
    mask = filename_to_base64(mask_image_path).decode()
    payload = {
        "prompt": prompt,
        "negative_prompt": ng_prompt,
        "ControlNet": {"args": [{"batch_image_dir": "", "batch_input_gallery": [], "batch_mask_dir": "", "batch_mask_gallery": [], "control_mode": "Balanced", "enabled": True, "generated_image": None, "guidance_end": 1, "guidance_start": 0, "hr_option": "Both", "image": None, "input_mode": "simple", "mask_image": None, "model": "diffusers_xl_depth_full [2f51180b]", "module": "depth_midas", "pixel_perfect": True, "processor_res": 512, "resize_mode": "Crop and Resize", "save_detected_map": False, "threshold_a": 0.5, "threshold_b": 0.5, "use_preview_as_input": False, "weight": 1}]},
        "styles": [],
        "seed": -1,
        "subseed": -1,
        "subseed_strength": 0,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        "sampler_name": "DPM++ 2M Karras",
        "batch_size": batch_size,
        "n_iter": 1,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "width": width,
        "height": height,
        "restore_faces": True,
        "tiling": True,
        "do_not_save_samples": False,
        "do_not_save_grid": False,
        "eta": 0,
        "denoising_strength": denoising_strength,
        "s_min_uncond": 0,
        "s_churn": 0,
        "s_tmax": 0,
        "s_tmin": 0,
        "s_noise": 0,
        "override_settings": {},
        "override_settings_restore_afterwards": True,
        "disable_extra_networks": False,
        "comments": {},
        "init_images": [
            init_image
        ],
        "resize_mode": 1,
        "image_cfg_scale": 1.5,
        "mask": mask,
        "mask_blur_x": 4,
        "mask_blur_y": 4,
        "mask_blur": 4,
        "mask_round": True,
        "inpainting_fill": 1,
        "inpaint_full_res": True,
        "inpaint_full_res_padding": 32,
        "inpainting_mask_invert": 0,
        "initial_noise_multiplier": 1,
        "script_name": None,
        "script_args": [],
        "send_images": True,
        "save_images": False,
        "alwayson_scripts": {}
        }
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
    image_data = img2img_dpth_api("best quality, masterpiece, ultra-detailed, 8k, high resolution, very aesthetic, absurdres,gorilla","negativeXL_D,(worst quality:1.4),(low quality:1.4),(monochrome:1.3),(bad anatomy, bad hands:1.4),(watermark, username:1.2),lowres,text,error,missing fingers,extra digit,fewer digits,cropped,normal quality,jpeg artifacts,nsfw,, negativeXL_D,(worst quality:1.4),(low quality:1.4),(monochrome:1.3),(bad anatomy, bad hands:1.4),(watermark, username:1.2),lowres,text,error,missing fingers,extra digit,fewer digits,cropped,normal quality,jpeg artifacts,nsfw,",
                     "./images/i2i_image.jpg",
                     "./images/output/masks/output_image_0.png",
                     3)
    