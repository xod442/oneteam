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
from utility.get_lobs import get_lobs
from utility.get_actions import get_actions
from utility.action_dump_prep import prep_actions
from utility.lob_dump_prep import prep_lobs
from utility.deal_dump_prep import prep_deals
from utility.company_dump_prep import prep_company
from utility.customer_dump_prep import prep_customer
from utility.meetings_dump_prep import prep_meeting
from utility.line_writer import process_line
from utility.database import connect
from utility.get_lob_number import get_lob_number
import uuid

lobs_app = Blueprint('lobs_app', __name__)

db=connect()

@lobs_app.route("/add_lob/<string:username>", methods=('GET', 'POST'))
def add_lob(username):
    if request.method == 'POST':
        # Get count
        highest_record = db.lobs.find({}).sort("number", pymongo.DESCENDING).limit(1)
        lob = loads(dumps(highest_record))
        if lob == []:
            number = 1
        else:
            number = lob[0]["number"] + 1
        # Generate UUID
        my_uuid = uuid.uuid4()
        my_uuid = str(my_uuid)
        entry = {
            "owner": username,
            "firstname": request.form['firstname'].replace("'", ""),
            "lastname": request.form['lastname'].replace("'", ""),
            "title": request.form['title'].replace("'", ""),
            "modality": request.form['modality'].replace("'", ""),
            "number": number,
            "uuid": my_uuid,
            "when": datetime.datetime.now()
        }
        res = db.lobs.insert_one(entry)
        message = 'Line of Business information written to database'
        return redirect(url_for('main_app.home_again', username=username, message=message))

    # Check user credentials
    return render_template('add_lob.html', username=username)

@lobs_app.route("/list_lob/<string:username>", methods=('GET', 'POST'))
def list_lob(username):
    # Get a list of Actions
    my_lobs = []
    lob = db.lobs.find({})
    lobs = loads(dumps(lob))
    for lob in lobs:
        number = lob['number']
        firstname = lob['firstname']
        lastname = lob['lastname']
        title = lob['title']
        modality = lob['modality']
        info = [number,firstname,lastname,title,modality]
        my_lobs.append(info)

    # Check user credentials
    message = 'Return from listing'
    return render_template('list_lobs.html', my_lobs=my_lobs, username=username, message=message)

@lobs_app.route("/edit_lob/<string:username>", methods=('GET', 'POST'))
def edit_lob(username):
    if request.method == 'POST':
        lob_info = request.form['lob_info']
        if lob_info == "unselected":
            message = "please select a valid lob"
            my_lobs = my_lobs = get_lob_number(db, username)
            return render_template('edit_lob.html', my_lobs=my_lobs, message=message, username=username)

        temp = lob_info.split('-')
        number = temp[0]
        number = int(number)
        lobs = db.lobs.find({"number":number})
        lob = loads(dumps(lobs))
        lob_info = lob[0]['lob_info']
        return render_template('edit_lob_complete.html', lob_info=lob_info, number=number, username=username)

    # Get a list of prep_lobs.
    my_lobs = get_lob_number(db, username)
    return render_template('edit_lob.html', my_lobs=my_lobs, username=username)

@lobs_app.route("/edit_lob_complete", methods=('GET', 'POST'))
def edit_lob_complete():
        username = request.form['username'].replace("'", "")
        number = request.form['number'].replace("'", "")
        lob_info = request.form['lob_info'].replace("'", "")
        number = int(number)
        myquery = { "number": number }
        newvalues = { "$set": { "lob_info": lob_info }}
        db.lobs.update_one(myquery, newvalues)
        message = 'Log information been updated in the database'
        return redirect(url_for('main_app.home_again', username=username, message=message))

@lobs_app.route("/delete_lob/<string:username>", methods=('GET', 'POST'))
def delete_lob(username):
    if request.method == 'POST':
        lob = request.form['lob_info']
        if lob == "unselected":
            my_lobs = get_lob_number(db, username)
            message = "please select a valid action"
            return render_template('delete_lob.html', message=message, my_lobs=my_lobs, username=username)

        temp = lob.split('-')
        number = temp[0]
        number = int(number)
        lob = db.lobs.delete_one({"number":number})
        message = "Log entry has been deleted"
        return redirect(url_for('main_app.home_again', username=username, message=message))

    # Get a list of lobs
    my_lobs = get_lob_number(db, username)
    return render_template('delete_lob.html', my_lobs=my_lobs, username=username)
