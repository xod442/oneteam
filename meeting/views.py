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
from datetime import date
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
from utility.get_company import get_companies
from utility.get_meeting import get_meetings
from utility.get_meeting_number import get_meeting_number
import uuid

meetings_app = Blueprint('meetings_app', __name__)

db=connect()

@meetings_app.route("/add_meeting/<string:username>", methods=('GET', 'POST'))
def add_meeting(username):
    when = str(date.today())
    if request.method == 'POST':
        # Generate UUID
        my_uuid = uuid.uuid4()
        my_uuid = str(my_uuid)
        highest_record = db.meetings.find({}).sort("number", pymongo.DESCENDING).limit(1)
        meeting = loads(dumps(highest_record))
        if meeting == []:
            number = 1
        else:
            number = meeting[0]["number"] + 1
        entry = {
            "owner": username,
            "company": request.form['company'].replace("'", ""),
            "title": request.form['title'].replace("'", ""),
            "notes": request.form['notes'].replace("'", ""),
            "uuid": my_uuid,
            "number": number,
            "when": when
        }
        if entry["company"] == "unselected":
            # Get a list of Companies
            my_companies = get_companies(db)
            message = "please select a valid company to save action"
            return render_template('add_meeting.html', message=message, my_companies=my_companies, when=when, username=username)

        res = db.meetings.insert_one(entry)
        message = 'Meeting notes have been written to database'
        return redirect(url_for('main_app.home_again', username=username, message=message))

    # Get a list of Companies
    my_companies = get_companies(db)
    return render_template('add_meeting.html', my_companies=my_companies, when=str(when), username=username)

@meetings_app.route("/view_meeting/<string:username>", methods=('GET', 'POST'))
def view_meeting(username):
    if request.method == 'POST':
        title = request.form['title']
        if title == "unselected":
            my_meetings = get_meetings(db, username)
            message = "please select a valid meeting title"
            return render_template('select_meeting.html', message=message, my_meetings=my_meetings, username=username)

        when,company,title = title.split("&")
        meeting = db.meetings.find({"title":title})
        meet = loads(dumps(meeting))
        title = meet[0]['title']
        notes = meet[0]['notes']
        company = meet[0]['company']
        message = 'Viewed the meeting'
        return render_template('view_meeting.html', company=company, title=title, message=message, notes=notes, when=when, username=username)

    # Get a list of Companies
    my_meetings = get_meetings(db, username)
    return render_template('select_meeting.html', my_meetings=my_meetings, username=username)

@meetings_app.route("/edit_meeting/<string:username>", methods=('GET', 'POST'))
def edit_meeting(username):
    if request.method == 'POST':
        meeting = request.form['meeting']
        if meeting == "unselected":
            message = "please select a valid meeting"
            # Get a list of meetings
            my_meetings = get_meeting_number(db, username)
            return render_template('edit_meeting.html',my_meetings=my_meetings, message=message, username=username)

        temp = meeting.split('-')
        number = temp[0]
        number = int(number)
        meeting = db.meetings.find({"number":number})
        meet = loads(dumps(meeting))
        title = meet[0]['title']
        notes = meet[0]['notes']
        when = meet[0]['when']
        company = meet[0]['company']
        return render_template('edit_meeting_complete.html', title=title, notes=notes, company=company, when=when, number=number, username=username)

    # Get a list of meetings
    my_meetings = get_meeting_number(db, username)
    return render_template('edit_meeting.html', my_meetings=my_meetings, username=username)

@meetings_app.route("/edit_meeting_complete", methods=('GET', 'POST'))
def edit_meeting_complete():
    username = request.form['username'].replace("'", "")
    title = request.form['title'].replace("'", "")
    number = request.form['number'].replace("'", "")
    notes = request.form['notes'].replace("'", "")
    number = int(number)
    myquery = { "number": number }
    newvalues = { "$set": { "notes": notes }}
    db.meetings.update_one(myquery, newvalues)
    message = 'Meeitng notes have been updated in the database'
    return redirect(url_for('main_app.home_again', username=username, message=message))

@meetings_app.route("/delete_meeting/<string:username>", methods=('GET', 'POST'))
def delete_meeting(username):
    if request.method == 'POST':
        meet = request.form['meeting']
        if meet == "unselected":
            message = "please select a valid meeting"
            my_meetings = get_meeting_number(db, username)
            return render_template('delete_meeting.html', message=message, my_meetings=my_meetings, username=username)

        temp = meet.split('-')
        number = temp[0]
        number = int(number)
        meet = db.meetings.delete_one({"number":number})
        message = "Meeting entry has been deleted"
        return redirect(url_for('main_app.home_again', username=username, message=message))
    # Get a list of logs
    my_meetings = get_meeting_number(db, username)
    return render_template('delete_meeting.html', my_meetings=my_meetings, username=username)
