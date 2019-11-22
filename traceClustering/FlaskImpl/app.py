import requests as request
from flask import Flask, flash, request, redirect, render_template
import os

app = Flask(__name__)

app.config['folder_location'] = "/"
app.secret_key = "secret key"

@app.route('/')
def home():
    return render_template('home.html')

file_format = set(['xes'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in file_format
	

@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			file.save(os.path.join(app.config['folder_location'], file.filename))
			flash('File successfully uploaded')
			return redirect('/')
		else:
			flash('Allowed file types are xes')
			return redirect(request.url)


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True) #to be set to False in production. Enabling this to get trace of the errors