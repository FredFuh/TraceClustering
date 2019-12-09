import requests as request
from flask import Flask, flash, request, redirect, render_template, session, send_from_directory
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
app.config['OUTPUT'] = "output/"


def allowed_log_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['LOG_FORMAT']


def allowed_sample_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['SAMPLE_FORMAT']


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        req = request.form
        if not req.get('username') is None:
            session['username'] = req.get("username")
            return render_template('log.html')
        else:
            return render_template('home.html')
    elif request.method == 'GET':
        return render_template('home.html')


@app.route('/log', methods=['GET', 'POST'])
def upload_log_file():
    if not session.get('username') is None:
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
                filename = session.get('username') +".xes"
                print(filename)
                file.save(os.path.join(app.config['STORAGE_PATH'], filename))
                # flash('File successfully uploaded')
                return render_template('sample.html')
            else:
                flash('Allowed file types are xes')
                return redirect(request.url)
        elif request.method == 'GET':
            return render_template('log.html')
    else:
        flash('Please enter a Projectname first')
        return redirect('/')


@app.route('/sample', methods=['GET', 'POST'])
def upload_sample_file():
    if not session.get('username') is None:
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
                filename = session.get("username") + ".xes"
                file.save(os.path.join(app.config['STORAGE_PATH'], filename))
                # flash('File successfully uploaded')
                return render_template('thresholds.html')
            else:
                flash('Allowed file types are csv')
                return redirect(request.url)
        elif request.method == 'GET':
            return render_template('sample.html')
    else:
        flash('Please enter a Projectname first')
        return redirect('/')


@app.route('/thresholds', methods=['GET', 'POST'])
def thresholds():
    if not session.get('username') is None:
        if request.method == 'POST':
            # this whole stuff is just placeholder will be removed once real values are obtained
            result = list()
            measures = dict()
            measures['recall'] = 1
            measures['precision'] = 1
            measures['F1'] = 1
            result.append(measures)
            result.append(measures)
            result.append(measures)
            return render_template('measures.html', result=result)  # instead of about page, call a new page which shows FSPs for each cluster and an option to download
        elif request.method == 'GET':
            return render_template('thresholds.html')
    else:
        flash('Please enter a Projectname first')
        return redirect('/')



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signout', methods=['GET','POST'])
def signout():
    if request.method == 'POST':
        session.pop('username', None)
        return redirect('/')
    else:
        return render_template('signout.html')

#output filename is set to <projectname>+_out.xes. File should be placed under output directory.
@app.route('/download', methods=['GET'])
def download():
    if not session.get('username') is None:
        output = os.path.join(app.root_path, app.config['OUTPUT'])
        print(session.get('username')+"_out")
        return send_from_directory(directory=output, filename=session.get('username')+"_out.xes", as_attachment=True)
    else:
        flash('Please enter a Projectname first')
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)  # to be set to False in production. Enabling this to get trace of the errors
