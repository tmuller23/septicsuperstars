import argparse
import zipfile
import io
import os
from PIL import Image

import torch
from flask import Flask, flash, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

uploads = "static/uploads/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
#ALLOWED_EXTENSIONS = set(['zip'])
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
        
        filestream = file.stream._file  
        zipf = zipfile.ZipFile(filestream)
        filenames = zipf.namelist()
        # Filter names to only include the filetype that you want:
        filenames = [file_name for file_name in filenames if not file_name.startswith("_")]
        files = [zipf.open(name).read() for name in filenames]
        print(filenames)
        images = [Image.open(io.BytesIO(file_bytes)) for file_bytes in files]
        results = predict(images)
        i = 0
        for img in results.imgs:
            img_base64 = Image.fromarray(img)
            img_base64.save(os.path.join(app.config['UPLOAD_FOLDER'], filenames[i]))
            i += 1
        return redirect(url_for('.results', imgs = ",".join(str(x) for x in filenames)))

    return render_template("index.html")

@app.route("/results", methods = ['GET', 'POST'])
def results():
    paths = []
    for filename in request.args['imgs'].split(","):
        paths.append(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('results.html', images=paths)

if __name__ == "__main__":
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='./best.pt', force_reload=True, autoshape=True
    ) # force_reload = recache latest code)
    model.conf = 0.05
    model.eval()
    app.run(debug=True)

    


#@app.route('/uploads/<name>')
#def download_file(name):
#    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
#app.add_url_rule(
#    "/uploads/<name>", endpoint="download_file", build_only=True
#)

