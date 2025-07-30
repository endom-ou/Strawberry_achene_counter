# イチゴ種密度解析アプリ (Strawberry Archine Counter)

このWebアプリケーションは、イチゴ果実のRGB画像を解析し、痩果種の数と密度を概算します。

## 機能

- イチゴ果実の画像をアップロード
- 画像解析によるイチゴ果実および痩果の自動検出
- 痩果密度の算出
- 1cm角の青いシールを基準とするスケール調整

## 必要な環境

- Python 3.7以上
- OpenCV
- Flask
- NumPy

## インストール方法

1. リポジトリをクローン
```bash
git clone https://github.com/yourusername/strawberry-archine-counter.git
cd strawberry-archine-counter
```

2. 依存関係をインストール
```bash
pip install -r requirements.txt
```

3. アプリケーションを起動
```bash
python app.py
```

4. ブラウザで `http://localhost:5000` にアクセス

## 使用方法

1. イチゴと1cm角の青いシールが写った画像を準備
2. Webアプリ上で解析用画像をアップロード
3. 解析結果（痩果数、果実表面積、痩果密度）を表示　※果実表面積は果実表面の丸みを考慮しないものであることに注意
※うまく解析できない場合、果実および痩果検出パラメータを調整してください

## 画像要件

- 対応形式：PNG, JPG, JPEG
- 最大ファイルサイズ：16MB
- RGB形式
- 青色の1cm角シールをスケール基準として配置
- イチゴ果実が明確に写っていること（机の上など、均一な背景で撮影したものが望ましい）

## 技術仕様

- **バックエンド**: Flask (Python)
- **画像処理**: OpenCV
- **色空間変換**: HSV色空間での色検出
- **形態学的処理**: ノイズ除去とエッジ検出

## ライセンス

Apache License Version 2.0

## 作者

遠藤みのり（Minori Hikawa-Endo)＠岡山大学学術研究院環境生命自然科学学域
