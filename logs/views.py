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
from flask import Flask, Blueprint, render_template, request, redirect, session, url_for, abort
import pymongo
import datetime
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
from utility.database import connect
from utility.get_log_number import get_log_number
import uuid

logs_app = Blueprint('logs_app', __name__)

db=connect()

@logs_app.route("/add_log/<string:username>", methods=('GET', 'POST'))
def add_log(username):
    if request.method == 'POST':
        # Get count
        highest_record = db.logs.find({}).sort("number", pymongo.DESCENDING).limit(1)
        log = loads(dumps(highest_record))
        if log == []:
            number = 1
        else:
            number = log[0]["number"] + 1
        # Generate UUID
        my_uuid = uuid.uuid4()
        my_uuid = str(my_uuid)
        entry = {
            "owner": username,
            "log_info": request.form['log_info'].replace("'", ""),
            "number": number,
            "uuid": my_uuid,
            "when": datetime.datetime.now()
        }
        res = db.logs.insert_one(entry)
        message = 'Log data written to database'
        return redirect(url_for('main_app.home_again', username=username, message=message))

    # Check user credentials
    return render_template('add_log.html', username=username)

@logs_app.route("/list_log/<string:username>", methods=('GET', 'POST'))
def list_log(username):
    # Get a list of Actions
    my_logs = []
    log = db.logs.find({})
    logs = loads(dumps(log))
    for log in logs:
        number = log['number']
        log_entry = log['log_info']
        info = [number, log_entry]
        my_logs.append(info)

    # Check user credentials
    message = 'Return from listing'
    return render_template('list_logs.html', my_logs=my_logs, username=username, message=message)

@logs_app.route("/edit_log/<string:username>", methods=('GET', 'POST'))
def edit_log(username):
    if request.method == 'POST':
        log_info = request.form['log_info']
        if log_info == "unselected":
            message = "please select a valid log"
            my_logs = my_logs = get_log_number(db, username)
            return render_template('edit_log.html', my_logs=my_logs, message=message, username=username)

        temp = log_info.split('-')
        number = temp[0]
        number = int(number)
        logs = db.logs.find({"number":number})
        log = loads(dumps(logs))
        log_info = log[0]['log_info']
        return render_template('edit_log_complete.html', log_info=log_info, number=number, username=username)

    # Get a list of prep_logs.
    my_logs = get_log_number(db, username)
    return render_template('edit_log.html', my_logs=my_logs, username=username)

@logs_app.route("/edit_log_complete", methods=('GET', 'POST'))
def edit_log_complete():
        username = request.form['username'].replace("'", "")
        number = request.form['number'].replace("'", "")
        log_info = request.form['log_info'].replace("'", "")
        number = int(number)
        myquery = { "number": number }
        newvalues = { "$set": { "log_info": log_info }}
        db.logs.update_one(myquery, newvalues)
        message = 'Log information been updated in the database'
        return redirect(url_for('main_app.home_again', username=username, message=message))

@logs_app.route("/delete_log/<string:username>", methods=('GET', 'POST'))
def delete_log(username):
    if request.method == 'POST':
        log = request.form['log_info']
        if log == "unselected":
            my_logs = get_log_number(db, username)
            message = "please select a valid action"
            return render_template('delete_log.html', message=message, my_logs=my_logs, username=username)

        temp = log.split('-')
        number = temp[0]
        number = int(number)
        log = db.logs.delete_one({"number":number})
        message = "Log entry has been deleted"
        return redirect(url_for('main_app.home_again', username=username, message=message))

    # Get a list of logs
    my_logs = get_log_number(db, username)
    return render_template('delete_log.html', my_logs=my_logs, username=username)
