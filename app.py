from flask import Flask, render_template, request, redirect, url_for, send_file
from PIL import Image, ImageDraw, ImageEnhance
import os
import io
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def process_image(image, brightness=1.0, contrast=1.0):
    target_size = (1989, 1300)
    img_ratio = target_size[0] / target_size[1]
    img_ratio_original = image.width / image.height

    if img_ratio_original > img_ratio:
        new_height = target_size[1]
        new_width = int(new_height * img_ratio_original)
    else:
        new_width = target_size[0]
        new_height = int(new_width / img_ratio_original)

    img_resized = image.resize((new_width, new_height), Image.LANCZOS)

    left = (new_width - target_size[0]) / 2
    top = (new_height - target_size[1]) / 2
    right = (new_width + target_size[0]) / 2
    bottom = (new_height + target_size[1]) / 2

    img_cropped = img_resized.crop((left, top, right, bottom))
    
    img_gray = img_cropped.convert("L")
    enhancer = ImageEnhance.Brightness(img_gray)
    img_brightened = enhancer.enhance(brightness)
    contrast_enhancer = ImageEnhance.Contrast(img_brightened)
    img_contrasted = contrast_enhancer.enhance(contrast)

    return halftone_effect(img_contrasted, dot_size=12)

def halftone_effect(image, dot_size=12):
    halftone_image = Image.new("L", image.size, color=0)
    width, height = image.size

    for y in range(0, height, dot_size):
        for x in range(0, width, dot_size):
            gray_value = image.getpixel((x, y))
            base_radius = int(gray_value / 255 * (dot_size / 2))
            radius = max(1, int(base_radius))

            draw = ImageDraw.Draw(halftone_image)

            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx**2 + dy**2 <= radius**2:
                        draw.point((x + dx, y + dy), fill=255)

    colored_image = Image.new("RGB", halftone_image.size)
    for x in range(halftone_image.width):
        for y in range(halftone_image.height):
            value = halftone_image.getpixel((x, y))
            if value == 255:
                colored_image.putpixel((x, y), (231, 66, 24))  # Оранжевый цвет
            else:
                colored_image.putpixel((x, y), (19, 6, 4))  # Черный цвет

    return colored_image

@app.route('/')
def index():
    return render_template('index.html', img_data=None)  # Изменено для инициализации img_data

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    img = Image.open(file.stream)
    img.save(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg'))

    # Обработка изображения с дефолтными значениями
    processed_image = process_image(img)
    img_io = io.BytesIO()
    processed_image.save(img_io, 'PNG')
    img_io.seek(0)
    img_data = base64.b64encode(img_io.read()).decode()

    # Сохранение оригинального изображения для скачивания
    img.save(os.path.join(app.config['UPLOAD_FOLDER'], 'original_image.jpg'))

    return render_template('index.html', img_data=img_data)

@app.route('/update', methods=['POST'])
def update_image():
    brightness = float(request.form.get('brightness', 1.0))
    contrast = float(request.form.get('contrast', 1.0))
    
    # Загружаем исходное изображение
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    img = Image.open(img_path)

    processed_image = process_image(img, brightness, contrast)
    img_io = io.BytesIO()
    processed_image.save(img_io, 'PNG')
    img_io.seek(0)
    img_data = base64.b64encode(img_io.read()).decode()

    # Сохранение отредактированного изображения для скачивания
    processed_image.save(os.path.join(app.config['UPLOAD_FOLDER'], 'edited_image.png'))

    return {'img_data': img_data}

@app.route('/download')
def download_image():
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], 'edited_image.png'), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
