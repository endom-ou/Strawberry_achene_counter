import os
from flask import Flask, request, render_template, url_for, redirect, flash
import cv2
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "strawberry_density_secret_key"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB制限

# アップロードフォルダが存在しない場合は作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # ファイルが存在するか確認
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        
        file = request.files['file']
        
        # ファイル名が空でないか確認
        if file.filename == '':
            flash('ファイルが選択されていません')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 画像処理実行
            results = process_image(filepath)
            
            return render_template('result.html', 
                                  filename=filename,
                                  strawberry_area=results['strawberry_area'],
                                  seed_count=results['seed_count'],
                                  seed_density=results['seed_density'])
    
    return render_template('index.html')

def process_image(image_path):
    # 画像を読み込む
    img = cv2.imread(image_path)
    
    # 元画像のコピーを作成（表示用）
    original = img.copy()
    
    # BGR→HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 1cm角シールの検出（青色のシールを想定）
    # 青色のHSV範囲
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # シールの輪郭を検出
    contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 最大の青い領域をシールとする
    if len(contours) > 0:
        seal_contour = max(contours, key=cv2.contourArea)
        seal_area_pixels = cv2.contourArea(seal_contour)
        
        # 1cm²が何ピクセルに相当するかを計算
        pixels_per_sqcm = seal_area_pixels / 1.0  # 1cm²のシール
    else:
        # シールが検出できない場合はデフォルト値を使用
        pixels_per_sqcm = 10000  # 仮のデフォルト値
        flash('1cm角のシールを検出できませんでした。デフォルトのスケールを使用します。')
    
    # イチゴ（赤い部分）の検出
    # 赤色のHSV範囲（赤色は色相が0付近または180付近）
    lower_red1 = np.array([0, 30, 30])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    strawberry_mask = cv2.bitwise_or(red_mask1, red_mask2)
    
    # ノイズ除去
    kernel = np.ones((5, 5), np.uint8)
    strawberry_mask = cv2.morphologyEx(strawberry_mask, cv2.MORPH_OPEN, kernel)
    strawberry_mask = cv2.morphologyEx(strawberry_mask, cv2.MORPH_CLOSE, kernel)
    
    # イチゴの輪郭を検出
    strawberry_contours, _ = cv2.findContours(strawberry_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 最大の赤い領域をイチゴとする
    if len(strawberry_contours) > 0:
        strawberry_contour = max(strawberry_contours, key=cv2.contourArea)
        strawberry_area_pixels = cv2.contourArea(strawberry_contour)
        
        # イチゴの表面積をcm²で計算
        strawberry_area_sqcm = strawberry_area_pixels / pixels_per_sqcm
        
        # イチゴの領域を描画（結果確認用）
        cv2.drawContours(original, [strawberry_contour], -1, (0, 255, 0), 2)
        
        # イチゴのマスクを作成（種の検出用）
        strawberry_only_mask = np.zeros_like(strawberry_mask)
        cv2.drawContours(strawberry_only_mask, [strawberry_contour], -1, 255, -1)
        
        # 種の検出（黄～黄赤色の点を検出）- 色範囲を広げる
        # 種の色範囲（HSV）- より広い範囲で検出
        lower_seed1 = np.array([10, 30, 40])  # より赤みがかった種も検出
        upper_seed1 = np.array([40, 255, 255])  # より黄色みがかった種まで検出

        # 白っぽい種も検出するための範囲
        lower_seed2 = np.array([0, 0, 180])  # 彩度の低い白っぽい種
        upper_seed2 = np.array([180, 40, 255])

        seed_mask1 = cv2.inRange(hsv, lower_seed1, upper_seed1)
        seed_mask2 = cv2.inRange(hsv, lower_seed2, upper_seed2)
        seed_mask = cv2.bitwise_or(seed_mask1, seed_mask2)  # 両方の条件を統合

        # イチゴの領域内の種だけを対象にする
        seed_mask = cv2.bitwise_and(seed_mask, strawberry_only_mask)

        # より穏やかなノイズ除去（小さい種も保持）
        kernel_small = np.ones((1, 1), np.uint8)  # より小さいカーネル
        seed_mask = cv2.morphologyEx(seed_mask, cv2.MORPH_OPEN, kernel_small)
        seed_mask = cv2.dilate(seed_mask, kernel_small, iterations=1)  # 種を少し膨張させて検出しやすく

        # 種の輪郭を検出
        seed_contours, _ = cv2.findContours(seed_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 種の数をカウント（最小面積を下げる）
        min_seed_area = 2  # 最小種面積を小さくして小さい種も検出
        valid_seeds = [c for c in seed_contours if cv2.contourArea(c) >= min_seed_area]
        seed_count = len(valid_seeds)  # 種の数を定義
        
        # 種の位置を描画（結果確認用）- 色を変更
        for seed_contour in valid_seeds:
            M = cv2.moments(seed_contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                # 中心に円を描画 - 黄色(0,255,255)に変更
                cv2.circle(original, (cX, cY), 3, (0, 255, 255), -1)
                # 種の輪郭も色を変更 - シアン(255,255,0)に変更
                cv2.drawContours(original, [seed_contour], -1, (255, 255, 0), 1)
        
        # 種の密度を計算（個/cm²）
        seed_density = seed_count / strawberry_area_sqcm if strawberry_area_sqcm > 0 else 0
        
        # 処理後の画像を保存
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_' + os.path.basename(image_path))
        cv2.imwrite(result_path, original)

        return {
            'strawberry_area': round(strawberry_area_sqcm, 2),  # cm²
            'seed_count': seed_count,  # 個
            'seed_density': round(seed_density, 2)  # 個/cm²
        }
    else:
        flash('イチゴを検出できませんでした。')
        return {
            'strawberry_area': 0,
            'seed_count': 0,
            'seed_density': 0
        }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)