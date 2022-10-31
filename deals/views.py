'''
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
__credits__ = ["Rick Kauffman"].
__license__ = "Apache2"
__version__ = "1.0.0"
__maintainer__ = "Rick Kauffman"
__email__ = "rick@rickkauffman.com"
__status__ = "Prototype."

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
from utility.get_deals import get_deals
import uuid
from jinja2 import Environment, FileSystemLoader

deals_app = Blueprint('deals_app', __name__)

db=connect()

@deals_app.route("/add_deal/<string:username>", methods=('GET', 'POST'))
def add_deal(username):
    if request.method == 'POST':
        # Get count
        highest_record = db.deals.find({}).sort("number", pymongo.DESCENDING).limit(1)
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
            "customer": request.form['customer'].replace('"', ""),
            "ope": request.form['ope'].replace('"', ""),
            "quarter": request.form['quarter'].replace('"', ""),
            "accountmgr": request.form['accountmgr'].replace('"', ""),
            "price": request.form['price'].replace('"', ""),
            "status": request.form['status'].replace('"', ""),
            "thoughts": request.form['thoughts'].replace('"', ""),
            "partner": request.form['partner'].replace('"', ""),
            "notes": request.form['notes'].replace('"', ""),
            "number": number,
            "uuid": my_uuid,
            "when": datetime.datetime.now()
        }
        if entry["company"] == "unselected":
            # Get a list of Companies
            my_companies = get_companies(db)
            message = "please select a valid company"
            return render_template('add_deal.html', message=message,
                                                    my_companies=my_companies,
                                                    username=username,
                                                    deal=request.form['deal'].replace("'", ""),
                                                    thoughts=request.form['thoughts'].replace("'", ""),
                                                    partner=request.form['partner'].replace("'", ""),
                                                    notes=request.form['notes'].replace("'", ""),
                                                    customer=request.form['customer'].replace('"', ""),
                                                    ope=request.form['ope'].replace('"', ""),
                                                    quarter=request.form['quarter'].replace('"', ""),
                                                    accountmgr=request.form['accountmgr'].replace('"', ""),
                                                    price=request.form['price'].replace('"', ""),
                                                    status=request.form['status'].replace('"', ""))

        res = db.deals.insert_one(entry)
        message = 'Deal information written to database'
        return redirect(url_for('main_app.home_again', message=message, username=username))

    # Get a list of Companies
    my_companies = get_companies(db)
    return render_template('add_deal.html', my_companies=my_companies, username=username)

@deals_app.route("/list_deals/<string:username>", methods=('GET', 'POST'))
def list_deals(username):
    # Get a list of Deals
    my_deals = []
    total = 0
    dev_total = 0
    deal = db.deals.find({"username": username})
    deals = loads(dumps(deal))
    for d in deals:
        number = d['number']
        status = d['status']
        price = int(d['price'])
        deal_size = price
        if status == 'dev':
            dev_total = dev_total + deal_size
        if status == 'pursuit':
            total = total + deal_size
        company = d['company']
        partner = d['partner']
        customer = d['customer']
        ope = d['ope']
        accountmgr = d['accountmgr']
        quarter = d['quarter']
        deal = d['deal']
        thoughts = d['thoughts']
        notes = d['notes']
        info = [number, quarter, accountmgr, company, customer, partner, ope, deal, price, status, thoughts, notes]
        my_deals.append(info)
    # Check user credentials
    message = 'Return from listing'
    return render_template('list_deals.html', my_deals=my_deals, total=total, dev_total=dev_total, username=username, message=message)

@deals_app.route("/edit_deals_list", methods=('GET', 'POST'))
def edit_deals_list():
    quarter = request.args.get('quarter')
    accountmgr = request.args.get('accountmgr')
    company = request.args.get('company')
    customer = request.args.get('customer')
    partner = request.args.get('partner')
    ope = request.args.get('ope')
    deal = request.args.get('deal')
    price = request.args.get('price')
    thoughts = request.args.get('thoughts')
    number = request.args.get('number')
    status = request.args.get('status')
    notes = request.args.get('notes')
    username = request.args.get('username')
    info = [partner,deal,accountmgr,quarter,status,thoughts,notes,ope,customer,number,price]
    return render_template('edit_deal_complete2.html',username=username,info=info)


@deals_app.route("/edit_deal/<string:username>", methods=('GET', 'POST'))
def edit_deal(username):
    if request.method == 'POST':
        deal = request.form['deal']
        if deal == "unselected":
            message = "please select a valid deal"
            # Get a list of deals
            my_deals = get_deals(db, username)
            return render_template('edit_deal.html', my_deals=my_deals, message=message, username=username)

        temp = deal.split('-')
        number = temp[0]
        number = int(number)
        deals = db.deals.find({"number":number})
        deal = loads(dumps(deals))
        info = [deal[0]['partner'],
                deal[0]['deal'],
                deal[0]['accountmgr'],
                deal[0]['quarter'],
                deal[0]['status'],
                deal[0]['thoughts'],
                deal[0]['notes'],
                deal[0]['ope'],
                deal[0]['customer'],
                deal[0]['number'],
                deal[0]['price']]
        return render_template('edit_deal_complete.html', info=info, username=username)


    # Get a list of deals
    my_deals = get_deals(db, username)
    return render_template('edit_deal.html', my_deals=my_deals, username=username)

@deals_app.route("/edit_deal_complete", methods=('GET', 'POST'))
def edit_deal_complete():
    username = request.form['username']
    deal = request.form['deal'].replace('"', "")
    number = request.form['number'].replace('"', "")
    status = request.form['status'].replace('"', "")
    thoughts = request.form['thoughts'].replace('"', "")
    price = request.form['price'].replace('"', "")
    partner = request.form['partner'].replace('"', "")
    notes = request.form['notes'].replace('"', "")
    customer = request.form['customer'].replace('"', "")
    ope = request.form['ope'].replace('"', "")
    accountmgr = request.form['accountmgr'].replace('"', "")
    quarter = request.form['quarter'].replace('"', "")
    number = int(number)
    myquery = { "number": number }
    newvalues = { "$set": { "deal": deal, "status": status, "thoughts": thoughts, "notes": notes, "partner": partner, "customer": customer, "ope": ope , "price": price, "quarter": quarter, "accountmgr": accountmgr}}
    db.deals.update_one(myquery, newvalues)
    message = 'Deal information been updated in the database'
    return redirect(url_for('main_app.home_again', message=message, username=username))


@deals_app.route("/edit_deal_complete2", methods=('GET', 'POST'))
def edit_deal_complete2():
    username = request.form['username']
    deal = request.form['deal'].replace('"', "")
    number = request.form['number'].replace('"', "")
    status = request.form['status'].replace('"', "")
    thoughts = request.form['thoughts'].replace('"', "")
    price = request.form['price'].replace('"', "")
    partner = request.form['partner'].replace('"', "")
    notes = request.form['notes'].replace('"', "")
    customer = request.form['customer'].replace('"', "")
    ope = request.form['ope'].replace('"', "")
    accountmgr = request.form['accountmgr'].replace('"', "")
    quarter = request.form['quarter'].replace('"', "")
    number = int(number)
    myquery = { "number": number }
    newvalues = { "$set": { "deal": deal, "status": status, "thoughts": thoughts, "notes": notes, "partner": partner, "customer": customer, "ope": ope , "price": price, "quarter": quarter, "accountmgr": accountmgr}}
    db.deals.update_one(myquery, newvalues)
    return redirect(url_for('deals_app.list_deals', username=username))


@deals_app.route("/delete_deal/<string:username>", methods=('GET', 'POST'))
def delete_deal(username):
    if request.method == 'POST':
        deal = request.form['deal']
        if deal == "unselected":
            message = "please select a valid deal"
            # Get a list of deals
            my_deals = get_deals(db, username)
            return render_template('delete_deal.html', message=message, my_deals=my_deals)

        temp = deal.split('-')
        number = temp[0]
        number = int(number)
        action = db.deals.delete_one({"number":number})
        message = "The Deal has been deleted"
        return redirect(url_for('main_app.home_again', message=message, username=username))

    # Get a list of deals
    my_deals = get_deals(db, username)
    return render_template('delete_deal.html', my_deals=my_deals, username=username)

@deals_app.route("/deals_report/<string:username>", methods=('GET', 'POST'))
def deals_report(username):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('deal_report.html')
    # Get a list of Deals
    my_deals = []
    total = 0
    dev_total = 0
    deal = db.deals.find({"username": username} ,{'_id': 0})
    deals = loads(dumps(deal))
    for d in deals:
        number = d['number']
        status = d['status']
        price = d['price']
        deal_size = int(price)
        if status == 'dev':
            dev_total = dev_total + deal_size
        if status != 'dev':
            total = total + deal_size
        company = d['company']
        partner = d['partner']
        customer = d['customer']
        ope = d['ope']
        accountmgr = d['accountmgr']
        quarter = d['quarter']
        deal = d['deal']
        thoughts = d['thoughts']
        notes = d['notes']
        deal_size = float(deal_size)
        total = float(total)
        dev_total = float(dev_total)
        info = [number, quarter, accountmgr, company, customer, partner, ope, deal, deal_size, status, thoughts, notes]
        my_deals.append(info)

    output_from_parsed_template = template.render(my_deals=my_deals, total=total, dev_total=dev_total, username=username)
    # to save the results
    with open("oneteam_deals_report.html", "w") as fh:
        fh.write(output_from_parsed_template)
    fh.close()
    message = 'Deal information report has been generated, use the download link'
    return redirect(url_for('main_app.home_again', message=message, username=username))
