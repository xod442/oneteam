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
from bson.json_util import dumps
from bson.json_util import loads
import json
#Script to get all logs from database
def prep_customer(db):
    header = '@-customer'
    cr = '\n'
    # Set filehandle
    f = open("oneteam_data.txt", "a")
    f.write(header)
    f.write(cr)
    # Get actions
    get_customer = db.customer.find({},{"_id":0, "company":1, "name":1, "phone":1, "email":1})
    json_customer = loads(dumps(get_customer))
    for item in json_customer:
        item = str(item)
        #item = item.replace("\'", "\"")
        f.write(item)
        f.write(cr)
    f.close()
    return json_customer
