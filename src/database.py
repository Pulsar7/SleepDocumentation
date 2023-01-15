"""
@Name: Sleepdoku - Visualization
@Author: Benedikt Fichtner
@2022 (gregorianischer Kalender)/Version 2.0/Database
"""
import sys,sqlite3
from contextlib import closing


class Database():
    def __init__(self,console,db_filepath:str,tables:dict) -> None:
        (self.console,self.db_filepath,self.tables) = (console,db_filepath,tables)
        state = self.create_tables()
        if state == True:
            pass
        else:
            sys.exit()


    ### CREATE / GENERATE ELEMENTS
    
    def create_tables(self) -> bool:
        state = False
        with self.console.status(f"[yellow]Generating database..."): # ... as state:
            try:
                for table in self.tables:
                    table_elements_list = []
                    for element in self.tables[table]['elements']:
                        table_elements_list.append(f"{element} {self.tables[table]['elements'][element]}")
                    table_elements = ", ".join(table_elements_list)
                    with closing(sqlite3.connect(self.db_filepath)) as connection:
                        with closing(connection.cursor()) as cursor:
                            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({table_elements});")
                            connection.commit()
                state = True
                self.console.log(f"[green]Created {len(self.tables)} table(s)")
            except Exception as error:
                self.console.log(f"[red]Could not create all {len(self.tables)} table(s):[bold red] {str(error)}")
                state = False
        return state

    
    def create_sleep_entry(self,bedtime:str,wake_up_mood:str,notes:str,
        wake_up_time:str,date:str,wet_bed:str,table_name:str,sleep_duration:str) -> tuple((bool,str)):
        rows = self.get_element(table_name = table_name, element_name = "date", element = date)
        if type(rows) == list:
            if len(rows) == 0:
                try:
                    with closing(sqlite3.connect(self.db_filepath)) as connection:
                        with closing(connection.cursor()) as cursor:
                            cursor.execute(f"INSERT INTO {table_name} VALUES(?,?,?,?,?,?,?)", (date,bedtime,
                                wake_up_time, wake_up_mood, wet_bed, notes, sleep_duration
                            ))
                            connection.commit()
                    return (True,f"Created new sleep-entry on {date}")
                except Exception as error: # database error:
                    self.console.log(f"[red]Database error")
                    return (False,str(error))
            else:
                return (False,f"The date '{date}' already exists in database!")
        else:
            return (False,str(rows))

    ### EDIT ELEMENT

    def edit_sleep_entry(self,new_values:dict,date:str) -> bool or str:
        try:
            with closing(sqlite3.connect(self.db_filepath)) as connection:
                with closing(connection.cursor()) as cursor:
                    for element in new_values:
                        key = None
                        for key in element.keys():
                            key = key
                        cursor.execute(f"UPDATE Days SET {key} = ? WHERE date = ?", (
                            element[key],date))
                        connection.commit()
            return True
        except Exception as error:
            self.console.log(f"[red]Database error")
            return str(error)

    ### GET ELEMENT

    def sort_date_data(self,dates:list[str],rows:list) -> list[str]:
        sorted_dates:list[str] = []
        sorted_rows:list = []
        data:dict = {}
        years:list = []
        for date in dates:
            args:list = date.split("-")
            year:str = args[2]
            month:str = args[1]
            day:str = args[0]
            if year not in data.keys():
                data[year] = {}
            if month not in data[year].keys():
                data[year][month] = []
            data[year][month].append(day)
        sorted_years:list = sorted(data.keys())
        for year in sorted_years:
            for month in data[year]:
                data[year][month] = sorted(data[year][month])
                for day in data[year][month]:
                    sorted_dates.append(f"{day}-{month}-{year}")
        for x, row in enumerate(rows, 0):
            elements:list = [row[i] for i in range(1,len(row))]
            elements.insert(0,sorted_dates[x])
            sorted_rows.append(elements)
        return sorted_rows

    def get_all_entries(self) -> list or str:
        try:
            with closing(sqlite3.connect(self.db_filepath)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(f"SELECT * FROM Days")
                    data_rows = cursor.fetchall()
                    connection.commit()
            rows:list = []
            dates:list = []
            for row in data_rows:
                rows.append(row)
                dates.append(row[0])
            return self.sort_date_data(dates = dates, rows = rows)
        except Exception as error: # database error:
            self.console.log(f"[red]Database error:[bold red] {str(error)}")
            return str(error)

    def count_all_entries(self) -> int or str:
        try:
            with closing(sqlite3.connect(self.db_filepath)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(f"SELECT * FROM Days")
                    data_rows = cursor.fetchall()
                    connection.commit()
            rows:list = []
            for row in data_rows:
                rows.append(row)
            return len(rows)
        except Exception as error: # database error:
            self.console.log(f"[red]Database error")
            return str(error)

    def get_day(self,date:str) -> list or str:
        rows = self.get_element(table_name = "Days", element_name = "date", element = date)
        if type(rows) == list:
            pass
        return rows

    def get_element(self,table_name:str,element:str,element_name:str) -> str or Exception:
        """
        SELECT * FROM ? WHERE ?=?", (table_name,element_name,element,)
        """
        try:
            with closing(sqlite3.connect(self.db_filepath)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(f"SELECT * FROM {table_name} WHERE {element_name} = ?", (element,))
                    data_rows = cursor.fetchall()
                    connection.commit()
            rows:list = []
            for row in data_rows:
                rows.append(row)
            return rows
        except Exception as error: # database error:
            self.console.log(f"[red]Database error")
            return error
        

    ### DELETE ELEMENT

    def delete_entry(self,date:str) -> bool or str:
        try:
            with closing(sqlite3.connect(self.db_filepath)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute("DELETE FROM Days WHERE date = ?", (date,))
                    connection.commit()
            return True
        except Exception as error: # database error:
            self.console.log(f"[red]Database error")
            return str(error)