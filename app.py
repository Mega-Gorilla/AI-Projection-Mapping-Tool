import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import threading
import av
import cv2
import numpy as np
from module.display import display_module
from module.clip_image import clip_image
from module.sd_api import sam_predict,img2img_dpth_api
from config import config
import os,time

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class VideoTransformer(VideoProcessorBase):
    """
    webrtc streamer 関数
    """
    frame_lock: threading.Lock  # フレームを安全に保持するためのロック
    out_frame: np.ndarray  # 出力フレームを保持する

    def __init__(self) -> None:
        self.frame_lock = threading.Lock()
        self.out_frame = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # 画像に対する処理をここに記述
        # 例: グレースケール変換
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        with self.frame_lock:
            self.out_frame = img.copy()

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def delete_png(folder_path):
    for filename in os.listdir(folder_path):
        # ファイルの拡張子が.pngであるかを確認
        if filename.endswith(".png"):
            # ファイルのフルパスを取得
            file_path = os.path.join(folder_path, filename)
            # ファイルが存在するかを確認
            if os.path.isfile(file_path):
                # ファイルを削除
                os.remove(file_path)
def initialize():
    if 'display_num' not in st.session_state:
        st.session_state.display_num = 1
    if 'display_size' not in st.session_state:
        st.session_state.display_size = None
    if 'mask_color' not in st.session_state:
        st.session_state.mask_color = '#008000'
    if 'display_thread' not in st.session_state:
        st.session_state.display_thread = None
    if 'display_module' not in st.session_state:
        st.session_state.display_module = display_module()
    if 'clip_module' not in st.session_state:
        st.session_state.clip_module = clip_image()
    if 'clip_position' not in st.session_state:
        st.session_state.clip_position = None
    if 'prompts' not in st.session_state:
        st.session_state.prompts = ""
    if 'negative_prompts' not in st.session_state:
        st.session_state.negative_prompts = ""
    if 'dino_prompts' not in st.session_state:
        st.session_state.dino_prompts = ""
    if 'mask_path_list' not in st.session_state:
        st.session_state.mask_path_list = None
    if 'mask_path' not in st.session_state:
        st.session_state.mask_path = "./images/output/masks/output_image_0.png"
    if 'image_path_list' not in st.session_state:
        st.session_state.image_path_list = None
    if 'image_path' not in st.session_state:
        st.session_state.image_path = "./images/output/output_image_0.png"
    if 'draw_image_path' not in st.session_state:
        st.session_state.draw_image_path = None

def main():
    initialize()
    # 画面情報取得
    display = st.session_state.display_module
    clip_module = st.session_state.clip_module
    monitors_info = display.get_monitors_info()
    st.header("Step1. プロジェクターディスプレイの選択",divider=True)
    st.markdown("プロジェクターが接続されているディスプレイ番号および解像度を選択してください。")
    col1,col2=st.columns(2)
    with col1:
        st.session_state.display_num = int(st.selectbox('Set display num',tuple(d['num'] for d in monitors_info),label_visibility='collapsed',index=st.session_state.display_num-1))
    with col2:
        st.session_state.display_size = st.selectbox('Set Display Size',tuple(f"{display['width']}x{display['height']}" for display in monitors_info),label_visibility='collapsed')

    st.header("Step2. プロジェクタの描画を開始する",divider=True)
    col1,col2,col3,col4=st.columns(4)
    with col1:
        if st.button("プロジェクタ ON",type="primary") and st.session_state.display_thread ==None:
            image_path = './images/smpte_color_bars.png'
            st.session_state.display_thread = threading.Thread(target=display.display_fullscreen_image,
                                            args=(st.session_state.display_num-1, image_path, True))
            st.session_state.display_thread.start()
    if st.session_state.display_thread != None:
        with col2:
            if st.button("暗転"):
                resolution_list = [int(number) for number in st.session_state.display_size.split('x')]
                display.create_image(resolution_list[0],resolution_list[1],'#000000','./images/black_BG.png')
                display.update_image_path('./images/black_BG.png',False)
        with col3:
            if st.button("カラーバー"):
                image_path = './images/smpte_color_bars.png'
                display.update_image_path(image_path,True)
        with col4:
            if st.button("プロジェクタ OFF"):
                display.pygame_quit()
                st.session_state.display_thread.join()
                st.session_state.display_thread = None
    
    if st.session_state.display_thread == None:
        return
    st.header("Step3. イメージサイズ調節",divider=True)
    with st.expander("Step3. イメージサイズ調節",True):
        st.markdown('Webカメラとプロジェクター描画サイズの同期を行います。')
        st.markdown('1.マスクカラーを設定後、調整マスクをスクリーンに表示してください。マスクが画面全体に適応されない場合画面サイズを調整する必要があります。')
        col1,col2 = st.columns(2)
        with col1:
            initialize_BG_color = st.color_picker('1.マスクカラー設定',st.session_state.mask_color,label_visibility="collapsed")
        with col2:
            if st.button("調整マスクを表示する",type='primary'):
                resolution_list = [int(number) for number in st.session_state.display_size.split('x')]
                display.create_image(resolution_list[0],resolution_list[1],initialize_BG_color,'./images/initialize_BG.png')
                display.update_image_path('./images/initialize_BG.png',False)
        
        st.markdown("2.Webカメラ画像の撮影")
        cropped_image_path = './images/cropped_image.jpg'
        webrtc_ctx = webrtc_streamer(key="initialize_cam",
                                    video_processor_factory=VideoTransformer,
                                    rtc_configuration=RTC_CONFIGURATION,
                                    sendback_audio=False,
                                    media_stream_constraints={"video": {"width": 1920, "height": 1080}, "audio": False})
        if webrtc_ctx.video_processor:
            if st.button("スクリーンショットを撮影する"):
                with webrtc_ctx.video_processor.frame_lock:
                    if webrtc_ctx.video_processor.out_frame is not None:
                        st.image(webrtc_ctx.video_processor.out_frame, channels="BGR", caption="スクリーンショット")
                        cv2.imwrite(cropped_image_path, webrtc_ctx.video_processor.out_frame)  # 画像を保存
        if webrtc_ctx.video_processor:
            if st.button("プロジェクタ投影範囲を切り抜く"):
                st.session_state.clip_position = clip_module.main(cropped_image_path) #切り抜き座標を記録
    
    if st.session_state.clip_position == None:
        return
    st.header("Step4. image to image 画像の撮影",divider=True)
    st.markdown("Image to Image を行う写真を撮影します。")
    st.markdown(F"生成画像サイズ: {st.session_state.clip_position['width']}x{st.session_state.clip_position['height']}")
    st.markdown(F"スクエアポジション: x{st.session_state.clip_position['x']} / y{st.session_state.clip_position['y']}")

    webrtc_ctx = webrtc_streamer(key="i2i_cam",
                                video_processor_factory=VideoTransformer,
                                rtc_configuration=RTC_CONFIGURATION,
                                sendback_audio=False,
                                media_stream_constraints={"video": {"width": 1920, "height": 1080}, "audio": False})

    i2i_image_path = './images/i2i_image.jpg'
    if webrtc_ctx.video_processor:
        #暗転処理
        if display.draw_image_path != './images/black_BG.png' and display.draw_image_path != None:
            resolution_list = [int(number) for number in st.session_state.display_size.split('x')]
            display.create_image(resolution_list[0],resolution_list[1],'#000000','./images/black_BG.png')
            display.update_image_path('./images/black_BG.png',False)

        timer = st.slider("timer",0,60,10)
        if st.button("スクリーンショットを撮影する",key="i2i_shutter"):
            time.sleep(timer)
            with webrtc_ctx.video_processor.frame_lock:
                if webrtc_ctx.video_processor.out_frame is not None:
                    cv2.imwrite(i2i_image_path, webrtc_ctx.video_processor.out_frame)  # 画像を保存
                    clip_module.crop_from_another_image(st.session_state.clip_position,i2i_image_path,i2i_image_path) #画像から切り抜き
                    st.image(i2i_image_path, channels="BGR", caption="I2I ソースイメージ")
    
    st.header("Step.4 マスク 設定",divider=True)
    col1,col2 = st.columns([3,1])
    with col1:
        st.session_state.dino_prompts = st.text_area(
            "Prompt",
            value = st.session_state.dino_prompts,
            key="dino_prompt"
        )
    with col2:
        if st.button("Generate Mask",type='primary'):
            st.session_state.mask_path_list = sam_predict(i2i_image_path,st.session_state.dino_prompts)
    if st.session_state.mask_path_list is not None:
        columns = st.columns(len(st.session_state.mask_path_list))
        for col, item in zip(columns, st.session_state.mask_path_list):
            with col:
                st.image(item)
        st.session_state.mask_path = st.selectbox('Select Maks',st.session_state.mask_path_list)
    
    st.header("Step.5 img2img 設定",divider=True)
    col1,col2 = st.columns([3,1])
    with col1:
        prompt = st.text_area(
            "Prompt",
            key="i2i_prompt"
        )
        negative_prompts = st.text_area(
            "Negative prompt",
        )
    with col2:
        preset_prompt_on = st.toggle("Basic Prompt")
        preset_ngprompt_on = st.toggle("Basic NG Prompt")
        batch_size = st.slider('Batch Size',1,10,3)
        denoising_strength = st.slider('Denoising Strength',0.0,1.0,0.6)
        if st.button("Generate",type='primary'):
            if preset_prompt_on:
                prompt = prompt + config.preset_prompt
            if preset_ngprompt_on:
                negative_prompts = negative_prompts + config.preset_ng_prompt
            delete_png(config.output_path)
            st.session_state.image_path_list = img2img_dpth_api(prompt,
                                                 negative_prompts,
                                                 i2i_image_path,
                                                 st.session_state.mask_path,
                                                 batch_size,
                                                 denoising_strength=denoising_strength)

    if st.session_state.image_path_list != None:
        columns = st.columns(len(st.session_state.image_path_list))
        for col, item in zip(columns, st.session_state.image_path_list):
            with col:
                st.image(item)

        st.session_state.image_path = st.selectbox('Result Data',st.session_state.image_path_list)
        st.write(st.session_state.image_path)
        draw_projector = st.toggle("プロジェクタへ描画")
        if draw_projector:
            display.update_image_path(st.session_state.image_path,True)
        else:
            if display.draw_image_path != './images/black_BG.png' and display.draw_image_path != None:
                resolution_list = [int(number) for number in st.session_state.display_size.split('x')]
                display.create_image(resolution_list[0],resolution_list[1],'#000000','./images/black_BG.png')
                display.update_image_path('./images/black_BG.png',False)

if __name__ == "__main__":
    main()
