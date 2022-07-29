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
from utility.get_actions_all import get_actions_all
from utility.get_actions_all_closed import get_actions_all_closed
from utility.select_actions import select_actions
from utility.get_company import get_companies
import uuid

actions_app = Blueprint('actions_app', __name__)

db=connect()

@actions_app.route("/add_action/<string:username>", methods=('GET', 'POST'))
def add_action(username):

    if request.method == 'POST':
        # Get count
        highest_record = db.actions.find({}).sort("number", pymongo.DESCENDING).limit(1)
        action = loads(dumps(highest_record))
        if action == []:
            number = 1
        else:
            number = action[0]["number"] + 1
        # Generate UUID
        my_uuid = uuid.uuid4()
        my_uuid = str(my_uuid)
        action = request.form['action'].replace("'", "")
        due_date = request.form['due_date'].replace("'", "")
        owner = request.form['owner'].replace("'", "")
        notes = request.form['notes'].replace("'", "")
        entry = {
            "username": username,
            "action": action,
            "owner": owner,
            "notes": notes,
            "due_date": due_date,
            "company": request.form['company'].replace("'", ""),
            "number": number,
            "uuid": my_uuid,
            "status": "open",
            "when": datetime.datetime.now()
        }
        if entry["company"] == "unselected":
            # Get a list of Companies
            my_companies = get_companies(db)
            message = "please select a valid company to save action"
            return render_template('add_action.html',message=message,
                                                     my_companies=my_companies,
                                                     action=action,
                                                     owner=owner,
                                                     notes=notes,
                                                     due_date=due_date,
                                                     username=username)

        res = db.actions.insert_one(entry)
        message = 'Action Item information written to database'
        return redirect(url_for('main_app.home_again', username=username, message=message))

    # Get a list of Companies
    my_companies = get_companies(db)
    return render_template('add_action.html', my_companies=my_companies, username=username)

@actions_app.route("/list_action/<string:username>", methods=('GET', 'POST'))
def list_action(username):
    # Get a list of Actions
    my_actions = []
    actions = get_actions_all(db)
    for act in actions:
        owner = act['owner']
        number = act['number']
        due_date = act['due_date']
        company = act['company']
        action = act['action']
        status = act['status']
        notes = act['notes']
        info = [number, owner, due_date, company, action, status, notes]
        my_actions.append(info)
    message = 'Return from listing'
    return render_template('list_actions.html', my_actions=my_actions, username=username, message=message)

@actions_app.route("/list_action_closed/<string:username>", methods=('GET', 'POST'))
def list_action_closed(username):
    # Get a list of Actions
    my_actions = []
    actions = get_actions_all_closed(db)
    for act in actions:
        owner = act['owner']
        number = act['number']
        due_date = act['due_date']
        company = act['company']
        action = act['action']
        status = act['status']
        notes = act['notes']
        info = [number, owner, due_date, company, action, status, notes]
        my_actions.append(info)
    message = 'Return from listing'
    return render_template('list_actions_closed.html', my_actions=my_actions, username=username, message=message)

@actions_app.route("/edit_action_list", methods=('GET', 'POST'))
def edit_action_list():
    action = request.args.get('action')
    number = request.args.get('number')
    due_date = request.args.get('due_date')
    status = request.args.get('status')
    owner = request.args.get('owner')
    notes = request.args.get('notes')
    username = request.args.get('username')
    return render_template('edit_action_complete2.html',action=action,owner=owner,status=status,due_date=due_date,number=number,username=username,notes=notes)

@actions_app.route("/edit_action_list_closed", methods=('GET', 'POST'))
def edit_action_list_closed():
    action = request.args.get('action')
    number = request.args.get('number')
    due_date = request.args.get('due_date')
    status = request.args.get('status')
    owner = request.args.get('owner')
    notes = request.args.get('notes')
    username = request.args.get('username')
    return render_template('edit_action_complete3.html',action=action,owner=owner,status=status,due_date=due_date,number=number,username=username,notes=notes)


@actions_app.route("/edit_action/<string:username>", methods=('GET', 'POST'))
def edit_action(username):
    if request.method == 'POST':
        action = request.form['action']
        if action == "unselected":
            message = "please select a valid action"
            # Get a list of actions
            my_actions = select_actions(db)
            return render_template('edit_action.html', my_actions=my_actions, message=message, username=username)

        temp = action.split('-')
        number = temp[0]
        number = int(number)
        action = db.actions.find({"number":number})
        act = loads(dumps(action))
        action = act[0]['action']
        due_date = act[0]['due_date']
        owner = act[0]['owner']
        notes = act[0]['notes']
        status = act[0]['status']

        return render_template('edit_action_complete.html',action=action,owner=owner,status=status,due_date=due_date,number=number,username=username,notes=notes)

    # Get a list of actions
    my_actions = select_actions(db)
    return render_template('edit_action.html', my_actions=my_actions, username=username)

@actions_app.route("/edit_action_complete", methods=('GET', 'POST'))
def edit_action_complete():
    username = request.form['username']
    action = request.form['action'].replace("'", "")
    due_date = request.form['due_date'].replace("'", "")
    owner = request.form['owner'].replace("'", "")
    number = request.form['number'].replace("'", "")
    status = request.form['status'].replace("'", "")
    notes = request.form['notes'].replace("'", "")
    number = int(number)
    myquery = { "number": number }
    newvalues = { "$set": { "action": action, "status": status, "owner": owner, "due_date": due_date, "notes": notes}}
    db.actions.update_one(myquery, newvalues)
    message = 'Action Item information been updated in the database'
    return redirect(url_for('main_app.home_again', username=username, message=message))

@actions_app.route("/edit_action_complete2", methods=('GET', 'POST'))
def edit_action_complete2():
    username = request.form['username']
    action = request.form['action'].replace("'", "")
    due_date = request.form['due_date'].replace("'", "")
    owner = request.form['owner'].replace("'", "")
    number = request.form['number'].replace("'", "")
    status = request.form['status'].replace("'", "")
    notes = request.form['notes'].replace("'", "")
    number = int(number)
    myquery = { "number": number }
    newvalues = { "$set": { "action": action, "status": status, "owner": owner, "due_date": due_date, "notes": notes}}
    db.actions.update_one(myquery, newvalues)
    return redirect(url_for('actions_app.list_action', username=username))

@actions_app.route("/edit_action_complete3", methods=('GET', 'POST'))
def edit_action_complete3():
    username = request.form['username']
    action = request.form['action'].replace("'", "")
    due_date = request.form['due_date'].replace("'", "")
    owner = request.form['owner'].replace("'", "")
    number = request.form['number'].replace("'", "")
    status = request.form['status'].replace("'", "")
    notes = request.form['notes'].replace("'", "")
    number = int(number)
    myquery = { "number": number }
    newvalues = { "$set": { "action": action, "status": status, "owner": owner, "due_date": due_date, "notes": notes}}
    db.actions.update_one(myquery, newvalues)
    return redirect(url_for('actions_app.list_action_closed', username=username))

@actions_app.route("/delete_action/<string:username>", methods=('GET', 'POST'))
def delete_action(username):
    if request.method == 'POST':
        action = request.form['action']
        if action == "unselected":

            message = "please select a valid action"
            my_actions = select_actions(db)
            return render_template('delete_action.html', message=message, my_actions=my_actions, username=username)

        temp = action.split('-')
        number = temp[0]
        number = int(number)
        action = db.actions.delete_one({"number":number})
        message = "Action item has been deleted"
        return redirect(url_for('main_app.home_again', username=username, message=message))

    # Get a list of actions
    my_actions = select_actions(db)
    return render_template('delete_action.html', my_actions=my_actions, username=username)
