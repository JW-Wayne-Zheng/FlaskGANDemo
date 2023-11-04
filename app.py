import sys
import os
from contextlib import redirect_stderr
from grpc import secure_channel
from numpy import load
from numpy import expand_dims
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img
from matplotlib import pyplot
from flask import Flask, render_template, redirect, url_for, request, flash
from tensorflow.keras.models import load_model
import tensorflow_addons as tfa
import tensorflow as tf
import PIL
import numpy as np
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "AzplDmi6jA"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
model_path = os.path.join(os.path.dirname(__file__), 'models', 'monet_generator.tflite')
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

uploadFile= ""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_resize_image(filename, size=(256, 256)):
    pixels = load_img(filename, target_size=size)
    pixels = img_to_array(pixels)
    pixels = expand_dims(pixels, 0)
    pixels = (pixels - 127.5) / 127.5
    return pixels


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")

@app.route("/convert", methods=["POST"])
def convert_image():
    image_src = load_resize_image("static/uploads/"+uploadFile)
    artist = request.form.get('which_artists')
    image_tar = None
    interpreter.set_tensor(input_details[0]['index'], image_src)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    image_tar = output_data
    image_tar = (image_tar + 1) / 2.0
    pyplot.imshow(image_tar[0])
    pyplot.axis("off")
    pyplot.savefig('static/generated/'+uploadFile, bbox_inches='tight', pad_inches=0)
    return render_template("index.html", filename="static/uploads/"+uploadFile ,gfilename="static/generated/"+uploadFile)

@app.route('/upload', methods=["POST"])
def upload_image():
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files['file']
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        global uploadFile 
        uploadFile = filename
        file.save(os.path.join("static/uploads/", filename))
        flash("Image successfully uploaded and displayed below")
        return render_template("index.html", filename=filename)
    else:
        flash("Allowed image types are: png, jpg and jpeg")
        return redirect(request.url)

@app.route("/<filename>")
def display_image(filename):
    return redirect(url_for("static", filename="uploads/"+filename), code=301)


@app.route("/<gfilename>")
def display_generated_image(gfilename):
    return redirect(url_for("static", gfilename="generated/"+gfilename), code=301)


if __name__ == "__main__":
    app.run(debug=True)
