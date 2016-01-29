# iplogger
Very simple python server for ip log / request operations.

## Dependencies
- python3.4 or newer
- bottle, if you want to use bottlepy version

## Installation
If you have bottle installed and configured, use sh_bottle.py as your default bottle app. There are certain parameters to be configured manually (if needed):
- LIFE_TIME - lifetime of a logged ip
- REFRESH_TIME - minimal time between ip lifetime checks
- LOG_PATH, IP_PATH - paths to the server log file and ip-list backup
- STR_APP, STR_VERSION - unique strings for GET requests

There's also the direct TCP realization without any dependencies except asyncio (introduced in python 3.4). Start it by typing:

    python3 sh.py
in the terminal. It requires manual ip/port configuration in sh34.py or sh35.py depending on that version of python you have installed.

## Usage (bottle version)
- http://{host address}/log?{STR_APP}&{STR_VERSION} - logs client's ip
- http://{host address}/get?{STR_APP}&{STR_VERSION} - deletes records older than {LIFE_TIME} and returns list of logged ip's
