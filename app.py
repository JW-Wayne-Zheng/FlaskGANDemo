import os
from contextlib import redirect_stderr
from grpc import secure_channel
from numpy import load
from numpy import expand_dims
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend, e.g., 'Agg'
from matplotlib import pyplot
from flask import Flask, render_template, redirect, url_for, request, flash
from tensorflow.keras.models import load_model
import tensorflow_addons as tfa
import tensorflow as tf
import unicodedata
import re

app = Flask(__name__)
app.secret_key = "AzplDmi6jA"
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
model_monet = load_model('models/monet_generator.h5')
model_degas = load_model('models/degas_generator.h5')
model_picasso = load_model('models/picasso_generator.h5')
model_rembrandt = load_model('models/rembrandt_generator.h5')
model_vangogh = load_model('models/vangogh_generator.h5')

uploadFile= ""

def secure_unicode_filename(filename):
    # Normalize the filename to NFC form, which composes characters into a consistent representation
    filename = unicodedata.normalize('NFC', filename)
    # Replace spaces and special characters (except non-English characters) with underscores
    filename = re.sub(r'[^\w\s.-]', '', filename)  # Keep non-English characters, remove unsafe ones
    filename = filename.strip().replace(' ', '_')  # Replace spaces with underscores
    return filename

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
    if(artist == "Monet"):
        image_tar = model_monet.predict(image_src)
    elif(artist == "Van Gogh"):
        image_tar = model_vangogh.predict(image_src)
    elif(artist == "Degas"):
        image_tar = model_degas.predict(image_src)
    elif(artist == "Picasso"):
        image_tar = model_picasso.predict(image_src)
    elif(artist == "Rembrandt"):
        image_tar = model_rembrandt.predict(image_src)
    else:
        image_tar = model_monet.predict(image_src)
    image_tar = (image_tar + 1) / 2.0
    pyplot.imshow(image_tar[0])
    pyplot.axis("off")
    pyplot.savefig('static/generated/'+uploadFile, bbox_inches='tight', pad_inches=0)
    return render_template("index.html", filename="static/uploads/"+uploadFile ,gfilename="static/generated/"+uploadFile)

@app.route('/upload', methods=["POST"])
def upload_image():
    if "file" not in request.files:
        flash("No file part")
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_unicode_filename(file.filename)
        global uploadFile 
        uploadFile = filename
        file.save(os.path.join("static/uploads/", filename))
        flash("Image successfully uploaded and displayed below")
        return render_template("index.html", filename=filename)
    else:
        flash("Allowed image types are: png, jpg, jpeg")
        return redirect(url_for('index'))

@app.route("/<filename>")
def display_image(filename):
    return redirect(url_for("static", filename="uploads/"+filename), code=301)


@app.route("/<gfilename>")
def display_generated_image(gfilename):
    return redirect(url_for("static", gfilename="generated/"+gfilename), code=301)


if __name__ == "__main__":
    app.run(debug=True)
