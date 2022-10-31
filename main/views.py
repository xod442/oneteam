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
import uuid

main_app = Blueprint('main_app', __name__)

db = connect()

@main_app.route("/")
def main():
    return render_template('login.html')

@main_app.route("/test")
def test():
    return render_template('test_table.html')

@main_app.route("/login", methods=('GET', 'POST'))
def login():
    return render_template('login.html')

@main_app.route("/build_creds", methods=('GET', 'POST'))
def build_creds():
    username = request.form['username']
    password = request.form['password']
    passwordv = request.form['passwordv']

    # Are password the same
    if password != passwordv:
        message = "Passwords do not match"
        return render_template('creds.html', message=message)

    # Are any of the entries empty
    if username == "":
        message = "Username cannot be blank!"
        return render_template('creds.html', message=message)

    if password == "":
        message = "Password cannot be blank!"
        return render_template('creds.html', message=message)

    if passwordv == "":
        message = "Verification cannot be blank!"
        return render_template('creds.html', message=message)

    my_uuid = uuid.uuid4()
    my_uuid = str(my_uuid)

    entry = {
        "username": username,
        "password": password,
        "uuid" : my_uuid
    }
    res = db.creds.insert_one(entry)
    message = "Credentials saved, proceed to login"
    return render_template('login.html', message=message)

@main_app.route("/home", methods=('GET', 'POST'))
def home():
    username = request.form['username']
    password = request.form['password']
    creds = db.creds.find({"username": username})
    creds = loads(dumps(creds))

    # Looking for creds
    if creds == []:
        error = 'Invalid Username or passsword'
        return render_template('login.html', error=error)

    if username == creds[0]['username'] and password == creds[0]['password']:
        my_actions = []
        my_logs = []
        deals = db.deals.count_documents({})
        logs = db.logs.count_documents({})
        actions = db.actions.count_documents({})
        company = db.company.count_documents({})
        customer = db.customer.count_documents({})
        meetings = db.meetings.count_documents({})
        travel = db.travel.count_documents({})
        stats = [deals,logs,actions,company,customer,meetings,travel]

        actions = get_actions(db, username)
        for a in actions:
            number = a['number']
            action = a['action']
            due_date = a['due_date']
            owner = a['owner']
            company = a['company']
            status = a['status']
            info = [number, owner, due_date, company, action, status]
            my_actions.append(info)
        message = 'The OneTeam system recognizes  '+ username
        # rick.append('fail')
        # return stats
        return render_template('home.html', stats=stats, my_actions=my_actions, username=username, message=message)
    else:
        error = 'Invalid Username or passsword'
        return render_template('login.html', error=error)

@main_app.route("/home_again/<string:message>", methods=('GET', 'POST'))
def home_again(message):
    # Check user credentials
    username  = request.args.get('username', None)
    my_actions = []
    my_logs = []
    deals = db.deals.count_documents({})
    logs = db.logs.count_documents({})
    actions = db.actions.count_documents({})
    company = db.company.count_documents({})
    customer = db.customer.count_documents({})
    meetings = db.meetings.count_documents({})
    travel = db.travel.count_documents({})
    stats = [deals,logs,actions,company,customer,meetings,travel]


    actions = get_actions(db, username)
    for a in actions:
        number = a['number']
        action = a['action']
        due_date = a['due_date']
        owner = a['owner']
        company = a['company']
        status = a['status']
        info = [number, owner, due_date, company, action, status]
        my_actions.append(info)

    # return stats
    return render_template('home.html', stats=stats, my_actions=my_actions, username=username, message=message)

@main_app.route("/code", methods=('GET', 'POST'))
def code():
    my_code = request.form['code']
    code = db.creds.find({"uuid": my_code})
    code = loads(dumps(code))

    if my_code == 'xod442':
        return render_template('team.html')

    if code == []:
        code_message = "Invalid or non-existent signup code"
        return render_template('login.html', code_message=code_message)

    if my_code == code[0]['uuid']:
        remove_code = db.creds.delete_one({"code":my_code})
        return render_template('creds.html')
