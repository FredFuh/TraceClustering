import requests as request
from flask import Flask, flash, request, redirect, render_template, session
import os

app = Flask(__name__)
'''
@app.route('/thresh', methods=['POST'])
def enterthresh():
    if not session.get('username') is None:
        if request.method == 'POST':
            t1 = float(request.form['threshold1'])
            t2 = float(request.form['threshold2'])
            tclo = float(request.form['thresholdclo'])
            if t1 < 0 or t1 > 1 or t2 < 0 or t2 > 1 or tclo < 0 or tclo > 1:
                flash('Please enter values between 0 and 1 ')
                return redirect(request.url)
            # calculate clustering and show downlaod page username used to find xes and csv file (username.xes, username.csv)
            # xes, csv = clusterdata(t1,t2,tclo, username)
            session.pop("username", None)
            flash("here downloadpage will be displayed")
            return redirect('/')
        return redirect('/thresh')
    else:
        flash("please enter projectname first")
        return redirect('/start')
'''

app.config['STORAGE_PATH'] = "uploads/"
app.config['LOG_FORMAT'] = ['xes']
app.config['SAMPLE_FORMAT'] = ['csv']
app.secret_key = "secret key"


def allowed_log_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['LOG_FORMAT']


def allowed_sample_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['SAMPLE_FORMAT']


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        req = request.form
        session['username'] = req.get("username")
        return render_template('log.html')
    elif request.method == 'GET':
        return render_template('home.html')


@app.route('/log', methods=['GET', 'POST'])
def upload_log_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if not request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_log_file(file.filename):
            file.save(os.path.join(app.config['STORAGE_PATH'], file.filename))
            # flash('File successfully uploaded')
            return render_template('sample.html')
        else:
            flash('Allowed file types are xes')
            return redirect(request.url)
    elif request.method == 'GET':
        return render_template('log.html')


@app.route('/sample', methods=['GET', 'POST'])
def upload_sample_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if not request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_sample_file(file.filename):
            file.save(os.path.join(app.config['STORAGE_PATH'], file.filename))
            # flash('File successfully uploaded')
            return render_template('thresholds.html')
        else:
            flash('Allowed file types are csv')
            return redirect(request.url)
    elif request.method == 'GET':
        return render_template('sample.html')


@app.route('/thresholds', methods=['GET', 'POST'])
def thresholds():
    if request.method == 'POST':
        return render_template('about.html')  # instead of about page, call a new page which shows FSPs for each cluster and an option to download
    elif request.method == 'GET':
        return render_template('thresholds.html')


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)  # to be set to False in production. Enabling this to get trace of the errors
