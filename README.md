[![Author](https://img.shields.io/badge/author-Pulsar7-lightgrey.svg?colorB=9900cc&style=flat-square)](https://github.com/Pulsar7)
[![Release](https://img.shields.io/github/release/dmhendricks/file-icon-vectors.svg?style=flat-square)](https://github.com/Pulsar7/Schlafdokumentation/releases)
[![Twitter](https://img.shields.io/twitter/url/https/github.com/dmhendricks/file-icon-vectors.svg?style=social)](https://twitter.com/SevenPulsar)

# Schlafdokumentation
A precise overview of your own sleep and possible influences on sleeping behavior. 
**But**: This is not a scientific proven script. It only shows you some variables, that could have influence on your sleep behavior. It does not replace any doctor! The science behind our sleep behaviour is much more complicated than this script is able to compute.

## :pushpin: Table of contents

* :point_right: [Installation](#installation)
* :point_right: [Usage](#usage)
* :point_right: [Import](#import)
* :point_right: [ToDo](#ToDo)
* :point_right: [Suggestions & Reports](#suggestions--reports)

## Installation

:small_orange_diamond: **Download the repository from github with git and go to directory**
 
    sudo apt-get install git
    git clone https://github.com/Pulsar7/Schlafdokumentation.git
    cd Schlafdokumentation

:small_orange_diamond: **Create virtual environment & install requirements**

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    

## Usage

    python3 sleep_doku.py --file '[DATABASE_PATH].db'

or 

    python3 sleep_doku.py 

Then enter the *database-filepath* in the given input.


## Import
If there is already an existing JSON-File, the script *json_to_db.py* is able to save the content of the JSON-File
in a SQL-Database-file.

:small_orange_diamond: **The JSON-File format of every entry / SYNTAX in JSON-File:**

    {
        "MONTH": {
            "DATE": {
                "bedtime": "HH:MM",
                "wake_up_time": "HH:MM",
                "wake_up_mood": "[PERFECT,GOOD OR BAD]",
                "wet_bed": "[YES OR NO]"
            }
        }
    }

:small_blue_diamond: *MONTH* => Example: Jan

:small_blue_diamond: *DATE* => Example: 1.1.

:small_blue_diamond: *bedtime* => Example: 00:00

:small_blue_diamond: *wake_up_mood* => Example: GOOD

:small_blue_diamond: *wet_bed* => Example: NO

:small_orange_diamond: **Importing data from JSON-File in Database-file:**

    python3 json_to_db.py --file '[JSON-FILEPATH].json' --db '[DB-FILEPATH].db'

Example:

    python3 json_to_db.py --file 'my_json_file.json' --db 'my_database.db'

## ToDo
- [ ] Export visualization as PDF
- [ ] Export sleep-data in JSON
- [ ] Export sleep-data in XLSX


## Suggestions & Reports

Suggestions or errors are welcome to be [:link: reported](https://github.com/Pulsar7/Schlafdokumentation/issues)!
