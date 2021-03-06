import requests as request
from flask import Flask, flash, request, redirect, render_template, session, send_from_directory
from traceClustering.main import check_sample_list, traceclustering_main
import os

app = Flask(__name__)

app.config['STORAGE_PATH'] = "uploads/"
app.config['LOG_FORMAT'] = ['xes']
app.config['SAMPLE_FORMAT'] = ['csv']
app.secret_key = "secret key"
app.config['OUTPUT'] = "output/"


def replaceSample(filename, newsample):
    """
    replace the oldest sample with the new one
    :param filename:
    :return:
    """
    with open(filename, "r") as f:
        data = f.readlines()

    toRemove = data[1]
    data[1] = data[2]
    data[2] = data[3]
    data[3] = newsample+'\n'
    with open(filename, "w") as f:
        f.writelines(data)
    deletefile = filename[:-4] + '_' + toRemove[:-1]
    print(deletefile)
    os.remove(deletefile)

def find_samples(filename):
    f = open(filename, "r")
    f.readline()
    names = []
    data = f.readlines()
    f.close()
    for d in data:
        names.append(d)
    return names


def find_projects():
    """
    list all currently created (with a stored xes file) projects
    :returns
        String of project names
    """
    dirlist = os.listdir(app.config['STORAGE_PATH'])
    message = "Currently there exist the following projects:"
    for f in dirlist:
        if f.endswith('.txt'):
            message += f[:-4]
            message += ", "

    return message[:-2]

def allowed_log_file(filename):
    """
    checks if given file has correct type for log
    :param filename: name of the file to check
    :return: boolean: file has valid type
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['LOG_FORMAT']


def allowed_sample_file(filename):
    """
    checks if given file has correct type for sample
    :param filename: name of file to check
    :return: boolean: file has valid type
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['SAMPLE_FORMAT']


@app.route('/', methods=['GET', 'POST'])
def home():
    """ Provide Landing Page to enter the Project name
    GET
    -------
        :returns
            landing page
    POST
    -------
        :returns
            Upload log page
    """
    session.pop('username', None)
    if request.method == 'POST':
        req = request.form
        if not req.get('username') is None:
            session['username'] = req.get("username")
            # create txt file
            file = open(app.config['STORAGE_PATH'] + req.get("username")+ ".txt", "a+")
            file.seek(0)
            logname = file.readline()
            file.close()
            if logname:
                print("logname:", logname)
                return render_template('log.html', log_uploaded_before=True, logname=logname)
            else:
                log_uploaded_before = False
                return render_template('log.html', log_uploaded_before=False)
        else:
            return render_template('home.html', project_names=[find_projects()])
    elif request.method == 'GET':
        return render_template('home.html', project_names=[find_projects()])


@app.route('/log', methods=['GET', 'POST'])
def upload_log_file():
    """
    provides page to upload log if user already has project
    POST
    -------
        store file and
        :return redirect to upload sample page

    GET
    -------
        :return page to select and upload log
    """
    if not session.get('username') is None:
        if request.method == 'POST':
            # If the log file is already present in the file system and the user chose to skip
            if 'skip' in request.form:
                names = find_samples(app.config['STORAGE_PATH'] + session.get('username')+ ".txt")
                print("names:", names)
                if names:
                    return render_template('sample.html', csv_uploaded_before=True, samples=names)
                else:
                    return render_template('sample.html', csv_uploaded_before=False)
            # check if the post request has the file part
            if not request.files:
                flash('No file selected for uploading.')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No file selected for uploading.')
                return redirect(request.url)
            if file and allowed_log_file(file.filename):
                filename = session.get('username') +".xes"
                # store filename into username.txt in first line
                with open(app.config['STORAGE_PATH'] + session.get('username')+".txt","r") as f:
                    data = f.readlines()
                if data:
                    data[0] = file.filename+'\n'
                    with open(app.config['STORAGE_PATH'] + session.get('username')+".txt","w") as f:
                        f.writelines(data)
                else:
                    with open(app.config['STORAGE_PATH']+ session.get('username')+".txt","w") as f:
                        f.write(file.filename + '\n')
                file.save(os.path.join(app.config['STORAGE_PATH'], session.get('username')+".xes"))
                # flash('File successfully uploaded')
                # Check if csv file was already uploaded
                names = find_samples(app.config['STORAGE_PATH'] + session.get('username') + ".txt")
                print("names", names)
                if names:
                    return render_template('sample.html', csv_uploaded_before=True, samples=names)
                else:
                    return render_template('sample.html', csv_uploaded_before=False)
            else:
                flash('The only allowed file type is xes.')
                return redirect(request.url)
        elif request.method == 'GET':
            try:
                f = open(app.config['STORAGE_PATH']+ session.get("username")+ ".txt", "r")
                filename = f.readline()
                f.close()
                if os.path.getsize(app.config['STORAGE_PATH'] + session.get('username') + ".txt") > 0:
                    logname = filename
                    return render_template('log.html', log_uploaded_before=True, logname=logname)
                else:
                    return render_template('log.html', log_uploaded_before=False)
            except Exception as e:
                print(e)
                return render_template('log.html')

    else:
        flash('Please enter a Projectname first.')
        return redirect('/')


@app.route('/sample', methods=['GET', 'POST'])
def upload_sample_file():
    """
     provides page to upload sample if user already has project
    POST
    -------
        store file and
        :return redirect to select thresholds page

    GET
    -------
        :return page to select and upload sample
    """
    if not session.get('username') is None:
        if request.method == 'POST':
            # If the log file is already present in the file system and the user chose to skip
            if 'Sample' in request.form:
                print(request.form['Sample'])
                session['samplefile'] = os.path.join(app.config['STORAGE_PATH'], session.get('username') + '_' + request.form['Sample'])
                success, error_str, clus_dict, cluster_labels, log = check_sample_list(os.path.join(app.config['STORAGE_PATH'], session.get("username") + ".xes"),session['samplefile'])

                if not success:
                    flash(error_str)
                    if log is None or clus_dict is None:
                        return redirect('/log')

                return render_template('thresholds.html', cluster_labels=cluster_labels)
            # check if the post request has the file part
            if not request.files:
                flash('No file selected for uploading.')
                return redirect(request.url)
            file = request.files['file']
            print(request.form.keys)
            if file.filename == '':
                flash('No file selected for uploading.')
                return redirect(request.url)
            if file and allowed_sample_file(file.filename):
                name = app.config['STORAGE_PATH'] + session.get('username') + ".txt"
                with open(name, "r") as f:
                    data = f.readlines()
                    alreadyIn = False
                    for d in data:
                        if d == file.filename + '\n':
                            alreadyIn = True
                            flash("This filename has already been used. The old file was overwritten")
                if not alreadyIn:
                    with open(name, "a") as f:
                        f.write(file.filename + '\n')

                file.save(os.path.join(app.config['STORAGE_PATH'], session.get('username') + '_' + file.filename))
                # flash('File successfully uploaded')
                success, error_str, clus_dict, cluster_labels, log = check_sample_list(os.path.join(app.config['STORAGE_PATH'], session.get("username") + ".xes"), os.path.join(app.config['STORAGE_PATH'], session.get('username') + '_' + file.filename))
                session['samplefile'] = os.path.join(app.config['STORAGE_PATH'], session.get('username') + '_' + file.filename)
                if not success:
                    flash(error_str)
                    if log is None or clus_dict is None:
                        return redirect('/log')

                return render_template('thresholds.html', cluster_labels=cluster_labels)
            else:
                flash('The only allowed file type is csv.')
                return redirect(request.url)
        elif request.method == 'GET':
            names = find_samples(app.config['STORAGE_PATH'] + session.get('username')+ ".txt")
            if names:
                return render_template('sample.html', samples=names)
            else:
                return render_template('sample.html')
    else:
        flash('Please enter a Projectname first.')
        return redirect('/')


@app.route('/thresholds', methods=['GET', 'POST'])
def thresholds():
    """
     provide page to calculate thresholds and performs the clustering.
     For more information on the clustering algorithm refer to backend documentation.
    POST
    -------
        perform clustering algorithm
        :return redirect to download page showing measurements and fsps

    GET
    -------
        :return page to select thresholds per cluster
    :return:
    """
    if not session.get('username') is None:
        if request.method == 'POST':
            # TODO: Check if automatic threshold is enables, accodringly call the function.
            req = request.form
            xes_path = os.path.join(app.config['OUTPUT'], session.get("username") + "_clustered.xes")
            csv_path = os.path.join(app.config['OUTPUT'], session.get("username") + "_clustered.csv")
            if not session.get('samplefile') is None:
                samplefile = session.get('samplefile')

            else:
                flash("Please choose sample file first")
                return upload_sample_file()
            support = float(req.get("support"))
            
            auto_thresh = False
            if req.get("auto_thresh"):
                auto_thresh = True


            thresh1 = list(map(float, req.getlist("threshold1")))
            print(thresh1)

            #thresh1[:] = [val / 100 for val in thresh1]
            thresh2 = list(map(float, req.getlist("threshold2")))
            #thresh2[:] = [val / 100 for val in thresh2]
            thresh3 = list(map(float, req.getlist("threshold3")))
            #thresh3[:] = [val / 100 for val in thresh3]

            success, error_str, clus_dict, cluster_labels, log = check_sample_list(os.path.join(app.config['STORAGE_PATH'], session.get("username") + ".xes"), samplefile)
            #print(success)
            #print(error_str)
            #print(clus_dict)
            #print(cluster_labels)
            #print(log[0])
            if not success:
                flash(error_str)
                if log is None or clus_dict is None:
                    return redirect('/log')

            cluster_fsps, measures = traceclustering_main(log, clus_dict, cluster_labels, support, thresh1, thresh2, thresh3, auto_thresh, xes_path, csv_path)

            #print(measures)
            #print(cluster_fsps)
            session.pop('samplefile')
            return render_template('measures.html', cluster_labels=cluster_labels, cluster_fsps=cluster_fsps, measures=measures)
        elif request.method == 'GET':
            flash("Please choose a sample first")
            return redirect('/sample')
    else:
        flash('Please enter a Projectname first')
        return redirect('/')

#output filename is set to <projectname>+_clustered.xes. File should be placed under app.config['output'] directory.
@app.route('/download_xes', methods=['GET'])
def download_xes():
    """
    send clustered xes file as download
    GET
    -------
        :return clustered xes file
    """
    if not session.get('username') is None:
        output = os.path.join(app.root_path, app.config['OUTPUT'])
        return send_from_directory(directory=output, filename=session.get('username')+"_clustered.xes", as_attachment=True)
    else:
        flash('Please enter a Projectname first')
        return redirect('/')

@app.route('/download_csv', methods=['GET'])
def download_csv():
    """
    send cluster csv file as download
    GET
    -------
        :return cluster csv file
    """
    if not session.get('username') is None:
        output = os.path.join(app.root_path, app.config['OUTPUT'])
        return send_from_directory(directory=output, filename=session.get('username')+"_clustered.csv", as_attachment=True)
    else:
        flash('Please enter a Projectname first')
        return redirect('/')

@app.route('/signout', methods=['GET','POST'])
def signout():
    if request.method == 'POST':
        session.pop('username', None)
        return redirect('/')
    else:
        return render_template('signout.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)  # to be set to False in production. Enabling this to get trace of the errors
