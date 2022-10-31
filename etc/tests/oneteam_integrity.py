
'''                               ,----,.
                             ,'   ,' |
    ,---,                  ,'   .'   |
  .'  .' `\              ,----.'    .'  ,--,         ,---,
,---.'     \             |    |   .'  ,--.'|       ,---.'|
|   |  .`\  |            :    :  |--, |  |,        |   | :
:   : |  '  |  ,--.--.   :    |  ;.' \`--'_        |   | |
|   ' '  ;  : /       \  |    |      |,' ,'|     ,--.__| |
'   | ;  .  |.--.  .-. | `----'.'\   ;'  | |    /   ,'   |
|   | :  |  ' \__\/: . .   __  \  .  ||  | :   .   '  /  |
'   : | /  ;  ," .--.; | /   /\/  /  :'  : |__ '   ; |:  |
|   | '` ,/  /  /  ,.  |/ ,,/  ',-   .|  | '.'||   | '/  '
;   :  .'   ;  :   .'   \ ''\       ; ;  :    ;|   :    :|
|   ,.'     |  ,     .-./\   \    .'  |  ,   /  \   \  /
'---'        `--`---'     `--`-,-'     ---`-'    `----'



2022 wookieware.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0.

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


__author__ = "@netwookie"
__credits__ = ["Rick Kauffman"]
__license__ = "Apache2"
__version__ = "0.1.1"
__maintainer__ = "Rick Kauffman"
__email__ = "rick@rickkauffman.com"
__status__ = "Alpha"


+++++++++++++++++++++++++++++++++++++++++++++++++++++
You must copy the da5id_data.txt file to this directory ~projectx/etc/tests/

'''
import json


f = open("oneteam_data.txt", "r")
while True:
    # read a single line
    line = f.readline()
    line = line.rstrip()
    if not line:
        break
    if line[0] == "@":
        junk, dbname = line.split('-')
        line = f.readline()
        line = line.rstrip()
        line = r'{}'.format(line)
    # Prints the line as a string
    print('/////////////////////////////////////////////////////////////')
    print(line)
    print('/////////////////////////////////////////////////////////////')
    x = json.loads(line)
    # Prints the line as a JSON serialized dictionary
    # If this fails you have a quote somewhere in the string
    print(type(x))
    print('--------------------------------------------------------------------------')

    print('this is x {}'.format(x))
# close the pointer to that file
f.close()
