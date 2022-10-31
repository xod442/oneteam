'''
_______  _        _______ _________ _______  _______  _______
(  ___  )( (    /|(  ____ \\__   __/(  ____ \(  ___  )(       )
| (   ) ||  \  ( || (    \/   ) (   | (    \/| (   ) || () () |
| |   | ||   \ | || (__       | |   | (__    | (___) || || || |
| |   | || (\ \) ||  __)      | |   |  __)   |  ___  || |(_)| |
| |   | || | \   || (         | |   | (      | (   ) || |   | |
| (___) || )  \  || (____/\   | |   | (____/\| )   ( || )   ( |
(_______)|/    )_)(_______/   )_(   (_______/|/     \||/     \|
===============================================================================
2022 wookieware.


   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


__author__ = "@netwookie"
__credits__ = ["Rick Kauffman"]
__license__ = "Apache2"
__version__ = "1.0.0"
__maintainer__ = "Rick Kauffman"
__email__ = "rick@rickkauffman.com"
__status__ = "Prototype"

Flask script that manages strains and stores
'''
from flask import Flask, Blueprint, render_template, request, redirect, session, url_for, abort, send_file
import pymongo
import datetime
import requests
import os
from bson.json_util import dumps
from bson.json_util import loads
from utility.get_logs import get_logs
from utility.get_actions import get_actions
from utility.action_dump_prep import prep_actions
from utility.log_dump_prep import prep_logs
from utility.deal_dump_prep import prep_deals
from utility.company_dump_prep import prep_company
from utility.customer_dump_prep import prep_customer
from utility.meetings_dump_prep import prep_meeting
from utility.line_writer import process_line
from utility.line_writer_da5id import process_line_da5id
from utility.database import connect
import uuid
from flask_cors import CORS
from werkzeug.utils import secure_filename

misc_app = Blueprint('misc_app', __name__)
CORS(misc_app)

db=connect()

@misc_app.route("/magic/<string:username>", methods=('GET', 'POST'))
def magic(username):
    # Check user credentials
    message = 'Magic 8 Ball? You must be desperate :-)'
    return render_template('magic.html', username=username, message=message)

@misc_app.route("/load_pin/<string:username>", methods=('GET', 'POST'))
def load_pin(username):
    if request.method == 'POST':
        pin = request.form['pin']
        if str(pin) == '3838':
            return render_template('load.html', username=username)
        else:
            message = 'wrong PIN number'
            return render_template('pin.html', username=username, message=message)
    return render_template('pin.html', username=username)

@misc_app.route("/load_pin_da5id/<string:username>", methods=('GET', 'POST'))
def load_pin_da5id(username):
    if request.method == 'POST':
        pin = request.form['pin']
        if str(pin) == '3838':
            return render_template('load_da5id.html', username=username)
        else:
            message = 'wrong PIN number'
            return render_template('pin.html', username=username, message=message)
    return render_template('pin_da5id.html', username=username)

@misc_app.route("/load_warn/<string:username>", methods=('GET', 'POST'))
def load_warn(username):
    return render_template('load.html', username=username)

@misc_app.route("/load_warn_da5id/<string:username>", methods=('GET', 'POST'))
def load_warn_da5id(username):
    return render_template('load_warn_da5id.html', username=username)


@misc_app.route("/load/<string:username>", methods=('GET', 'POST'))
def load(username):

    if request.method == 'POST':
        backupfile = request.files['file']
        backupfile.save(secure_filename(backupfile.filename))
        filename = secure_filename(backupfile.filename)
        f = open(filename, "r")
        while True:
            # read a single line
            line = f.readline()
            line = line.rstrip()
            if not line:
                break
            if line[0] == "@":
                junk, dbname = line.split('-')
                line = f.readline()
                line = line.rstrip()
            process = process_line(db,dbname,line)
        # close the pointer to that file
        f.close()
        message = 'File has been loaded in the MongoDb'
        return redirect(url_for('main_app.home_again', username=username, message=message))

@misc_app.route("/load_da5id/<string:username>", methods=('GET', 'POST'))
def load_da5id(username):
    if request.method == 'POST':
        backupfile = request.files['file']
        filename = secure_filename(backupfile.filename)
        f = open(filename, "r")
        while True:
            # read a single line
            line = f.readline()
            line = line.rstrip()
            if not line:
                break
            if line[0] == "@":
                junk, dbname = line.split('-')
                line = f.readline()
                line = line.rstrip()
            process = process_line_da5id(db,dbname,line, username)
        # close the pointer to that file
        f.close()
        message = 'File has been loaded in the MongoDb'
        return redirect(url_for('main_app.home_again', username=username, message=message))

@misc_app.route("/loadcsv/<string:username>", methods=('GET', 'POST'))
def loadcsv(username):
    # open the file for reading
    number = 1
    f = open("action.csv", mode="r", encoding='utf-8-sig')
    while True:
        # read a single line
        line = f.readline()
        line = line.rstrip()
        action = line.split(',')
        if action[0] == '':
            break

        # Generate UUID
        my_uuid = uuid.uuid4()
        my_uuid = str(my_uuid)

        company = action[0]
        actionitem = action[4]
        owner = action[2]
        notes = action[1]
        #compute due_date
        month = action[3][0:1]
        month = '0' + str(month) + '-'
        day = action[3][1:2]
        day = '0' + str(day) + '-'
        year = action[3][3:7]
        due_date = str(month) + str(day) + str(year)

        entry = {
            "username": username,
            "action": actionitem,
            "owner": owner,
            "notes": notes,
            "due_date": due_date,
            "company": company,
            "number": number,
            "uuid": my_uuid,
            "status": "open",
            "when": datetime.datetime.now()
        }
        res = db.actions.insert_one(entry)
        number= number + 1

    # close the pointer to that file
    f.close()
    message = 'Bulk Action Item information written to database'
    return redirect(url_for('main_app.home_again', username=username, message=message))

@misc_app.route("/wipe_warn/<string:username>", methods=('GET', 'POST'))
def wipe_warn(username):
    return render_template('wipe_warn.html', username=username)


@misc_app.route("/wipe/<string:username>", methods=('GET', 'POST'))
def wipe(username):
    db.actions.drop()
    db.logs.drop()
    db.deals.drop()
    db.company.drop()
    db.customer.drop()
    db.meetings.drop()
    message = "database has been deleted"
    return redirect(url_for('main_app.home_again', username=username, message=message))

@misc_app.route("/dump/<string:username>", methods=('GET', 'POST'))
def dump(username):
    # Get db records and dump them to a file
    actions = prep_actions(db)
    logs = prep_logs(db)
    deal = prep_deals(db)
    company = prep_company(db)
    customer = prep_customer(db)
    meetings = prep_meeting(db)
    message = 'Database has been written to the oneteam_data.txt file'
    return redirect(url_for('main_app.home_again', username=username, message=message))

@misc_app.route("/download_report", methods=('GET', 'POST'))
def download_report():
    # Check user credentials
    return send_file('oneteam_deals_report.html', as_attachment=True)

@misc_app.route("/logout", methods=('GET', 'POST'))
def logout():
    # Check user credentials
    return render_template('logout.html')

@misc_app.route("/help/<string:username>", methods=('GET', 'POST'))
def help(username):
    # Check user credentials
    return render_template('help.html', username=username)


@misc_app.route("/test_table", methods=('GET', 'POST'))
def test_table():
    data = request.get_json()
    return render_template('help.html', data=data)

@misc_app.route("/page_test", methods=('GET', 'POST'))
def page_test():
    return render_template('deal_lobs.html')
