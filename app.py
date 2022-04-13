from numpy import load
from numpy import expand_dims
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img
from matplotlib import pyplot
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

# load an image to the preferred size
def load_resize_image(filename, size=(256,256)):
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
image_src = load_resize_image('test.jpeg')
# load the model
model_AtoB = load_model('models/monet_generator.h5')
# translate image
image_tar = model_AtoB.predict(image_src)
# scale from [-1,1] to [0,1]
image_tar = (image_tar + 1) / 2.0
# plot the translated image
pyplot.imshow(image_tar[0])
pyplot.savefig('output.jpg')
pyplot.show()


# model = generator.generator_fn()
# model.load_weights("models/monet_generator.h5")
# model = load_model("models/monet_generator.h5", custom_objects={"InstanceNormalization":tfa.layers.InstanceNormalization})
# print(model.summary())

# img = cv2.imread("test.jpeg")
# img = tf.reshape(img, [1, 256, 256, 3])
# prediction = model(img, training=False)[0].numpy() # make predition
# prediction = (prediction * 127.5 + 127.5).astype(np.uint8)   # re-scale
# im = PIL.Image.fromarray(prediction)
# im.save("output.jpg")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug=True)