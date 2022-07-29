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
from utility.get_company_number import get_company_number
import uuid

company_app = Blueprint('company_app', __name__)

db=connect()

@company_app.route("/add_company/<string:username>", methods=('GET', 'POST'))
def add_company(username):
    if request.method == 'POST':
        # Generate UUID
        my_uuid = uuid.uuid4()
        my_uuid = str(my_uuid)
        highest_record = db.company.find({}).sort("number", pymongo.DESCENDING).limit(1)
        company = loads(dumps(highest_record))
        if company == []:
            number = 1
        else:
            number = company[0]["number"] + 1

        entry = {
            "name": request.form['company'].replace("'", ""),
            "uuid": my_uuid,
            "number": number,
            "when": datetime.datetime.now()
        }
        res = db.company.insert_one(entry)
        message = 'Company information written to database'
        return redirect(url_for('main_app.home_again', username=username, message=message))
    # Check user credentials
    return render_template('add_company.html', username=username)



@company_app.route("/list_company/<string:username>", methods=('GET', 'POST'))
def list_company(username):
    # Get a list of Companies
    my_companies = []
    companies = db.company.find({})
    company = loads(dumps(companies))
    for c in company:
        name = c['name']
        number = c['number']
        info = [number, name]
        my_companies.append(info)
    message = 'Return from listing'
    return render_template('list_company.html', my_companies=my_companies, username=username, message=message)


    # Check user credentials
    message = 'Return from listing'
    return render_template('list_logs.html', my_logs=my_logs, username=username, message=message)

@company_app.route("/delete_company/<string:username>", methods=('GET', 'POST'))
def delete_company(username):
    if request.method == 'POST':
        comp = request.form['company']
        if comp == "unselected":
            message = "please select a valid company"
            my_companies = get_company_number(db)
            return render_template('delete_company.html', message=message, my_companies=my_companies, username=username)

        temp = comp.split('-')
        number = temp[0]
        number = int(number)
        meet = db.company.delete_one({"number":number})
        message = "Company entry has been deleted"
        return redirect(url_for('main_app.home_again', username=username, message=message))
    # Get a list of logs
    my_companies = get_company_number(db)
    return render_template('delete_company.html', my_companies=my_companies, username=username)
