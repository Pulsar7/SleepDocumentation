"""
@Name: Sleepdoku - Import JSON
@Author: Benedikt Fichtner
@2022 (gregorianischer Kalender)/Version 2.0/JSON-TO-DB
"""
import sqlite3,json,argparse,sys,datetime as dt
from datetime import datetime
from contextlib import closing


def calc_sleep_duration(bedtime:str,wake_up_time:str) -> str: # copied from 'sleep_doku.py' / Version 2.0
    """ Calculating the sleep-duration hours:minutes """
    # convert time string to datetime
    start = datetime.strptime(bedtime, "%H:%M") # :%S - for seconds
    end = datetime.strptime(wake_up_time, "%H:%M") # :%S - for seconds
    delta = end - start
    if delta.days == -1: # The sleep ends on the next day
        now = datetime.now()
        bedtime = f"{now.year}/{now.month}/{now.day} "+ bedtime
        next_day = datetime.today() + dt.timedelta(days=1)
        wake_up_time = f"{next_day.year}/{next_day.month}/{next_day.day} "+wake_up_time
        this_bedtime = datetime.strptime(bedtime, "%Y/%m/%d %H:%M")
        this_wake_up_time = datetime.strptime(wake_up_time, "%Y/%m/%d %H:%M")
        delta = this_wake_up_time-this_bedtime
    delta = str(delta)
    return delta

def main(file:str,db_filepath:str) -> None:
    with open(file,'r') as json_file_data:
        data = json.load(json_file_data)
    with closing(sqlite3.connect(db_filepath)) as connection:
        with closing(connection.cursor()) as cursor:
            for month in data:
                for day in data[month]:
                    bedtime:str = data[month][day]['bedtime']
                    wake_up_time:str = data[month][day]['wake_up_time']
                    wake_up_mood:str = data[month][day]['wake_up_mood'].upper()
                    wet_bed:str = data[month][day]['wet_bed'].upper()
                    if 'notes' in data[month][day]:
                        notes:str = ", ".join(data[month][day]['notes'])
                    else:
                        notes:str = " "
                    day = day+"2022"
                    sleep_duration:str = calc_sleep_duration(bedtime = bedtime, wake_up_time = wake_up_time)
                    cursor.execute(f"INSERT INTO Days VALUES(?,?,?,?,?,?,?)", (day,bedtime,
                        wake_up_time, wake_up_mood, wet_bed, notes.upper(), sleep_duration
                    ))
                    connection.commit()

parser = argparse.ArgumentParser()
parser.add_argument('-f','--file',help="JSON-File")
parser.add_argument('-d','--db',help="DB-File")
args = parser.parse_args()
if args.file == None:
    parser.print_help()
    sys.exit()

if __name__ == '__main__':
    main(file = args.file, db_filepath = args.db)