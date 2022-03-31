from flask import Flask, render_template
# import tensorflow as tf
# from tensorflow import keras
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image
from bs4 import BeautifulSoup


soup = BeautifulSoup("templates/index.html")

# model = load_model("models/monet_generator.h5")

# print(model.summary())


app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug=True)