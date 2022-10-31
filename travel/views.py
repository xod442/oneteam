
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
from utility.get_company import get_companies
from utility.get_travel import get_travel
from utility.get_travel_number import get_travel_number
import uuid

travel_app = Blueprint('travel_app', __name__)

db = connect()

@travel_app.route("/add_travel/<string:username>", methods=('GET', 'POST'))
def add_travel(username):
    if request.method == 'POST':
        # Get count
        highest_record = db.travel.find({}).sort("number", pymongo.DESCENDING).limit(1)
        travel = loads(dumps(highest_record))
        if travel == []:
            number = 1
        else:
            number = travel[0]["number"] + 1
        # Generate UUID
        my_uuid = uuid.uuid4()
        my_uuid = str(my_uuid)
        entry = {
            "owner": username,
            "travel-desc": request.form['travel-desc'].replace("'", ""),
            "date-out": request.form['date-out'].replace("'", ""),
            "takeoff-out": request.form['takeoff-out'].replace("'", ""),
            "land-out": request.form['land-out'].replace("'", ""),
            "flight-out": request.form['flight-out'].replace("'", ""),
            "date-back": request.form['date-back'].replace("'", ""),
            "takeoff-back": request.form['takeoff-back'].replace("'", ""),
            "land-back": request.form['land-back'].replace("'", ""),
            "flight-back": request.form['flight-back'].replace("'", ""),
            "notes": request.form['notes'].replace("'", ""),
            "number": number,
            "uuid": my_uuid,
            "when": datetime.datetime.now()
        }
        res = db.travel.insert_one(entry)
        message = 'Travel data written to database'
        return redirect(url_for('main_app.home_again', username=username, message=message))

    # Send form
    return render_template('add_travel.html', username=username)

@travel_app.route("/list_travel/<string:username>", methods=('GET', 'POST'))
def list_travel(username):
    if request.method == 'POST':
        travel_desc = request.form['travel-desc']

        if travel_desc == "unselected":
            my_travel = get_travel(db, username)
            message = "please select a valid travel description"
            return render_template('select_travel.html', message=message, my_travel=my_travel, username=username)

        travel = db.travel.find({"travel-desc":travel_desc})
        trav = loads(dumps(travel))
        date_out = trav[0]['date-out']
        takeoff_out = trav[0]['takeoff-out']
        land_out = trav[0]['land-out']
        flight_out = trav[0]['flight-out']
        date_back = trav[0]['date-back']
        takeoff_back = trav[0]['takeoff-back']
        land_back = trav[0]['land-back']
        flight_back = trav[0]['flight-back']
        notes = trav[0]['notes']
        info = [travel_desc,date_out,takeoff_out,land_out,flight_out,date_back,takeoff_back,land_back,flight_back,notes]
        message = "return from viewin travel"
        return render_template('view_travel.html', info=info, message=message, username=username)

    # Get a list of Companies
    my_travel = get_travel(db, username)
    return render_template('select_travel.html', my_travel=my_travel, username=username)

@travel_app.route("/edit_travel/<string:username>", methods=('GET', 'POST'))
def edit_travel(username):
    if request.method == 'POST':
        travel = request.form['travel']

        if travel == "unselected":
            my_travels = get_travel_number(db, username)
            message = "please select a valid travel record"
            return render_template('edit_travel.html', my_travels=my_travels, message=message, username=username)

        temp = travel.split('-')
        number = temp[0]
        number = int(number)
        travels = db.travel.find({"number":number})
        trav = loads(dumps(travels))
        date_out = trav[0]['date-out']
        takeoff_out = trav[0]['takeoff-out']
        land_out = trav[0]['land-out']
        flight_out = trav[0]['flight-out']
        date_back = trav[0]['date-back']
        takeoff_back = trav[0]['takeoff-back']
        land_back = trav[0]['land-back']
        flight_back = trav[0]['flight-back']
        notes = trav[0]['notes']
        number = str(number)
        info = [temp[1],date_out,takeoff_out,land_out,flight_out,date_back,takeoff_back,land_back,flight_back,notes,number]
        return render_template('edit_travel_complete.html', info=info, username=username)

    # Get a list of customers
    my_travels = get_travel_number(db, username)
    return render_template('edit_travel.html', my_travels=my_travels, username=username)

@travel_app.route("/edit_travel_complete", methods=('GET', 'POST'))
def edit_travel_complete():
    travel = {}
    travel['owner'] = request.form['username'].replace("'", "")
    travel['travel_desc'] = request.form['travel-desc'].replace("'", "")
    travel['date-out'] = request.form['date-out'].replace("'", "")
    travel['takeoff-out'] = request.form['takeoff-out'].replace("'", "")
    travel['land-out'] = request.form['land-out'].replace("'", "")
    travel['flight-out'] = request.form['flight-out'].replace("'", "")
    travel['date-back'] = request.form['date-back'].replace("'", "")
    travel['takeoff-back'] = request.form['takeoff-back'].replace("'", "")
    travel['land-back'] = request.form['land-back'].replace("'", "")
    travel['flight-back'] = request.form['flight-back'].replace("'", "")
    travel['notes'] = request.form['notes'].replace("'", "")
    number = request.form['number'].replace("'", "")
    username = request.form['username']
    number = int(number)
    myquery = { "number": number }
    newvalues = { "$set": travel }
    db.travel.update_one(myquery, newvalues)
    message = 'Travel information been updated in the database'
    return redirect(url_for('main_app.home_again', username=username, message=message))

@travel_app.route("/delete_travel/<string:username>", methods=('GET', 'POST'))
def delete_travel(username):
    if request.method == 'POST':
        travel = request.form['travel']
        if travel == "unselected":
            my_travels = get_travel_number(db, username)
            message = "please select a valid travel record"
            return render_template('delete_travel.html', message=message, my_travels=my_travels, username=username)

        temp = travel.split('-')
        number = temp[0]
        number = int(number)
        meet = db.travel.delete_one({"number":number})
        message = "Travel entry has been deleted"
        return redirect(url_for('main_app.home_again', username=username, message=message))

    # Get a list of logs
    my_travels = get_travel_number(db, username)
    return render_template('delete_travel.html', my_travels=my_travels, username=username)
