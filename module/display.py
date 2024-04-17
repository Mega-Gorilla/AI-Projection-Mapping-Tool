import pygame,re
from screeninfo import get_monitors
from PIL import Image
import threading
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import time

class display_module:

    def __init__(self):
        self.pygame_running = False
        self.stop_event = threading.Event()

    def get_monitors_info(self):
        monitors_info = []
        for monitor in get_monitors():
            # モニター名から不要な部分を除去し、番号のみを取得
            monitor_index = re.search(r'DISPLAY(\d+)', monitor.name)
            if monitor_index:
                monitor_name = monitor_index.group(1)
            else:
                monitor_name = "Unknown Monitor"
            
            # 各モニター情報を辞書としてリストに追加
            monitors_info.append({
                "num": monitor_name,
                "width": monitor.width,
                "height": monitor.height
            })
        return monitors_info

    def display_fullscreen_image(self, display_num, image_path=None, scaling=False):
        self.stop_event.clear()  # stop_eventを非設定状態に戻します
        self.current_image_path = image_path
        self.scaling = scaling
        print(f"draw_image:{self.current_image_path} / display Num:{display_num}")
        pygame.init()
        displays = pygame.display.get_num_displays()
        if displays <= display_num:
            print("ディスプレイが見つかりませんでした。")
            return

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, display=display_num)
        self.screen_width, self.screen_height = self.screen.get_size()

        while not self.stop_event.is_set():
            self.load_and_display_image()
            time.sleep(1)
        pygame.quit()
    
    def load_and_display_image(self):
        image = pygame.image.load(self.current_image_path)
        image_rect = image.get_rect()
        if self.scaling:
            image = pygame.transform.scale(image, (self.screen_width, self.screen_height))
            position = (0, 0)
        else:
            position = ((self.screen_width - image_rect.width) // 2, (self.screen_height - image_rect.height) // 2)
        self.screen.blit(image, position)
        pygame.display.flip()
    
    def pygame_quit(self):
        self.stop_event.set()
    
    def update_image_path(self, new_image_path,scaling=False):
        self.current_image_path = new_image_path
        self.scaling = scaling
        print(f"Image path updated to {new_image_path}")
    
    def create_image(self,width, height, hex_color, filename):
        """
        指定されたサイズとHEXカラーコードでPNG画像を生成し、指定されたファイル名で保存する。

        Args:
        width (int): 画像の幅
        height (int): 画像の高さ
        hex_color (str): HEXカラーコード (例: "#00f900")
        filename (str): 保存するファイル名（例: "output.png"）
        """
        # 新しい画像を作成
        image = Image.new("RGB", (width, height), hex_color)
        # 画像をPNG形式で保存
        image.save(filename, "PNG")
        print(f"画像が {filename} として保存されました。")

if __name__ == "__main__":
    display_module = display_module()
    image_path = './images/smpte_color_bars.png'
    monitors_info = display_module.get_monitors_info()
    print(monitors_info)
    display_num = 1
    # ディスプレイに画像を表示するスレッドを開始
    display_thread = threading.Thread(target=display_module.display_fullscreen_image,
                                      args=(display_num, image_path, True))
    display_thread.start()

    # ユーザーの入力を待つ (例: エンターキーで終了)
    time.sleep(5)
    new_image_path = '02026.png'
    display_module.update_image_path(new_image_path) 

    input("Press Enter to quit...")

    # pygame_quit を呼び出して、画像表示を終了
    display_module.pygame_quit()

    # スレッドの終了を待つ
    display_thread.join()