from flask import Flask, redirect, url_for, request, render_template, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField
from flask_bootstrap import Bootstrap
import numpy as np
from PIL import Image
import pandas as pd
import requests
from scipy.cluster.vq import whiten, kmeans


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECURE_KEY'
Bootstrap(app)

# File upleoad form
class UploadForm(FlaskForm):
    file = FileField(validators=[FileRequired()])
    submit = SubmitField(label='GET COLORS')

# main page
@app.route("/", methods = ["GET", "POST"])
def index():
    form = UploadForm()
    if request.method == "POST":

        # get image
        photo = form.file.data

        # convert to array
        img = Image.open(photo)
        img_a = np.asarray(img)

        # get 10 main colors from array
        list_of_colors = []
        for row in range(0,img_a.shape[0]):
            for column in img_a[row]:
                color = str(tuple(column))
                list_of_colors.append(color)
        series_of_colors = pd.Series(list_of_colors)
        color_count = series_of_colors.groupby(series_of_colors).count()
        winner_colors = color_count.sort_values(ascending=False)[:10]
        winners = winner_colors.reset_index(level=0)
        winners.rename(columns={"index": "color", "0": "count"}, inplace=True)

        # get colors from api
        color_links = []
        for color in winners["color"]:
            r = requests.get(url=f"https://www.thecolorapi.com/id?rgb=rgb{color}1&format=json")
            data = r.json()
            color_link = data["image"]["named"]
            color_links.append(color_link)
        return render_template("index.html", form=form, colors=color_links)

    else:
        return render_template("index.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)
