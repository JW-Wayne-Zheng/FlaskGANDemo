from flask import Flask, render_template
from tensorflow.keras.models import load_model
import tensorflow_addons as tfa
from bs4 import BeautifulSoup
import cv2
import tensorflow as tf
import PIL
import numpy as np
import generator

soup = BeautifulSoup("templates/index.html")
model = generator.generator_fn()
model.load_weights("models/monet_generator.h5")
# model = load_model("models/monet_generator.h5", custom_objects={"InstanceNormalization":tfa.layers.InstanceNormalization})
print(model.summary())

img = cv2.imread("test-images\Webp.net-resizeimage.jpg")
img = tf.reshape(img, [1, 256, 256, 3])
prediction = model(img, training=False)[0].numpy() # make predition
prediction = (prediction * 127.5 + 127.5).astype(np.uint8)   # re-scale
im = PIL.Image.fromarray(prediction)
im.save("output.jpg")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug=True)