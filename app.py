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
    if 'mask_color' not in st.session_state:
        st.session_state.mask_color = '#008000'

def main():
    initialize()
    # 画面情報取得
    display = display_module()
    monitors_info = display.get_monitors_info()
    st.header("Step1. プロジェクターディスプレイの選択",divider=True)
    st.markdown("プロジェクターが接続されているディスプレイ番号を選択してください。")
    col1,col2 = st.columns(2)
    with col1:
        st.session_state.display_num = int(st.selectbox('set display num',tuple(d['num'] for d in monitors_info),label_visibility='collapsed',index=st.session_state.display_num-1))
    with col2:
        if st.button("TEST",type="primary"):
            st.write("設定画面に、カラーバーを作画します")
            display.display_fullscreen_image(st.session_state.display_num-1,'./images/smpte_color_bars.png',True)
            time.sleep(5)
            display.pygame_quit()
            st.experimental_rerun()

    st.header("Step2. イメージサイズ調節",divider=True)
    st.markdown("Webカメラとプロジェクター描画サイズの同期を行います。")
    initialize_BG_color = st.color_picker('1.マスクカラー設定',st.session_state.mask_color)
    st.markdown("2.Webカメラ画像の撮影")
    webrtc_ctx = webrtc_streamer(key="initialize_cam", video_processor_factory=VideoTransformer,
                                 rtc_configuration=RTC_CONFIGURATION,sendback_audio=False)
    if webrtc_ctx.video_processor:

        if st.button("スクリーンショットを取る"):
            with webrtc_ctx.video_processor.frame_lock:
                if webrtc_ctx.video_processor.out_frame is not None:
                    st.image(webrtc_ctx.video_processor.out_frame, channels="BGR", caption="スクリーンショット")
    
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
