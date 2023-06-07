from flask import Flask, render_template, request, redirect, url_for, g,abort, send_file
from PIL import Image
import os
from werkzeug.utils import secure_filename
import numpy as np
from forms import MyForm, FloatForm
import matplotlib.pyplot as plt
import tkinter as tk
from io import BytesIO
import cv2
import base64

app = Flask(__name__, static_folder='static')
counter = 0
app.config['UPLOAD_FOLDER'] = 'upload'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Ldval4mAAAAABVnJCBhDO2V5H1jaBod3CVCb0Kd'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Ldval4mAAAAAKsW78OlmcndDtGQeQY5l6yTd02x'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
#
@app.route('/protected')
def protected():
    # Проверяем, решена ли reCAPTCHA
    if request.args.get('captcha') == 'solved':
        return redirect(url_for('image', captcha='solved'))
    if request.args.get('captcha') == 'unsolved':
        return "Captcha not succed"
    return abort(403)

@app.route('/', methods=['GET', 'POST'])
#def submit():
 #   form = MyForm()
  #  if form.validate_on_submit():
   #     return redirect(url_for('protected', captcha='solved'))
#
 #   return render_template('index.html', form=form)

@app.route('/image', methods=['GET'])
def image():
    form = FloatForm()
    global counter
    counter+=1
    return render_template('upload-image.html',form=form,counter=counter)

@app.route('/image/upload', methods=['GET','POST'])
def upload():
    # Получаем загруженный файл из формы
    file = request.files['image']
    form = FloatForm()
    # Проверяем, что файл существует и имеет разрешенное расширение
    if file and allowed_file(file.filename):
        # Сохраняем файл на сервере
        number = form.float_number.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Выполняем необходимые операции с изображением
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        image_changed_path = "static/changed"
        # Обработка изображения
        # resize_image(image_path, filename, image_changed_path, scale=number)
        # graname = filename.split('.')[0] + "_graph.png"
        # plot_color_distribution(image_path, graname)
        # return render_template("changed_image.html", filename=filename, graph_name=graname)
    else:
        return 'Недопустимый файл'

def allowed_file(filename):
    # Проверяем разрешенные расширения файлов
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





@app.route("/rotate", methods=["POST"])
def rotate():
    # Получаем угол поворота из формы
    angle = int(request.form.get("angle"))

    # Получаем файл из формы и открываем его с помощью Pillow
    file = request.files['file']
    img = Image.open(file.stream)

    # Создаем массив изображения
    img_array = np.array(img)

    # Получаем размеры изображения
    height, width, channels = img_array.shape

    # Вычисляем центр изображения
    center_x = width / 2
    center_y = height / 2

    # Создаем матрицу поворота
    rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), angle, 1)

    # Применяем матрицу поворота к изображению
    rotated_img_array = cv2.warpAffine(img_array, rotation_matrix, (width, height))

    # Создаем объект изображения из массива
    rotated_img = Image.fromarray(rotated_img_array)

    # Создаем гистограммы для исходного и повернутого изображений
    red_hist = np.histogram(img_array[:, :, 0], bins=256, range=(0, 256))
    green_hist = np.histogram(img_array[:, :, 1], bins=256, range=(0, 256))
    blue_hist = np.histogram(img_array[:, :, 2], bins=256, range=(0, 256))

    # Рисование графика распределения цветов
    plt.figure(figsize=(10, 6))
    plt.title('Color Distribution')
    plt.xlabel('Color Intensity')
    plt.ylabel('Frequency')
    plt.xlim(0, 255)
    plt.plot(red_hist[1][:-1], red_hist[0], color='red', label='Red')
    plt.plot(green_hist[1][:-1], green_hist[0], color='green', label='Green')
    plt.plot(blue_hist[1][:-1], blue_hist[0], color='blue', label='Blue')
    plt.legend()

    # Сохраняем изображения и гистограммы на диск
    img_path = os.path.join(app.static_folder, "changed", "rotated.jpg")
    rotated_img.save(img_path)
    histogram_path = os.path.join(app.static_folder, "graph", "histogram.png")
    plt.savefig(histogram_path)

    # Отправляем на страницу результатов
    return render_template("changed_image.html", image="changed/rotated.jpg", histogram="graph/histogram.png")

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'upload'
    app.run()
