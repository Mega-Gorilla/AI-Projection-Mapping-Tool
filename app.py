import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import threading
import av
import numpy as np
from module.display import display_module
import time

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
    if 'green_bg_image' not in st.session_state:
        st.session_state.green_bg_image = None

def main():
    initialize()
    # 画面情報取得
    display = st.session_state.display_module
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
                    st.session_state.green_bg_image = webrtc_ctx.video_processor.out_frame
    
    generate_image_size = {}
    generate_image_size["width"]=monitors_info[st.session_state.display_num-1]['width']//64*64
    generate_image_size["height"]=monitors_info[st.session_state.display_num-1]['height']//64*64
    st.markdown(F"生成画像サイズ: {generate_image_size['width']}x{generate_image_size['height']}")


    webrtc_ctx = webrtc_streamer(key="example", video_processor_factory=VideoTransformer,
                                 rtc_configuration=RTC_CONFIGURATION,sendback_audio=False)

    if webrtc_ctx.video_processor:
        if st.button("スクリーンショットを取る"):
            with webrtc_ctx.video_processor.frame_lock:
                if webrtc_ctx.video_processor.out_frame is not None:
                    st.image(webrtc_ctx.video_processor.out_frame, channels="BGR", caption="スクリーンショット")

if __name__ == "__main__":
    main()
