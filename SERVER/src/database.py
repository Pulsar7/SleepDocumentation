#!
# SleepDocumentation / SERVER / database.py
# by Benedikt Fichtner
# Python 3.10.6
#
import sqlite3,random,string
from contextlib import closing


class DATABASE():
    def __init__(self,console,conf,db_filepath:str) -> None:
        (self.console,self.conf,self.db_filepath) = (console,conf,db_filepath)
        #
        self.tables:dict = conf.get("database","tables")
        self.sleep_data_table_name:str = "SleepData"
        self.blacklist_data_table_name:str = "Blacklist"
        self.entry_id_len:int = self.tables[self.sleep_data_table_name]['entry_id_len']
        #
    
    def create_tables(self) -> bool:
        state = False
        with self.console.status(f"[yellow]Creating tables..."): # ... as state:
            try:
                for table in self.tables:
                    table_elements = ", ".join([value.split(" ")[0] for value in self.tables[table]['values']])
                    with closing(sqlite3.connect(self.db_filepath)) as connection:
                        with closing(connection.cursor()) as cursor:
                            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({table_elements});")
                            connection.commit()
                state = True
                self.console.log(f"[green]Created {len(self.tables)} table(s)")
                del table_elements
            except Exception as error:
                self.console.log(f"[red]Could not create all {len(self.tables)} table(s):[bold red] {str(error)}")
                state = False
        return state
    
    def generate_entry_id(self) -> str:
        generated_id:str = ""
        while True:
            generated_id_elements:list[str] = []
            for i in range(0,self.entry_id_len):
                if random.randint(0,1) == 1:
                    element:str = str(random.randint(0,9))
                else:
                    element:str = random.choice(string.ascii_letters)
                generated_id_elements.append(element)
            generated_id = "".join(generated_id_elements)
            if self.check_if_entry_id_exists(entry_id = generated_id) == False:
                break
        return generated_id
                
    def create_entry(self,data:dict) -> tuple((bool,str)):
        rows:list or str = self.get_element(table_name = self.sleep_data_table_name, element_name = 'date', element = data['date'])
        if type(rows) == list:
            if len(rows) == 0:
                try:
                    data['entry_id']:str = self.generate_entry_id()
                    q_marks:str = ",".join(["?" for e in data])
                    with closing(sqlite3.connect(self.db_filepath)) as connection:
                        with closing(connection.cursor()) as cursor:
                            cursor.execute(f"INSERT INTO {self.sleep_data_table_name} VALUES({q_marks});", (
                                data['entry_id'],data['date'],data['bedtime'],data['wake_up_time'],data['wake_up_mood'],
                                data['notes'],data['wet_bed'],data['at_home'],data['sleep_duration']
                            ))
                            connection.commit()
                    return (True,data['entry_id'])
                except Exception as error:
                    self.console.log("[red]Database error")
                    return (False,str(error))
            else:
                return (False,f"An entry with the date '{data['date']}' already exists in the database!")
        else:
            return (False,rows)
        
    def add_blacklist_address(self,data:dict) -> tuple((bool,str)):
        rows:list or str = self.get_element(table_name = self.blacklist_data_table_name, element_name = 'ip', element = data['ip'])
        if type(rows) == list:
            if len(rows) == 0:
                if data['ip'] not in self.conf.get("socket","whitelist"):
                    try:
                        q_marks:str = ",".join(["?" for e in data])
                        with closing(sqlite3.connect(self.db_filepath)) as connection:
                            with closing(connection.cursor()) as cursor:
                                cursor.execute(f"INSERT INTO {self.blacklist_data_table_name} VALUES({q_marks});", (
                                    data['ip'], data['reason']
                                ))
                                connection.commit()
                        return (True,"")
                    except Exception as error:
                        self.console.log("[red]Database error")
                        return (False,str(error))
                else:
                    return (False,f"The IP-Address '{data['ip']}' is in the whitelist!")
            else:
                return (False,f"An blacklist-entray with the IP-Address '{data['ip']}' already exists in the database!")
        else:
            return (False,rows)
    
    def get_element(self,element,element_name:str,table_name:str) -> list or str:
        try:
            with closing(sqlite3.connect(self.db_filepath)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(f"SELECT * FROM {table_name} WHERE {element_name} = ?;", (element,))
                    data_rows = cursor.fetchall()
                    connection.commit()
            rows:list = []
            for row in data_rows:
                rows.append(row)
            return rows
        except Exception as error:
            self.console.log(f"[red]Database error")
            return str(error)
        
    def get_sleepentry(self,date:str) -> list or str:
        return self.get_element(element = date, element_name = "date", table_name = self.sleep_data_table_name)
        
    def check_if_entry_id_exists(self,entry_id:str) -> bool:
        rows = self.get_element(element = entry_id, element_name = "entry_id", table_name = self.sleep_data_table_name)
        if type(rows) == list:
            if len(rows) > 0:
                return True
        return False
    
    def check_addr_in_blacklist(self,ip:str) -> tuple((bool,str)):
        rows = self.get_element(element = ip, element_name = "ip", table_name = self.blacklist_data_table_name)
        if type(rows) == list:
            if len(rows) > 0:
                return (True,rows[0][1])
            else:
                return (False,"")
        else:
            return (False,rows)
        
    def get_all_sleepdata_of_year(self,year:str) -> list or bool:
        try:
            with closing(sqlite3.connect(self.db_filepath)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(f"SELECT * FROM {self.sleep_data_table_name} WHERE date LIKE '%'||?||'%';",(year,))
                    data_rows = cursor.fetchall()
                    connection.commit()
            rows:list = []
            for row in data_rows:
                rows.append(row)
            return rows
        except Exception as error:
            self.console.log(f"[red]Database error")
            return str(error)
        
    def get_all_blacklist_entries(self) -> list or bool:
        try:
            with closing(sqlite3.connect(self.db_filepath)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(f"SELECT * FROM {self.blacklist_data_table_name};")
                    data_rows = cursor.fetchall()
                    connection.commit()
            rows:list = []
            for row in data_rows:
                rows.append(row)
            return rows
        except Exception as error:
            self.console.log(f"[red]Database error")
            return str(error)
        
    def delete_blacklisted_address(self,ip:str) -> tuple((bool,str)):
        (state,resp) = self.check_addr_in_blacklist(ip = ip)
        if state == True:
            try:
                with closing(sqlite3.connect(self.db_filepath)) as connection:
                    with closing(connection.cursor()) as cursor:
                        cursor.execute(f"DELETE FROM {self.blacklist_data_table_name} WHERE ip = ?;",(ip,))
                        connection.commit()
                return (True,"")
            except Exception as error:
                self.console.log(f"[red]Database error")
                return (False,str(error))
        else:
            if len(resp) == 0:
                resp = "The IP-Address is not in the blacklist!"
            return (False,resp)
        
    def delete_sleepentry(self,entry_id:str) -> tuple((bool,str)):
        state:bool = self.check_if_entry_id_exists(entry_id = entry_id)
        if state == True:
            try:
                with closing(sqlite3.connect(self.db_filepath)) as connection:
                    with closing(connection.cursor()) as cursor:
                        cursor.execute(f"DELETE FROM {self.sleep_data_table_name} WHERE entry_id = ?;",(entry_id,))
                        connection.commit()
                return (True,"")
            except Exception as error:
                self.console.log(f"[red]Database error")
                return (False,str(error))
        else:
            return (False,"There is no sleep-entry with that id")