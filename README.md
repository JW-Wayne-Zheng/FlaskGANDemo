# FlaskGANDemo
## General
This is a web application that allows users to upload images and apply artists' style transformations to the images.

**Note:** The information regarding the machine learning models used can be found [here](https://github.com/WayneJWZLemon/CIS4496-GANs-Project)
## How to run it locally for development
**Notes: Because the model was trained on a specific Kaggle Notebook environment, it is preferred to run your local environment listed below. (We did not perform any testing on other version of Python and Tensorflow)**
```
Python == 3.8
TensorFlow == 2.4
TensorFlow_addons == 0.14
```
1. Pull the repository locally and open it in any code editor that supports Python.
2. Run ```pip install -r requirements.txt```
3. Navigate to the root folder of the project then do ```python app.py```, then you should be able to access the application on your localhost.

## Hosting
**Note:** This is only a beta release for testing, there could be bugs in the application to be resolved. The page could take some time to load, if your request is left with a "loading" indicator, please try to refresh the page again. The app is running on a free tier service, which could lead to some low performance issues.

Render: https://paintingganapp.onrender.com/
