# Auto AI Projection Mapping

[Stable Diffusion Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge) + Control Net(depth_midas) + [Segment Anything](https://github.com/continue-revolution/sd-webui-segment-anything) を用いて、プロジェクションマッピングを行うソフトウェアです。

Segment Anytingを用いて、カメラ画像から物体をマスクし、SDとControl Netを用いて、マスクした物体に対して画像を生成、投影します。

# Demo
<p float="left">
  <img src="https://github.com/Mega-Gorilla/AI-Projection-Mapping-Tool/blob/main/example_image/raw.JPG?raw=true" width="300" />
  <img src="https://github.com/Mega-Gorilla/AI-Projection-Mapping-Tool/blob/main/example_image/blood.JPG?raw=true" width="300" /> 
  <img src="https://github.com/Mega-Gorilla/AI-Projection-Mapping-Tool/blob/main/example_image/muscle.JPG?raw=true" width="300" />
</p>

# Installation

## ハードウェア
本プログラムは、以下のハードウェアを用いています。

注意: Webカメラからチャプチャーした画像を、生成に用いるため、Webカメラは可能な限り、プロジェクターのレンズと近い位置に配置する必要があります。
- プロジェクター / EPSON EB-G7900U
- Webカメラ / Logitech webcam c920

<p float="left">
<img src ="https://github.com/Mega-Gorilla/AI-Projection-Mapping-Tool/blob/main/example_image/layout.JPG?raw=true" width="300">
</p>

## ソフトウェア
- [Stable Diffusion Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge)
- [Segment Anything](https://github.com/continue-revolution/sd-webui-segment-anything)
- Control Net / Model : [diffusers_xl_depth_full.safetensors](https://huggingface.co/lllyasviel/sd_control_collection/blob/d1b278d0d1103a3a7c4f7c2c327d236b082a75b1/diffusers_xl_depth_full.safetensors)

## Auto AI Projection Mapping Installation
### 設定
Stable Diffusion Forgeの`webui-user.bat`を編集し、以下のように設定してください。設定後Forgeを起動し、ポート番号を確認します。(デフォルトポート番号は7860です。)
```
set COMMANDLINE_ARGS=--api --listen
```

その後、Forgeを起動しているサーバーのIPアドレスを確認し、Auto AI Projection Mappingにアドレス設定をします。
config.pyを編集して、server_addressを任意のサーバーアドレスに変更してください。

### ライブラリーをインストールする
```
pip install -r requirements.txt
```

### 実行
```
streamlit run app.py
```

## 開発者連絡先
Git issue または、[X - 猩々博士](https://twitter.com/Mega_Gorilla_)までご連絡ください。