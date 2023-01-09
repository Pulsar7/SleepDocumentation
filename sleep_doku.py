"""
@Name: Sleepdoku - Visualization
@Author: Benedikt Fichtner
@2022 (gregorianischer Kalender)/Version 2.0
"""
import sys,os, datetime as dt,argparse
from rich import (pretty, console as cons)
sys.dont_write_bytecode = True
from src import (database,visualizer)
from datetime import datetime
from rich.table import Table

class Visualization():
    def __init__(self,console:cons.Console,db,commands:dict,db_filepath:str,datetime_format:str,wake_up_moods:list[str],
            wet_bed_options:list[str],tables:dict,vis,note_seperator:str) -> None:
        (self.console,self.db,self.db_filepath,self.vis) = (console,db,db_filepath,vis)
        (self.close_command,self.commands) = ("close()",commands)
        self.datetime_format = datetime_format
        self.wake_up_moods = wake_up_moods
        self.wet_bed_options = wet_bed_options
        self.tables = tables
        self.note_seperator = note_seperator
        
    def help(self) -> None:
        self.console.rule()
        for command in self.commands:
            self.console.log(f"[yellow]{command}    [white]=[yellow]   {self.commands[command]['help']}")
        self.console.rule()

    def close(self) -> None:
        self.console.rule()
        self.console.log(f"[yellow]Exiting")
        sys.exit()

    def version(self) -> None:
        name:str = "version"
        self.console.log(f"[white]Sleep-Doku Version [bold green]{self.commands[name.upper()][name]}")

    def clear(self) -> None:
        os.system("clear") # 

    def check_time_format(self,raw_time:str) -> tuple((bool,str)):
        not_msg:str = f"{raw_time} is not a valid time-format!"
        if ":" in raw_time:
            args:list[str] = raw_time.split(":")
            if len(args) == 2:
                (hours,minutes) = (int(args[0]),int(args[1]))
                if hours > 23 or hours < 0 or minutes < 0 or minutes > 59:
                    return (False,not_msg)
                else:
                    return (True,"")
            else:
                return (False,not_msg)
        else:
            return (False,not_msg)

    def calc_sleep_duration(self,bedtime:str,wake_up_time:str) -> str:
        """ Calculating the sleep-duration hours:minutes """
        # convert time string to datetime
        start = datetime.strptime(bedtime, "%H:%M") # :%S - for seconds
        self.console.log(f"[green]Start-time: {start.time()}")
        end = datetime.strptime(wake_up_time, "%H:%M") # :%S - for seconds
        self.console.log(f"[green]End-time: {end.time()}")
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
        self.console.log(f"Sleep-Duration: {delta}")
        return delta

    def delete(self) -> None:
        self.console.rule()
        error_counter:int = 0
        max_errors:int = 10
        date:str = ""
        while (error_counter <= max_errors):
            date:str = str(self.console.input(f"[yellow]Enter the date ([white]{self.datetime_format}[yellow]):[purple] "))
            if "-" in date:
                args:list[str] = date.split("-")
                if len(args) == 3:
                    rows:str = self.db.get_day(date = date)
                    if type(rows) == list:
                        if len(rows) > 0:
                            state = self.db.delete_entry(date = date)
                            if isinstance(state,bool):
                                self.console.log(f"[green]Deleted '{date}' successfully")
                            else:
                                self.console.log(f"[red]{state}")
                        else:
                            self.console.log(f"[red]The entry '{date}' does not exist!")
                        break
                    else:
                        self.console.log(f"[red]{str(rows)}")
                else:
                    self.console.log(f"[red]'{date}' is not the correct date-format!")
            else:
                self.console.log(f"[red]'{date}' is not the correct date-format!")
            error_counter += 1 
        if error_counter == max_errors:
            self.console.log(f"[red]Couldn't delete sleep-entry of '{date}':[bold red] Too many errors!")

    def count(self) -> None:
        self.console.log(f"There are at least {self.db.count_all_entries()} entries")

    def printoutall(self) -> None:
        rows = self.db.get_all_entries()
        if isinstance(rows,list):
            table = Table(title=f"Sleep-Doku ~ {self.db_filepath}")
            table.add_column("Date", justify="left", style="cyan", no_wrap=True)
            table.add_column("Bedtime", style="magenta")
            table.add_column("Wake-Up-Time", justify="right", style="green")
            table.add_column("Wake-Up-Mood", justify="right", style="yellow")
            table.add_column("Wet-Bed", justify="right", style="blue")
            table.add_column("Sleep-Duration", justify="right", style="red")
            for row in rows:
                table.add_row(row[0],row[1],row[2],row[3],row[4],row[6])
            self.console.print(table)

    def edit(self) -> None:
        error_counter:int = 0
        max_errors:int = 10
        date:str = ""
        while (error_counter <= max_errors):
            date:str = str(self.console.input(f"[yellow]Enter the date ([white]{self.datetime_format}[yellow]):[purple] "))
            if "-" in date:
                args:list[str] = date.split("-")
                if len(args) == 3:
                    rows:str = self.db.get_day(date = date)
                    if type(rows) == list:
                        if len(rows) > 0:
                            set_command_state:bool = True
                            self.console.log("Type in all elements you want to change, syntax:")
                            keys:list = self.tables['Days']['elements'].keys()
                            x:int = 1
                            self.console.rule()
                            for key in keys:
                                if "duration" not in key and "date" not in key:
                                    self.console.log(f"({x}) set {key} = NEW VALUE")
                                x += 1
                            self.console.rule()
                            self.console.log(f"[yellow]Notes-seperator: '{self.note_seperator}'")
                            self.console.log("[yellow]Type in 'end' to finish")
                            set_commands:list[str] = []
                            while (set_command_state == True and error_counter <= max_errors):
                                set_command:str = str(self.console.input("[yellow]>[purple] ")).lower()
                                if "set" in set_command and "=" in set_command:
                                    key_element = set_command.split(" ")[1]
                                    if key_element in keys:
                                        new_value:str = set_command.split("=")[1]
                                        value:str = new_value.strip()
                                        set_commands.append({key_element:new_value})
                                        if key_element == "bedtime" or key_element == "wake_up_time":
                                            time_value:str = value
                                            (state,msg) = self.check_time_format(raw_time = time_value)
                                            if state == True:
                                                if key_element == "bedtime":
                                                    sleep_duration:str = self.calc_sleep_duration(bedtime = time_value, 
                                                        wake_up_time = rows[0][2]
                                                    )
                                                    set_commands.append({"sleep_duration":sleep_duration})
                                                else:
                                                    sleep_duration:str = self.calc_sleep_duration(bedtime = rows[0][1], 
                                                        wake_up_time = new_value
                                                    )
                                                    set_commands.append({"sleep_duration":sleep_duration})
                                            else:
                                                self.console.log(f"[red]{msg}")
                                                error_counter += 1
                                    else:
                                        self.console.log(f"[red]'{set_command}' is not a valid set-command!")
                                        error_counter += 1
                                elif set_command == "end":
                                    break
                            if len(set_commands) > 0:
                                state = self.db.edit_sleep_entry(new_values = set_commands, date = date)
                                if isinstance(state,bool):
                                    self.console.log(f"[green]Changed sleep-entry of '{date}'")
                                else:
                                    self.console.log(f"[red]{state}")
                            else:
                                self.console.log("Nothing to change...")
                        else:
                            self.console.log(f"[red]The entry '{date}' does not exist!")
                        break
                    else:
                        self.console.log(f"[red]{str(rows)}")
                else:
                    self.console.log(f"[red]'{date}' is not the correct date-format!")
            else:
                self.console.log(f"[red]'{date}' is not the correct date-format!")
            error_counter += 1 
        if error_counter == max_errors:
            self.console.log(f"[red]Couldn't edit sleep-entry of '{date}':[bold red] Too many errors!")

    def get(self) -> None:
        self.console.rule()
        error_counter:int = 0
        max_errors:int = 5
        date:str = ""
        while (error_counter <= max_errors):
            date:str = str(self.console.input(f"[yellow]Enter the date ([white]{self.datetime_format}[yellow]):[purple] "))
            if "-" in date:
                args:list[str] = date.split("-")
                if len(args) == 3:
                    rows:str = self.db.get_day(date = date)
                    if type(rows) == list:
                        if len(rows) > 0:
                            data = rows[0]
                            keys:list = self.tables['Days']['elements'].keys()
                            x:int = 0
                            for key in keys:
                                self.console.log(f"[purple]{key}[white] =[blue] {data[x]}")
                                x += 1
                        else:
                            self.console.log(f"[red]The entry '{date}' does not exist!")
                        break
                    else:
                        self.console.log(f"[red]{str(rows)}")
                else:
                    self.console.log(f"[red]'{date}' is not the correct date-format!")
            else:
                self.console.log(f"[red]'{date}' is not the correct date-format!")
            error_counter += 1
        if error_counter == max_errors:
            self.console.log(f"[red]Couldn't get sleep-entry of '{date}':[bold red] Too many errors!")

    def add(self) -> None:
        self.console.rule()
        error_counter:int = 0
        max_errors:int = 5
        while (error_counter <= max_errors):
            date:str = str(self.console.input(f"[yellow]Enter the date ([white]{self.datetime_format}[yellow]):[purple] "))
            if "-" in date:
                args:list[str] = date.split("-")
                if len(args) == 3:
                    rows:str = self.db.get_day(date = date)
                    if type(rows) == list:
                        if len(rows) > 0:
                            self.console.log(f"[red]The entry '{date}' already exists!")
                            break
                    bedtime:str = str(self.console.input("[yellow]Enter the bedtime ([white]HH:mm[yellow]):[purple] "))
                    (state,msg) = self.check_time_format(raw_time = bedtime)
                    if state == True:
                        wake_up_time:str = str(self.console.input("[yellow]Enter the wake-up-time ([white]HH:mm[yellow]):[purple] "))
                        (state,msg) = self.check_time_format(raw_time = wake_up_time)
                        if state == True:
                            wake_up_mood:str = str(
                                self.console.input(f"[yellow]Enter the wake-up-mood ([white]{', '.join(self.wake_up_moods)}[yellow]):[purple] ")).upper()
                            if wake_up_mood in self.wake_up_moods:
                                wet_bed:str = str(
                                    self.console.input(f"[yellow]Enter the wet-bed state ([white]{', '.join(self.wet_bed_options)}[yellow]):[purple] ")).upper()
                                if wet_bed in self.wet_bed_options:
                                    notes:str = str(self.console.input("[yellow]Enter the notes before bedtime ([white]note1, note2, note3[yellow]):[purple] ")).upper()
                                    sleep_duration:str = self.calc_sleep_duration(bedtime = bedtime, 
                                        wake_up_time = wake_up_time
                                    )
                                    (state,msg) = self.db.create_sleep_entry(
                                        bedtime = bedtime, wake_up_mood = wake_up_mood,
                                        wake_up_time = wake_up_time, notes = notes,
                                        wet_bed = wet_bed, date = date, table_name = 'Days',
                                        sleep_duration = sleep_duration
                                    )
                                    if state == True:
                                        self.console.log(f"[green]{msg}")
                                    else:
                                        self.console.log(f"[red]{msg}")
                                    break
                                else:
                                    self.console.log(f"[red] '{wet_bed}' is not a valid wet-bed-option!")
                            else:
                                self.console.log(f"[red] '{wake_up_mood}' is not a valid wake-up-mood!")
                        else:
                            self.console.log(f"[red]{msg}")
                    else:
                        self.console.log(f"[red]{msg}")
                else:
                    self.console.log(f"[red] '{date}' is not a valid date!")
            else:
                self.console.log(f"[red] '{date}' is not a valid date!")
            error_counter += 1
        if error_counter == max_errors:
            self.console.log("red]Couldn't create new sleep-entry:[bold red] Too many errors!")


    def show(self) -> None:
        self.console.rule()
        options = {
            "1": {
                "description": "Visualizes data of an entire year",
                "command": "show_year"
            },

            "2": {
                "description": "Visualizes data of a month",
                "command": "show_month"
            }
        }
        table = Table(title="Options to visualize")
        table.add_column("Number", justify="right", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")
        for option in options:
            table.add_row(option,options[option]['description'])
        self.console.print(table)
        number:str = str(self.console.input("[yellow]Enter Number>[purple] "))
        if number in options.keys():
            myStr = number
            myVars = locals()
            myVars[myStr] = myStr
            exec(f"self.vis.{options[number]['command']}()")
        else:
            self.console.log(f"[red]'{number}' is not a valid option!")


    def run(self) -> None:
        db_filename:str = self.db_filepath.split(".")[0]
        if "/" in self.db_filepath:
            args:list[str] = db_filename.split("/")
            db_filename = args[len(args)-1]
        while True:
            user_command:str = self.console.input(f"[white]@[purple]{db_filename.upper()}[yellow]>[white] ").upper()
            user_command = user_command.split(" ")[0]
            if user_command != "" and user_command != " ":
                if user_command in self.commands:
                    for command in self.commands:
                        if command == user_command:
                            myStr = command
                            myVars = locals()
                            myVars[myStr] = myStr
                            exec(f"self.{command.lower()}()")
                        else:
                            pass
                else:
                    self.console.log(f"[red]'{user_command}' is not a valid command!")
            else:
                pass


#
tables:dict = {
    "Days": {
        "elements": {
            "date": "string",
            "bedtime": "string",
            "wake_up_time": "string",
            "wake_up_mood": "string",
            "wet_bed": "string",
            "notes": "string",
            "sleep_duration": "string"
        }
    }
}

commands:dict = {
    "HELP": {
        "help": "Printout this window"
    },

    "CLOSE": {
        "help": "Exits the sleep-doku"
    },

    "VERSION": {
        "help": "Show the version of the sleep-doku",
        "version": 2.0
    },

    "CLEAR": {
        "help": "Clears the content in the terminal"
    },

    "ADD": {
        "help": "Creates new sleep-entry"
    },

    "GET": {
        "help": "Get data from specific date"
    },

    "EDIT": {
        "help": "Edit data from specific date"
    },

    "DELETE": {
        "help": "Delete entry from specific date"
    },
    
    "COUNT": {
        "help": "Shows the number of all entries"
    },

    "PRINTOUTALL": {
        "help": "Shows all entries"
    },

    "SHOW": {
        "help": "Options to visualize with matplotlib"
    }
}

datetime_format:str = "DD-MM-YYYY" # day.month.year
wake_up_moods:list[str] = ["PERFECT","GOOD","BAD"]
wet_bed_options:list[str] = ["YES","NO"]
note_seperator:str = ";"
#
pretty.install()
console = cons.Console()
parser = argparse.ArgumentParser()
parser.add_argument('-f','--file', help="Database filepath (example: my_data.db)")
args:list = parser.parse_args()
if args.file == None:
    parser.print_help()
    db_filepath:str = str(console.input("[yellow]Sleep-Doku[white]/[yellow]Database-Path[white]:[cyan] "))
else:
    db_filepath:str = args.file
if db_filepath == "" or db_filepath == " " or ".db" not in db_filepath:
    console.log("[red]Incorrect database filepath!")
    sys.exit()
db = database.Database(console = console, db_filepath = db_filepath, tables = tables)
vis = visualizer.VISUALIZE(console = console, db = db, tables = tables, note_seperator = note_seperator)
#

if __name__ == '__main__':
    os.system("clear")
    visualisation = Visualization(console = console, db = db, commands = commands, db_filepath = db_filepath,
        datetime_format = datetime_format, wake_up_moods = wake_up_moods, wet_bed_options = wet_bed_options, 
        tables = tables, vis = vis, note_seperator = note_seperator
    )
    visualisation.run()