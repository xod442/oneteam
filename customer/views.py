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
from utility.get_customer_number import get_customer_number
import uuid

customer_app = Blueprint('customer_app', __name__)

db=connect()

@customer_app.route("/add_customer/<string:username>", methods=('GET', 'POST'))
def add_customer(username):
    if request.method == 'POST':
        # Generate UUID
        my_uuid = uuid.uuid4()
        my_uuid = str(my_uuid)
        highest_record = db.customer.find({}).sort("number", pymongo.DESCENDING).limit(1)
        customer = loads(dumps(highest_record))
        if customer == []:
            number = 1
        else:
            number = customer[0]["number"] + 1

        name = request.form['name'].replace("'", "")
        phone = request.form['phone'].replace("'", "")
        email = request.form['email'].replace("'", "")

        entry = {
            "company": request.form['company'].replace("'", ""),
            "name": name,
            "phone": phone,
            "email": email,
            "uuid": my_uuid,
            "number": number,
            "when": datetime.datetime.now()
        }
        if entry["company"] == "unselected":
            # Get a list of Companies
            my_companies = get_companies(db)
            message = "please select a valid company to save action"
            return render_template('add_customer.html',message=message,my_companies=my_companies,name=name,phone=phone,email=email,username=username)

        res = db.customer.insert_one(entry)
        message = 'Customer information written to database'
        return redirect(url_for('main_app.home_again', username=username, message=message))

    # Get a list of Companies
    my_companies = get_companies(db)
    return render_template('add_customer.html', my_companies=my_companies, username=username)

@customer_app.route("/list_customer/<string:username>", methods=('GET', 'POST'))
def list_customer(username):
    my_customers = []
    cust = db.customer.find({})
    customer = loads(dumps(cust))
    for c in customer:
        number = c['number']
        name = c['name']
        phone = c['phone']
        email = c['email']
        company = c['company']
        info = [number, name, phone, email, company]
        my_customers.append(info)
    # Check user credentials
    message = 'Return from listing'
    return render_template('list_customer.html', my_customers=my_customers, username=username, message=message)


@customer_app.route("/edit_customer/<string:username>", methods=('GET', 'POST'))
def edit_customer(username):
    if request.method == 'POST':
        log_info = request.form['customer']
        if log_info == "unselected":
            message = "please select a valid customer"
            # Get a list of customers
            my_customers = get_customer_number(db)
            return render_template('edit_customer.html', my_customers=my_customers, message=message, username=username)

        temp = log_info.split('-')
        number = temp[0]
        number = int(number)
        customer = db.customer.find({"number":number})
        cust = loads(dumps(customer))
        name = cust[0]['name']
        phone = cust[0]['phone']
        email = cust[0]['email']
        return render_template('edit_customer_complete.html', name=name, phone=phone, email=email, number=number, username=username)

    # Get a list of customers
    my_customers = get_customer_number(db)
    return render_template('edit_customer.html', my_customers=my_customers, username=username)

@customer_app.route("/edit_customer_complete", methods=('GET', 'POST'))
def edit_customer_complete():
    username = request.form['username'].replace("'", "")
    name = request.form['name'].replace("'", "")
    number = request.form['number'].replace("'", "")
    phone = request.form['phone'].replace("'", "")
    email = request.form['email'].replace("'", "")
    number = int(number)
    myquery = { "number": number }
    newvalues = { "$set": { "name": name, "phone": phone, "email": email }}
    db.customer.update_one(myquery, newvalues)
    message = 'Customer information been updated in the database'
    return redirect(url_for('main_app.home_again', username=username, message=message))

@customer_app.route("/delete_customer/<string:username>", methods=('GET', 'POST'))
def delete_customer(username):
    if request.method == 'POST':
        cust = request.form['customer']
        if cust == "unselected":
            message = "please select a valid customer"
            my_customers = get_customer_numnber(db)
            return render_template('delete_customer.html', message=message, my_customers=my_customers, username=username)

        temp = cust.split('-')
        number = temp[0]
        number = int(number)
        meet = db.customer.delete_one({"number":number})
        message = "Customer entry has been deleted"
        return redirect(url_for('main_app.home_again', username=username, message=message))
    # Get a list of logs
    my_customer = get_customer_number(db)
    return render_template('delete_customer.html', my_customer=my_customer, username=username)
