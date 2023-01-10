[![Author](https://img.shields.io/badge/author-Pulsar7-lightgrey.svg?colorB=9900cc&style=flat-square)](https://github.com/Pulsar7)
[![Release](https://img.shields.io/github/release/dmhendricks/file-icon-vectors.svg?style=flat-square)](https://github.com/Pulsar7/Schlafdokumentation/releases)
[![Twitter](https://img.shields.io/twitter/url/https/github.com/dmhendricks/file-icon-vectors.svg?style=social)](https://twitter.com/SevenPulsar)

# Schlafdokumentation
A precise overview of your own sleep and possible influences on sleeping behavior. 
**But**: This is not a scientific proven script. It only shows you some variables, that could have influence on your sleep behavior. It does not replace any doctor! The science behind our sleep behaviour is much more complicated than this script is able to compute.

## :pushpin: Table of contents

* :point_right: [Installation](#installation)
* :point_right: [Usage](#usage)
* :point_right: [Import data](#import-data)
* :point_right: [Overview](#overview)
* :point_right: [Enuresis nocturna](#enuresis-nocturna)
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

    python3 sleep_doku.py --db '[DATABASE_PATH].db'

or - enter the *database-filepath* in the given input:

    python3 sleep_doku.py 

For *help*, enter: `help`


## Import Data
If there is already an existing JSON-File, the script *json_to_db.py* is able to save the content of the JSON-File
in a SQL-Database-file.

:small_orange_diamond: **The JSON-File format of every entry / SYNTAX in JSON-File:**

    {
        "MONTH": {
            "DATE": {
                "bedtime": "HH:MM",
                "wake_up_time": "HH:MM",
                "wake_up_mood": "[PERFECT,GOOD OR BAD]",
                "wet_bed": "[YES OR NO]",
                "notes": ["note1", "note2", "note3", "note4"]
            }
        }
    }

|Element|Example|
|---|---|
|MONTH|Jan|
|DATE|1.1|
|bedtime|00:00|
|wake_up_mood|GOOD|
|wet_bed|NO|
|notes|["note1", "note2", "note3", "note4"]|

:small_orange_diamond: **Importing data from JSON-File in Database-file:**

    python3 sleep_doku.py --db '[DATABASE_PATH].db'
    > 'close'
    python3 json_to_db.py --file '[JSON-FILEPATH].json' --db '[DB-FILEPATH].db'


**Important here**: To create the 'Days'-Table in the database, you have to start the script 'sleep_doku.py' before importing your JSON-File!

Example:

    python3 sleep_doku.py --db 'my_database.db'
    > 'close'
    python3 json_to_db.py --file 'my_json_file.json' --db 'my_database.db'


## Overview
You have two options to show your sleep-data with graphics:

1. Year - Overview
2. Month - Overview


### Year-Overview
It shows you the data of all days with the given year and creates three windows: 
    
* Wet bed, Average sleep duration & Wake-up-mood
* Bedtime & Wake-Up-Time (hours:minutes)
* Sleep duration of each day (in hours)


### Month-Overview
This options shows you the data of all days in the given year and a specific month. Then it creates three windows:

* Wet bed, Average sleep duration & Wake-up-mood
    > Difference to *Year-Overview*: The average sleep duration of weeks is displayed.

* Bedtime & Wake-Up-Time (hours:minutes)
    > Difference to *Year-Overview*: Shows only the bed- & wake-up-times of the specific month.

* Sleep duration of each day (in hours)


## Enuresis nocturna

> Enuresis nocturna is defined as normal filling and normal emptying of the urinary bladder at the wrong time (sleep) and in the wrong place (bed) in a child after the age of 5. The symptom enuresis nocturna must be differentiated from primary monosymptomatic enuresis nocturna as an indication of an underlying disorder. This is possible by means of a non-invasive diagnosis that does not stress the child by means of a structured anamnesis interview, physical examination, urine examination and sonography of the urinary tract. The cause of monosymptomatic enuresis nocturna is a genetically determined wake-up disorder in the sense of a partial developmental delay. ^[Klinik und Diagnostik der Enuresis nocturna](https://link.springer.com/article/10.1007/s00112-003-0783-1)

Enuresis nocturna comes in different forms and there are millions of people who are affected by it.
In order to consequently offer help to this group of people as well, 'wet_bed' was added. 


## ToDo
- [ ] Export visualization as PDF
- [ ] Export sleep-data in JSON
- [ ] Export sleep-data in XLSX


## Suggestions & Reports

Suggestions or errors are welcome to be [:link: reported](https://github.com/Pulsar7/Schlafdokumentation/issues)!
