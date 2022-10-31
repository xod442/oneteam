#
import json
import uuid
import datetime

def process_line(db,dbname, line):
    line = json.loads(line)
    my_uuid = uuid.uuid4()
    my_uuid = str(my_uuid)
    if dbname == 'actions':
        count = db.actions.count_documents({})
        number = count + 1
        entry = {
            "username": line['username'],
            "action": line['action'],
            "company": line['company'],
            "owner": line['owner'],
            "notes": line['notes'],
            "due_date": line['due_date'],
            "number": number,
            "uuid": my_uuid,
            "status": line['status'],
            "when": datetime.datetime.now()
        }
        res = db.actions.insert_one(entry)
    if dbname == 'logs':
        count = db.logs.count_documents({})
        number = count + 1
        entry = {
            "owner": line['owner'],
            "log_info": line['log_info'],
            "number": number,
            "uuid": my_uuid,
            "when": datetime.datetime.now()
        }
        res = db.logs.insert_one(entry)
    if dbname == 'deals':
        count = db.deals.count_documents({})
        number = count + 1
        entry = {
            "username": line['deal'],
            "deal": line['deal'],
            "company": line['company'],
            "status": line['status'],
            "thoughts": line['thoughts'],
            "partner": line['partner'],
            "notes": line['notes'],
            "customer": line['customer'],
            "ope": line['ope'],
            "quarter": line['quarter'],
            "accountmgr": line['accountmgr'],
            "price": line['price'],
            "number": number,
            "uuid": my_uuid,
            "when": datetime.datetime.now()
        }
        res = db.deals.insert_one(entry)
    if dbname == 'company':
        count = db.company.count_documents({})
        number = count + 1
        entry = {
            "name": line['name'],
            "uuid": my_uuid,
            "number": number,
            "when": datetime.datetime.now()
        }
        res = db.company.insert_one(entry)
    if dbname == 'customer':
        count = db.customer.count_documents({})
        number = count + 1

        entry = {
            "company": line['company'],
            "name": line['name'],
            "phone": line['phone'],
            "email": line['email'],
            "uuid": my_uuid,
            "number": number,
            "when": datetime.datetime.now()
        }
        res = db.customer.insert_one(entry)
    if dbname == 'meetings':
        count = db.meetings.count_documents({})
        number = count + 1
        entry = {
            "company": line['company'],
            "title": line['title'],
            "notes": line['notes'],
            "owner": line['owner'],
            "uuid": my_uuid,
            "number": number,
            "when": datetime.datetime.now()
        }
        res = db.meetings.insert_one(entry)
    '''
    if dbname == 'travel':
        count = db.travel.count_documents({})
        number = count + 1
        entry = {
            "owner": line['owner'],
            "travel_desc": line['travel_desc'],
            "": line['date-out'],
            "": line['takeoff-out'],
            "": line['land-out'],
            "": line['flight-out'],
            "": line['date-back'],
            "": line['takeoff-back'],
            "": line['land-back'],
            "": line['flight-back'],
            "notes": line['notes'],
            "uuid": my_uuid,
            "number": number,
            "when": datetime.datetime.now()
        }
        res = db.travel.insert_one(entry)
    '''
    return
