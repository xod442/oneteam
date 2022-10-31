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
from utility.get_company import get_companies
from utility.get_dealsx import get_deals
from utility.get_packing import get_packing
from utility.make_lob import make_lob
from utility.make_lob_blank import make_lob_blank
import uuid
from jinja2 import Environment, FileSystemLoader

dealsx_app = Blueprint('dealsx_app', __name__)

db=connect()

@dealsx_app.route("/add_dealx/<string:username>", methods=('GET', 'POST'))
def add_dealx(username):
    if request.method == 'POST':
        # Get count
        highest_record = db.dealsx.find({}).sort("number", pymongo.DESCENDING).limit(1)
        deal = loads(dumps(highest_record))
        if deal == []:
            number = 1
        else:
            number = deal[0]["number"] + 1
        # Generate UUID
        my_uuid = uuid.uuid4()
        my_uuid = str(my_uuid)

        entry = {
            "username": request.form['username'].replace("'", ""),
            "deal": request.form['deal'].replace('"', ""),
            "company": request.form['company'].replace('"', ""),
            "ope": request.form['ope'].replace('"', ""),
            "price": request.form['price'].replace('"', ""),
            "number": number,
            "uuid": my_uuid,
            "when": datetime.datetime.now()
        }
        if entry["company"] == "unselected":
            # Get a list of Companies
            message = "please select a valid company"
            return render_template('add_dealx.html', message=message,
                                                    username=username,
                                                    deal=request.form['deal'].replace("'", ""),
                                                    ope=request.form['ope'].replace('"', ""),
                                                    price=request.form['price'].replace('"', ""))

        res = db.dealsx.insert_one(entry)
        message = 'Deal information written to database'
        return redirect(url_for('main_app.home_again', message=message, username=username))

    # Get a list of Companies
    return render_template('add_dealx.html', username=username)

@dealsx_app.route("/list_dealsx/<string:username>", methods=('GET', 'POST'))
def list_dealsx(username):
    # Get a list of Deals
    my_deals = []
    deal = db.dealsx.find({})
    deals = loads(dumps(deal))
    for d in deals:
        number = d['number']
        price = int(d['price'])
        company = d['company']
        ope = d['ope']
        deal = d['deal']
        info = [number, company, ope, deal, price]
        my_deals.append(info)
    # Check user credentials
    message = 'Return from listing'
    return render_template('list_dealsx.html', my_deals=my_deals, username=username, message=message)

@dealsx_app.route("/edit_dealsx_list", methods=('GET', 'POST'))
def edit_dealsx_list():
    number = request.args.get('number')
    ope = request.args.get('ope')
    deal = request.args.get('deal')
    price = request.args.get('price')
    username = request.args.get('username')
    info = [deal,ope,price,number]
    return render_template('edit_deal_complete3.html',username=username,info=info)


@dealsx_app.route("/edit_dealx_complete3", methods=('GET', 'POST'))
def edit_dealx_complete3():
    username = request.form['username']
    deal = request.form['deal'].replace('"', "")
    number = request.form['number'].replace('"', "")
    price = request.form['price'].replace('"', "")
    ope = request.form['ope'].replace('"', "")
    number = int(number)
    myquery = { "number": number }
    newvalues = { "$set": { "deal": deal, "ope": ope , "price": price }}
    db.dealsx.update_one(myquery, newvalues)
    return redirect(url_for('dealsx_app.list_dealsx', username=username))


@dealsx_app.route("/delete_dealx/<string:username>", methods=('GET', 'POST'))
def delete_dealx(username):
    if request.method == 'POST':
        deal = request.form['deal']
        if deal == "unselected":
            message = "please select a valid deal"
            # Get a list of deals
            my_deals = get_deals(db, username)
            return render_template('delete_dealx.html', message=message, my_deals=my_deals)

        temp = deal.split('-')
        number = temp[0]
        number = int(number)
        action = db.dealsx.delete_one({"number":number})
        message = "The Deal has been deleted"
        return redirect(url_for('main_app.home_again', message=message, username=username))

    # Get a list of deals
    my_deals = get_deals(db, username)
    return render_template('delete_dealx.html', my_deals=my_deals, username=username)

@dealsx_app.route("/list_lobs/<string:username>", methods=('GET', 'POST'))
def list_lobs(username):
    position_1_lobs = []
    position_2_lobs = []
    position_3_lobs = []
    position_4_lobs = []
    position_5_lobs = []
    position_6_lobs = []

    line = []
    lines = []

    open ={}

    deal = db.dealsx.find({})
    deals = loads(dumps(deal))
    x = 0
    for d in deals:
        if d['company'] == "1":
            position_1_lobs.append(d)
        if d['company'] == "2":
            position_2_lobs.append(d)
        if d['company'] == "3":
            position_3_lobs.append(d)
        if d['company'] == "4":
            position_4_lobs.append(d)
        if d['company'] == "5":
            position_5_lobs.append(d)
        if d['company'] == "6":
            position_6_lobs.append(d)

    # Pack arrays
    length = len(position_1_lobs)
    pack = get_packing(length)
    position_1_lobs = position_1_lobs + pack

    length = len(position_2_lobs)
    pack = get_packing(length)
    position_2_lobs = position_2_lobs + pack

    length = len(position_3_lobs)
    pack = get_packing(length)
    position_3_lobs = position_3_lobs + pack

    length = len(position_4_lobs)
    pack = get_packing(length)
    position_4_lobs = position_4_lobs + pack

    length = len(position_5_lobs)
    pack = get_packing(length)
    position_5_lobs = position_5_lobs + pack

    length = len(position_6_lobs)
    pack = get_packing(length)
    position_6_lobs = position_6_lobs + pack

    while x <= 5:
        entry = make_lob(position_1_lobs[x])
        line.append(entry)

        entry = make_lob(position_2_lobs[x])
        line.append(entry)

        entry = make_lob(position_3_lobs[x])
        line.append(entry)

        entry = make_lob(position_4_lobs[x])
        line.append(entry)

        entry = make_lob(position_5_lobs[x])
        line.append(entry)

        entry = make_lob(position_6_lobs[x])
        line.append(entry)

        lines.append(line)
        line=[]
        x = x + 1
    return render_template('deal_lobs.html', lines=lines, username=username)
