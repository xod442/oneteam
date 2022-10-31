
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
from flask import Flask
import pymongo
#

def create_app():

    app = Flask(__name__)

    from main.views import main_app
    app.register_blueprint(main_app)

    from team.views import team_app
    app.register_blueprint(team_app)

    from actions.views import actions_app
    app.register_blueprint(actions_app)

    from company.views import company_app
    app.register_blueprint(company_app)

    from customer.views import customer_app
    app.register_blueprint(customer_app)

    from deals.views import deals_app
    app.register_blueprint(deals_app)

    from logs.views import logs_app
    app.register_blueprint(logs_app)

    from meeting.views import meetings_app
    app.register_blueprint(meetings_app)

    from misc.views import misc_app
    app.register_blueprint(misc_app)

    from travel.views import travel_app
    app.register_blueprint(travel_app)

    from list.views import list_app
    app.register_blueprint(list_app)

    from deal_lobs.views import dealsx_app
    app.register_blueprint(dealsx_app)


    return app
