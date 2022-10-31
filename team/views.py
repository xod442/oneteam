

'''
2022 wookieware.

__author__ = "@netwookie"
__credits__ = ["Rick Kauffman"]
__license__ = "Apache2"
__version__ = "1.0.0"
__maintainer__ = "Rick Kauffman"
__email__ = "rick@rickkauffman.com"
__status__ = "Prototype"

Flask script that manages team members
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

team_app = Blueprint('team_app', __name__)

db = connect()

@team_app.route("/add_code", methods=('GET', 'POST'))
def add_code():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        if first_name == "" and last_name == "":
            message = "Fields cannot be blank"
            return render_template('add_code.html', message=message)

        my_uuid = uuid.uuid4()
        my_uuid = str(my_uuid)
        entry = {
            "first_name": request.form['first_name'].replace("'", ""),
            "last_name": request.form['last_name'].replace("'", ""),
            "uuid": my_uuid,
            "when": datetime.datetime.now()
        }
        try:
            res = db.creds.insert_one(entry)
        except:
            message = "Failed to add user code to database"
            return render_template('add_code.html', message=message)

        user_info = entry['first_name']+" "+entry['last_name']+": "+entry['uuid']
        return render_template('code_gen.html', user_info=user_info)

    return render_template('add_code.html')

@team_app.route("/delete_user", methods=('GET', 'POST'))
def delete_user():
    return render_template('team.html')
