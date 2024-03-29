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
#Script to get all logs from database
def get_packing(length):
    pack = {
    "deal": 'Open',
    "ope": 'OPE-XXXXXXXXXXX',
    "price": '000'
    }
    if length == 0:
        entry = [pack,pack,pack,pack,pack,pack]
    if length == 1:
        entry = [pack,pack,pack,pack,pack]
    if length == 2:
        entry = [pack,pack,pack,pack]
    if length == 3:
        entry = [pack,pack,pack]
    if length == 4:
        entry = [pack,pack]
    if length == 5:
        entry = [pack]


    return entry
