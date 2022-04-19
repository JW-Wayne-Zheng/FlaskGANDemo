from contextlib import redirect_stderr
from numpy import load
from numpy import expand_dims
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img
from matplotlib import pyplot
from flask import Flask, render_template, redirect, url_for, request
from tensorflow.keras.models import load_model
import tensorflow_addons as tfa
from bs4 import BeautifulSoup
import cv2
import tensorflow as tf
import PIL
import numpy as np

# load an image to the preferred size


def load_resize_image(filename, size=(256, 256)):
    # load and resize the image
    pixels = load_img(filename, target_size=size)
    # convert to numpy array
    pixels = img_to_array(pixels)
    # transform in a sample
    pixels = expand_dims(pixels, 0)
    # scale from [0,255] to [-1,1]
    pixels = (pixels - 127.5) / 127.5
    return pixels

# load the image
# image_src = load_resize_image('test.jpeg')
# load the model
# model_AtoB = load_model('models/monet_generator.h5')
# translate image
# image_tar = model_AtoB.predict(image_src)
# scale from [-1,1] to [0,1]
# image_tar = (image_tar + 1) / 2.0
# plot the translated image
# pyplot.imshow(image_tar[0])
# pyplot.axis("off")
# pyplot.savefig('output.jpg', bbox_inches='tight', pad_inches=0)


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		if request.form['Convert_btn'] == "Convert":
			with open("templates/index.html") as fp:
				soup = BeautifulSoup(fp, 'html.parser')
			for a in soup.find_all('img'):
				print("Found the URL:", a['src'])
			return render_template("index.html")
	else:
		return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
