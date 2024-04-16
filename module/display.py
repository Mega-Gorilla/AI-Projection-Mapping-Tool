import pygame,re
from screeninfo import get_monitors
from PIL import Image
import io

class display_module:

    def __init__(self):
        self.initialized = False

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

    def display_fullscreen_image(self, display_num,image_path=None,scaling=False):
        print(f"draw_image:{image_path} / display Num:{display_num}")
        if self.initialized is False:
            pygame.init()
        # ディスプレイ情報の取得
        displays = pygame.display.get_num_displays()
        if displays < 2:
            print("ディスプレイが見つかりませんでした。")
            return
        # セカンドディスプレイのサイズを取得
        second_display_info = pygame.display.Info()
        screen_width, screen_height = second_display_info.current_w, second_display_info.current_h

        # セカンドディスプレイのサーフェスを作成
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN, display=display_num)

        # 画像の読み込み
        image = pygame.image.load(image_path)
        image_rect = image.get_rect()

        # 画像のサイズをセカンドディスプレイのサイズに合わせてスケーリング
        if scaling:
            image = pygame.transform.scale(image, (screen_width, screen_height))
            position = (0, 0)
        else:
            position = ((screen_width - image_rect.width) // 2, (screen_height - image_rect.height) // 2)

        # 画像をセカンドディスプレイに表示
        screen.blit(image, position)

        pygame.display.flip()
        self.initialized = True

    def pygame_quit(self):
        print("pygame_quit")
        pygame.quit()

    def create_image(width, height, hex_color, filename):
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
    import time
    display_module = display_module()
    monitors_info = display_module.get_monitors_info()
    print(monitors_info)
    display_module.display_fullscreen_image(1,'02026.png')
    time.sleep(5)
    display_module.display_fullscreen_image(1,'./images/smpte_color_bars.png',True)
    time.sleep(5)
    display_module.pygame_quit()