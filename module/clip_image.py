import cv2
import numpy as np

class clip_image:
    def __init__(self):
        self.exit_flag = False
        self.ix = None
        self.iy = None
        self.drawing = None
        self.img = None
        self.roi = None
        self.rect_width = None
        self.rect_height = None
    
    # コールバック関数の定義
    def draw_rectangle(self,event, x, y, flags, param):

        # マウスがクリックされたとき
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y

        # マウスが移動している間、長方形を描画（クリック状態で）
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing == True:
                img_copy = self.img.copy()
                # 64の倍数に調整
                adjusted_x = x - (x - self.ix) % 16
                adjusted_y = y - (y - self.iy) % 16
                cv2.rectangle(img_copy, (self.ix, self.iy), (adjusted_x, adjusted_y), (0, 255, 0), 1)
                cv2.imshow('clip_BG', img_copy)

        # マウスボタンが離されたとき
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            # 64の倍数に調整
            self.rect_width = abs(x - self.ix) - (abs(x - self.ix) % 16)
            self.rect_height = abs(y - self.iy) - (abs(y - self.iy) % 16)
            self.crop_image(self.ix, self.iy, self.rect_width, self.rect_height)
            cv2.rectangle(self.img, (self.ix, self.iy), (x, y), (0, 255, 0), 1)
            self.exit_flag = True

    def crop_image(self,x, y, width, height):
        # 四角で囲まれた範囲を切り抜く
        self.roi = self.img[y:y+height, x:x+width]
        # 切り抜いた画像を保存
        cv2.imwrite('./images/cropped_image.jpg', self.roi)

    def crop_from_another_image(self,crop_info, source_image_path, output_image_path):
        """
        指定されたソース画像から指定された領域を切り抜き、指定されたパスに画像を保存する。

        Parameters:
            crop_info (dict): 切り抜く領域の情報。{'x': int, 'y': int, 'width': int, 'height': int}
            source_image_path (str): ソース画像のパス。
            output_image_path (str): 切り抜いた画像を保存するパス。
        """
        # ソース画像を読み込む
        img = cv2.imread(source_image_path)
        if img is None:
            print("ソース画像が読み込めません。パスを確認してください。")
            return

        # 切り抜き
        x = crop_info['x']
        y = crop_info['y']
        width = crop_info['width']
        height = crop_info['height']
        cropped_img = img[y:y + height, x:x + width]

        # 切り抜いた画像を保存
        cv2.imwrite(output_image_path, cropped_img)
        print(f"Image cropped and saved to {output_image_path}")

    
    def main(self,img_path):
        self.img = cv2.imread(img_path)
        if self.img is None:
            print("画像が読み込めません。パスを確認してください。")
            return
        cv2.namedWindow('clip_BG')
        cv2.setMouseCallback('clip_BG', self.draw_rectangle)
                
        self.drawing = False # 描画中フラグ
        self.ix, self.iy = -1, -1
        self.roi = None
        # キー入力を待ちながら画像を表示
        while True:
            cv2.imshow('clip_BG', self.img)
            if self.exit_flag:  # exit_flagがTrueの場合にループを抜ける
                break
            k = cv2.waitKey(1) & 0xFF
            if k == 27:  # ESC キーで終了
                break

        cv2.destroyAllWindows()
        return {'x':self.ix,'y':self.iy,'width':self.rect_width,'height':self.rect_height}


if __name__ == "__main__":
    clip_image = clip_image()
    img_path = './greenback.jpg'
    result = clip_image.main(img_path)
    print(result)
    clip_image.crop_from_another_image(result,img_path,'cropped_image2.jpg')