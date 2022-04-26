import argparse
import io
import os
from PIL import Image

import torch
from flask import Flask, flash, render_template, request, redirect
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
        file_bytes = file.read()
        image = Image.open(io.BytesIO(file_bytes))
        results = predict(image)
        for img in results.imgs:
            img_base64 = Image.fromarray(img)
            img_base64.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return render_template("index.html")


if __name__ == "__main__":
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='./best.pt', force_reload=True, autoshape=True
    ) # force_reload = recache latest code)
    model.conf = 0.05
    model.eval()
    app.run(debug=True)

    
#@app.route("/results", methods = ['GET', 'POST'])
#def results():
#    return render_template('results.html')

#@app.route('/uploads/<name>')
#def download_file(name):
#    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
#app.add_url_rule(
#    "/uploads/<name>", endpoint="download_file", build_only=True
#)

