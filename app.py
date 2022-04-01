from flask import Flask, render_template
from tensorflow import keras
import tensorflow_addons as tfa
from bs4 import BeautifulSoup


soup = BeautifulSoup("templates/index.html")

model = keras.models.load_model("models/monet_generator.h5", custom_objects={"InstanceNormalization":tfa.layers.InstanceNormalization})

print(model.summary())


app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug=True)