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
from utility.get_log_number import get_log_number
from utility.get_meeting_all import get_meetings_all
from utility.get_actions_all import get_actions_all
import uuid

list_app = Blueprint('list_app', __name__)

db=connect()

@list_app.route("/list_actions/<string:username>", methods=('GET', 'POST'))
def list_actions(username):
    # Get a list of Actions
    list_actions = []
    actions = get_actions_all(db)
    for act in actions:
        owner = act['username']
        number = act['number']
        company = act['company']
        action = act['action']
        status = act['status']
        info = [owner, number, company, action, status]
        list_actions.append(info)
    return render_template('list_actions.html', my_actions=list_actions, username=username)

@list_app.route("/deals_list/<string:username>", methods=('GET', 'POST'))
def deals_list(username):
    # Get a list of Deals
    my_deals = []
    deal = db.deals.find({})
    deals = loads(dumps(deal))
    for d in deals:
        owner = d['username']
        number = d['number']
        company = d['company']
        partner = d['partner']
        status = d['status']
        deal = d['deal']
        thoughts = d['thoughts']
        notes = d['notes']
        info = [owner, number, company, partner, deal, status, thoughts, notes]
        my_deals.append(info)
    return render_template('list_deals.html', my_deals=my_deals, username=username)

@list_app.route("/all_meeting/<string:username>", methods=('GET', 'POST'))
def all_meeting(username):
    if request.method == 'POST':
        title = request.form['title']
        if title == "unselected":
            my_meetings = get_meetings_all(db)
            message = "please select a valid meeting title"
            return render_template('select_meeting.html', message=message, my_meetings=my_meetings, username=username)

        when,title = title.split(":")
        meeting = db.meetings.find({"title":title})
        meet = loads(dumps(meeting))
        title = meet[0]['title']
        notes = meet[0]['notes']
        company = meet[0]['company']
        return render_template('view_meeting.html', company=company, title=title, notes=notes, when=when, username=username)

    # Get a list of Companies
    my_meetings = get_meetings_all(db)
    return render_template('select_meeting.html', my_meetings=my_meetings, username=username)
