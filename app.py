import argparse
import zipfile as zp
import io
import os
from PIL import Image

import torch
from flask import Flask, flash, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

uploads = "static/uploads/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = uploads

def predict(img):
    results =  model(img, size=640)
    results.render()
    return results	

@app.route("/", methods=["GET", "POST"])
def modelapp():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('File not present')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('File not selected')
            return redirect(request.url)
        if not file:
             return
        if file:
            filename = secure_filename(file.filename)
            print(filename) 
        streamed_file = file.stream._file  
        zipped = zp.ZipFile(streamed_file)
        names_list = zipped.namelist()
        files_name_kept_list = []
        for name in names_list:
            file_not_accepted = name.startswith("_")
            if file_not_accepted:
                continue
            else:
                files_name_kept_list.append(name)
        files_list = []
        for name in files_name_kept_list:
            zips = zipped.open(name)
            zips_read = zips.read()
            files_list.append(zips_read)
        print(files_name_kept_list)
        images = []
        for file in files_list:
            image = Image.open(io.BytesIO(file))
            images.append(image)
        results = predict(images)
        i = 0
        for image in results.imgs:
            Image.fromarray(image).save(os.path.join(app.config['UPLOAD_FOLDER'], files_name_kept_list[i]))
            i += 1
        return redirect(url_for('.results', imgs = ",".join(str(x) for x in files_name_kept_list)))

    return render_template("index.html")

@app.route("/results", methods = ['GET', 'POST'])
def results():
    paths = []
    for filename in request.args['imgs'].split(","):
        paths.append(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('results.html', images=paths)

if __name__ == "__main__":
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='./best_modeltwo.pt', force_reload=True, autoshape=True) 
    model.conf = 0.07
    model.eval()
    app.run(debug=True)
