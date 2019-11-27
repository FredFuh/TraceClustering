import requests as request
from flask import Flask, flash, request, redirect, render_template, session
import os

app = Flask(__name__)

app.config['folder_location'] = "/"
app.secret_key = "secret key"


@app.route('/start')
def start():
    return render_template('login.html')


@app.route('/start', methods=['POST'])
def start_session():
    if request.method == 'POST':
        req = request.form
        session['username'] = req.get("username")
        return redirect('/')
    else:
        return redirect(request.url)


@app.route('/')
def home():
    if not session.get('username') is None:
        return render_template('home.html')
    else:
        flash("Please enter a projectname first")
        return redirect('/start')


file_format = set(['xes'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in file_format


@app.route('/', methods=['POST'])
def upload_file():
    if not session.get('username') is None:
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
                print(os.path.join(app.config['folder_location']))
                file.save(os.path.join(app.config['folder_location'], file.filename))
                flash('File successfully uploaded')
                return redirect('/thresh')
            else:
                flash('Allowed file types are xes')
                return redirect(request.url)
    else:
        flash("please enter projectname first")
        return redirect('/start')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/thresh')
def thresh():
    if not session.get("username") is None:
        return render_template('thresholds.html')
    else:
        flash("please enter projectname first")
        return redirect('/start')


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


if __name__ == '__main__':
    app.run(debug=True)  # to be set to False in production. Enabling this to get trace of the errors
