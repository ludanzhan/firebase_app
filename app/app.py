from flask import Flask, render_template, request, redirect, flash, url_for
from firebase import firebase
from helper import *
from requests.exceptions import ConnectionError
import os
from werkzeug.utils import secure_filename

firebase = firebase.FirebaseApplication('https://dsci-551-project-177ec-default-rtdb.firebaseio.com/', None)
app = Flask(__name__)

curdir = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = os.path.join(curdir, 'temp')
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'This doesnt matter, but is required'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/firebase.html", methods=('GET', 'POST'))
def firebase_html():
    analyses_output = ""
    cat_output = ""
    html="No Data or unable to communicate with database"

    # Handle POST
    if request.method == 'POST':
        data = request.form.to_dict()
        # Handle EDFS Commands
        if data.get('command'):
            file = request.files.get('file_input')
            data['file_input'] = file
            cmd = validate_input(data, file)

            if cmd.error:
                flash(cmd.error, 'danger')

            else:
                flash(f"Executing $edfs {cmd.command} {cmd.file_input} {cmd.arg1} {cmd.arg2}", 'primary')
                response = run_command(cmd, 'firebase')

                if cmd.command == "cat":
                    cat_output = response.output

                    if response.status == "danger":
                        flash(response.output, response.status)
                    else:
                        flash(f"Succesfully retreived contents of {cmd.arg1}", response.status)
                    
                    # We Return early on a CAT command
                    return render_template("firebase.html", data=html, cat_output=cat_output, analyses_output=analyses_output)

                else:
                    flash(response.output, response.status)

            return redirect(url_for('firebase_html'))
        
        elif data.get('analyses'):
            analyses_output = run_analyses(data.get('analyses'), database='firebase')

    try:
        database = firebase.get('/', None)
        html = dict_to_html("", database)
    except ConnectionError:
        logger.error(f"Couldn't establish a connection to Firebase!")
        flash("Couldn't establish a connection to firebase! Are you online?", "danger")

    return render_template("firebase.html", data=html, cat_output=cat_output, analyses_output=analyses_output)


@app.route("/mysql.html", methods=('GET', 'POST'))
def mysql_html():
    analyses_output = ""
    cat_output = ""
    html="No Data or unable to communicate with database"
    if request.method == 'POST':
        data = request.form.to_dict()
        if data.get('command'):
            # Logic for handling EDFS Commands
            cmd = validate_input(data)
            if cmd.error:
                flash(cmd.error, 'danger')
            else:
                flash(f"Executing $edfs {cmd.command} {cmd.file_input} {cmd.arg1} {cmd.arg2}", 'primary')
                response = run_command(cmd, 'mysql')
                if cmd.command == "cat": # Need special logic to handle CAT command
                    cat_output = response.output # Need addtl logic to actually pass CAT output
                    if response.status == "danger":
                        flash(response.output, response.status)
                    else:
                        flash(f"Succesfully retreived contents of {cmd.arg1}", response.status)
                        # Handle CAT Output Here
                else:
                    flash(response.output, response.status)

            return redirect(url_for('mysql_html'))
        
        elif data.get('analyses'):
            # analyses_output = run_analyses((data.get('analyses'), database='mysql') <-- runs specific analyses
            analyses_output = format_analyses_output('')
        else:
            # default
            pass

    # database = None ## LOGIC TO GET MYSQL DATABASE GOES HERE
    # html = dict_to_html("", database)

    return render_template("mysql.html", data=html, cat_output=cat_output, analyses_output=analyses_output)


if __name__ == "__main__":
    app.run(debug=True)
