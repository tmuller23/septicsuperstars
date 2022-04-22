from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import yolov5

####################
# Model Prediction #
####################
def predict(img):
    model  = yolov5.load("defect-model")
    results =  model(img)
    return results.show()

###################
# Flask Interface #
###################
uploads = "static/uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = uploads

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/app", methods = ['GET', 'POST'])
def modelapp():
    return render_template('app.html')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route("/results", methods = ['GET', 'POST'])
def results():
    return render_template('results.html')

if __name__ == "__main__":
    app.run(debug=True)
