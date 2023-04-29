#!
# SleepDocumentation / SERVER
# by Benedikt Fichtner
# Python 3.10.6
#
import os,sys,argparse,socket,threading,pytz,time,string,datetime as dt
from rich import (pretty,console as cons)
from colorama import (init,Fore)
from datetime import datetime
sys.dont_write_bytecode = True
from src import (config,encryption,database)


class SLEEPDOCU():
    def __init__(self) -> None:
        pass
    
    def calculate_sleepduration(self,bedtime:str,wake_up_time:str) -> str:
        start = datetime.strptime(bedtime, "%H:%M") # :%S - for seconds
        end = datetime.strptime(wake_up_time, "%H:%M") # :%S - for seconds
        delta = end - start
        if delta.days == -1: # The sleep ends on the next day
            now = datetime.now()
            bedtime = f"{now.year}/{now.month}/{now.day} "+ bedtime
            next_day = dt.today() + dt.timedelta(days=1)
            wake_up_time = f"{next_day.year}/{next_day.month}/{next_day.day} "+wake_up_time
            this_bedtime = dt.strptime(bedtime, "%Y/%m/%d %H:%M")
            this_wake_up_time = dt.strptime(wake_up_time, "%Y/%m/%d %H:%M")
            delta = this_wake_up_time-this_bedtime
        delta = str(delta)
        return delta



class SERVER(SLEEPDOCU):
    def __init__(self,console:cons.Console,dbs_folder_path:str,server_ip:str,server_port:int,conf:config.CONFIG,db:database.DATABASE,encr:encryption.ENCRYPTION) -> None:
        (self.dbs_folder_path,self.console,self.server_ip,self.server_port,self.conf,self.db,self.encr
            ) = (dbs_folder_path,console,server_ip,server_port,conf,db,encr)
        self.server_up_state:bool = False
        self.timezone:str = self.conf.get("general","timezone")
        self.max_incoming_conns:int = self.conf.get("socket","max_incoming_connections")
        self.max_errors:int = self.conf.get("general","max_errors")
        self.buffer_size:int = self.conf.get("socket","buffer_size")
        self.exit_command:str = self.conf.get("socket","exit_command")
        self.max_msg_len:int = self.conf.get("socket","max_message_len")
        #
        self.info:str = Fore.RESET+"["+Fore.YELLOW+"INFO"+Fore.RESET+"] "
        self.error:str = Fore.RESET+"["+Fore.RED+"ERROR"+Fore.RESET+"]"+Fore.RED+" "
        self.warning:str = Fore.RESET+f"["+Fore.MAGENTA+"WARNING"+Fore.RESET+"] "
        self.failed:str = Fore.RED+"FAILED "+Fore.RESET
        self.success:str = Fore.GREEN+"O.K. "+Fore.RESET
        #
        self.PUB_KEYS:dict = {}
        self.LOGIN_ATTEMPTS:dict = {}
        self.commands:dict = {
            'help': {
                "help": "Shows this screen",
                "args": {}
            },
            'exit': {
                "help": "Closes connection with the server",
                "args": {}
            },
            'create-sleepentry': {
                "help": "Creates a new sleep-docu-entry",
                "args": {
                    "-date=": "Format: Day.Month.Year",
                    "-bedtime=": "Format: Hour:Minute",
                    "-wake_up_time=": "Format: Hour:Minute",
                    "-notes=": "Seperate each note with ;",
                    "-wake_up_mood=": "BAD or GOOD or PERFECT",
                    "-wet_bed=": "YES OR NO",
                    "-at_home=": "YES OR NO"
                }
            },
            'delete-sleepentry': {
                "help": "Deletes a sleep-docu-entry",
                "args": {
                    "-id=": "Just enter the entry-id"
                }
            },
            'show-sleepentries-of-year': {
                "help": "Shows all sleep-entries of a specific year",
                "args": {
                    "-year=": "Enter the year of which you want to see all sleep-entries"
                }
            },
            'show-sleepentry': {
                "help": "Shows a specific sleep-entry",
                "args": {
                    "-date=": "Enter the date of the sleep-entry"
                }
            },
            'add-blacklist': {
                "help": "Adds an IP-Address to the blacklist",
                "args": {
                    '-ip=': "IP-Address of the client",
                    '-reason=': "The reason of the block"
                }
            },
            'show-blacklist': {
                "help": "Shows all blacklist-entries",
                "args": {}
            },
            'delete-blacklisted': {
                "help": "Delete blacklisted address",
                "args": {
                    "-ip=": "IP-Address of blacklisted client"
                }
            },
            'show-connections': {
                "help": "Show all clients connected to the server",
                "args": {}
            }
        }
        super().__init__()
        
    def check_date_format(self,date:str) -> bool:
        if "." in date:
            args:list[str] = date.split(".")
            if len(args) == 3 and int(args[0]) <= 31 and int(args[1]) <= 12 and len(args[2]) > 2:
                if int(args[0]) > 0 and int(args[1]) > 0 and int(args[2]) > 0:
                    return True
        return False
    
    def check_time_format(self,time:str) -> bool:
        if ":" in time:
            args:list[str] = time.split(":")
            if len(args) == 2 and int(args[0]) < 25 and int(args[1]) < 60 and int(args[0]) >= 0 and int(args[1]) >= 0:
                return True
        return False
        
    def help(self,b:str,client_socket:socket.socket,client_msg:str) -> None:
        help_msg:str = ""
        for command in self.commands:
            help_msg += "# "+command+"\n  - HELP = "+self.commands[command]['help']+"\n  - ARGS = "+", ".join(self.commands[command]['args'])+"\n\n"
        state = self.send(client_socket = client_socket, msg = help_msg)
        if type(state) == bool:
            print(self.get_now()+self.info.strip()+b+"Sent help message")
        else:
            print(self.get_now()+self.error.strip()+b+f"Couldn't send the help-message: {state}")
        del help_msg
        
    def show_connections(self,b:str,client_socket:socket.socket,client_msg:str) -> None:
        response:str = ""
        state:str = ""
        for connection in self.PUB_KEYS:
            if connection.getpeername() == client_socket.getpeername():
                state = Fore.LIGHTYELLOW_EX+"YOU       "
            else:
                state = Fore.LIGHTGREEN_EX+"CONNECTED "
            response += state+Fore.LIGHTCYAN_EX+f"{connection.getpeername()}"+"\n"
        state = self.send(client_socket = client_socket, msg = response)
        if type(state) == bool:
            print(self.get_now()+self.info.strip()+b+"Sent connections-details")
        else:
            print(self.get_now()+self.error.strip()+b+f"Couldn't send the help-message: {state}")
        del response
        
    def get_args_from_msg(self,msg:str,arg_name:str) -> tuple((bool,dict)):
        state:bool = True
        client_args:dict = {}
        elements_client_args:dict = {}
        for arg in self.commands[arg_name]['args']:
            command_arg:str = arg.split("-")[1].split("=")[0]
            if arg in msg:
                element:str = msg.split(arg)[1]
                elements_client_args[command_arg] = element
            else:
                state = False
                break
        if state == True:
            for x,arg in enumerate(list(elements_client_args.keys())):
                if x < len(list(elements_client_args.keys()))-1:
                    next_element_arg:str = list(elements_client_args.keys())[(list(elements_client_args.keys())).index(arg)+1]
                    client_args[arg] = elements_client_args[arg].split(elements_client_args[next_element_arg])[0].split("-")[0].strip()
                else:
                    client_args[arg] = elements_client_args[arg]
        del elements_client_args
        return (state,client_args)
    
    def show_sleepentry(self,b:str,client_socket:socket.socket,client_msg:str) -> None:
        (state,client_args) = self.get_args_from_msg(msg = client_msg, arg_name = "show-sleepentry")
        if state == True:
            state:bool = self.check_date_format(date = client_args['date'])
            if state == True:
                response:str = ""
                rows:list or str = self.db.get_sleepentry(date = client_args['date'])
                if type(rows) == list:
                    if len(rows) > 0:
                        table_elements:list[str] = self.db.tables[self.db.sleep_data_table_name]['values']
                        for x,element in enumerate(rows):
                            response += Fore.LIGHTMAGENTA_EX+"- "+Fore.WHITE+"("+Fore.YELLOW+str(x+1)+Fore.WHITE+")"+Fore.RESET+f" {element[0]}\n"+"".join([Fore.CYAN+"    - "+Fore.RESET+table_elements[e].split(" ")[0]+": "+element[e]+"\n" for e in range(1,len(element))])
                        del table_elements
                        
                    else:
                        response = Fore.LIGHTRED_EX+f"There is no sleep-data for date '{client_args['date']}' in the database"
                else:
                    response = Fore.LIGHTRED_EX+f"Couldn't get sleep-entry-data for date '{client_args['date']}': {rows}"
            else:
                response = Fore.LIGHTRED_EX+f"Invalid date-format: '{client_args['date']}'"
        else:
            response = Fore.LIGHTRED_EX+"Invalid arguments for 'show-sleepentry'-command."
        if "\x1b[91" in response:
            print(self.get_now()+self.warning.strip()+b+response)
        else:
            print(self.get_now()+self.info.strip()+b+f"Show sleepentry of date {client_args['date']}")
        state = self.send(client_socket = client_socket, msg = response)
        if type(state) != bool:
            print(self.get_now()+self.error.strip()+b+f"Couldn't send a response to the client: {state}")
        del response, client_args
            
    def show_sleepentries_of_year(self,b:str,client_socket:socket.socket,client_msg:str) -> None:
        (state,client_args) = self.get_args_from_msg(msg = client_msg, arg_name = "show-sleepentries-of-year")
        if state == True:
            for str_el in string.ascii_letters:
                if str_el in client_args['year']:
                    state = False
                    break
            if state == True:
                response:str = ""
                sleep_data = self.db.get_all_sleepdata_of_year(year = client_args['year'])
                if type(sleep_data) == list:
                    if len(sleep_data) > 0:
                        table_elements:list[str] = self.db.tables[self.db.sleep_data_table_name]['values']
                        for x,element in enumerate(sleep_data):
                            response += Fore.LIGHTMAGENTA_EX+"- "+Fore.WHITE+"("+Fore.YELLOW+str(x+1)+Fore.WHITE+")"+Fore.RESET+f" {element[0]}\n"+"".join([Fore.CYAN+"  - "+Fore.RESET+table_elements[e].split(" ")[0]+": "+element[e]+"\n" for e in range(1,len(element)-1)])
                        del table_elements
                    else:
                        response = Fore.LIGHTRED_EX+"There is no sleep-data for the year "+client_args['year']+" saved in the database"
                else:
                    response = Fore.LIGHTRED_EX+f"Couldn't get all sleep-entries for the year '{client_args['year']}' from database: {sleep_data}"
            else:
                response = Fore.LIGHTRED_EX+f"Invalid year: '{client_args['year']}'"
        else:
            response = Fore.LIGHTRED_EX+"Invalid arguments for 'show-sleepentries-of-year'-command."
        if "\x1b[91" in response:
            print(self.get_now()+self.warning.strip()+b+response)
        else:
            print(self.get_now()+self.info.strip()+b+f"Show sleepentries of year {client_args['year']}")
        state = self.send(client_socket = client_socket, msg = response)
        if type(state) != bool:
            print(self.get_now()+self.error.strip()+b+f"Couldn't send a response to the client: {state}")
        del response, client_args
    
    def delete_sleepentry(self,b:str,client_socket:socket.socket,client_msg:str) -> None:
        (state,client_args) = self.get_args_from_msg(msg = client_msg, arg_name = "delete-sleepentry")
        if state == True:
            if len(client_args['id']) == self.conf.get("database","tables","SleepData","entry_id_len"):
                (state,response) = self.db.delete_sleepentry(entry_id = client_args['id'])
                if state == True:
                    response = f"Deleted sleep-entry with id {client_args['id']} from database"
                else:
                    response = Fore.LIGHTRED_EX+f"Couldn't delete the sleep-entry {client_args['id']} from database: {response}"
            else:
                response = Fore.LIGHTRED_EX+f"Invalid sleep-entry-id: '{client_args['id']}'"
        else:
            response = Fore.LIGHTRED_EX+f"Invalid arguments for 'delete-sleepentry'-command."
        print(self.get_now()+self.info.strip()+b+response)
        state = self.send(client_socket = client_socket, msg = response)
        if type(state) != bool:
            print(self.get_now()+self.error.strip()+b+f"Couldn't send a response to the client: {state}")
        del response, client_args
    
    def delete_blacklisted(self,b:str,client_socket:socket.socket,client_msg:str) -> None:
        (state,client_args) = self.get_args_from_msg(msg = client_msg, arg_name = "delete-blacklisted")
        if state == True:
            for str_el in string.ascii_letters:
                if str_el in client_args['ip']:
                    state = False
                    break
            if "." in client_args['ip'] and state == True:
                (state,response) = self.db.delete_blacklisted_address(ip = client_args['ip'])
                if state == True:
                    response = f"Deleted IP-Address {client_args['ip']} from blacklist"
                else:
                    response = Fore.LIGHTRED_EX+f"Couldn't delete IP-Address {client_args['ip']} from blacklist: {response}"
            else:
                response = Fore.LIGHTRED_EX+f"Invalid IP-Address: '{client_args['ip']}'"
        else:
            response = Fore.LIGHTRED_EX+f"Invalid arguments for 'delete-blacklisted'-command."
        print(self.get_now()+self.info.strip()+b+response)
        state = self.send(client_socket = client_socket, msg = response)
        if type(state) != bool:
            print(self.get_now()+self.error.strip()+b+f"Couldn't send a response to the client: {state}")
        del response, client_args
    
    def show_blacklist(self,b:str,client_socket:socket.socket,client_msg:str) -> None:
        response:str = ""
        blacklist_entries = self.db.get_all_blacklist_entries()
        if type(blacklist_entries) == list:
            if len(blacklist_entries) > 0:
                response = "".join([f"- IP = {entry[0]} -> Reason: {entry[1]}\n" for entry in blacklist_entries])
            else:
                response = "The blacklist is empty."
        else:
            response = Fore.LIGHTRED_EX+f"Couldn't show all blacklist-entries "+blacklist_entries
        if "\x1b[91" in response:
            print(self.get_now()+self.warning.strip()+b+response)
        else:
            print(self.get_now()+self.info.strip()+b+f"Show blacklist")
        state = self.send(client_socket = client_socket, msg = response)
        if type(state) != bool:
            print(self.get_now()+self.error.strip()+b+f"Couldn't send a response to the client: {state}")
        del response, blacklist_entries
        
    def add_blacklist(self,b:str,client_socket:socket.socket,client_msg:str) -> None:
        response:str = ""
        (state,client_args) = self.get_args_from_msg(msg = client_msg, arg_name = "add-blacklist")
        if state == True:
            for str_el in string.ascii_letters:
                if str_el in client_args['ip']:
                    state = False
                    break
            if "." in client_args['ip'] and state == True:
                (state,response) = self.db.add_blacklist_address(data = client_args)
                if state == True:
                    response = f"Added blacklist-entry for IP-Address {client_args['ip']}"
                else:
                    response = Fore.LIGHTRED_EX+f"Couldn't add blacklist-entry: {response}"
            else:
                response = Fore.LIGHTRED_EX+f"Invalid IP-Address: '{client_args['ip']}'"
        else:
            response = Fore.LIGHTRED_EX+f"Invalid arguments for 'add-blacklist'-command."
        print(self.get_now()+self.info.strip()+b+response)
        state = self.send(client_socket = client_socket, msg = response)
        if type(state) != bool:
            print(self.get_now()+self.error.strip()+b+f"Couldn't send a response to the client: {state}")
        del response, client_args
        
    def check_entered_sleepdata(self,client_args:dict) -> tuple((bool,str)):
        state:bool = self.check_date_format(date = client_args['date'])
        if state == True:
            state:bool = self.check_time_format(time = client_args['bedtime'])
            if state == True:
                state:bool = self.check_time_format(time = client_args['wake_up_time'])
                if state == True:
                    if client_args['at_home'].upper() in ["YES","NO"]:
                        if client_args['wet_bed'].upper() in ["YES","NO"]:
                            if client_args['wake_up_mood'].upper() in ["GOOD","BAD","PERFECT"]:
                                return (True,"")
                            else:
                                response = Fore.LIGHTRED_EX+f"Invalid option for 'wake_up_mood': '{client_args['wake_up_mood']}' | Valid options: BAD or GOOD or PERFECT"
                        else:
                            response = Fore.LIGHTRED_EX+f"Invalid option for 'wet_bed': '{client_args['wet_bed']}' | Valid options: YES or NO"
                    else:
                        response = Fore.LIGHTRED_EX+f"Invalid option for 'at_home': '{client_args['at_home']}' | Valid options: YES or NO"
                else:
                    response = Fore.LIGHTRED_EX+f"Invalid time-format for wake_up_time: '{client_args['wake_up_time']}'"
            else:
                response = Fore.LIGHTRED_EX+f"Invalid time-format for bedtime: '{client_args['bedtime']}'"
        else:
            response = Fore.LIGHTRED_EX+f"Invalid date-format: '{client_args['date']}'"
        return (False,response)
        
    def create_sleepentry(self,b:str,client_socket:socket.socket,client_msg:str) -> None:
        response:str = ""
        (state,client_args) = self.get_args_from_msg(msg = client_msg, arg_name = "create-sleepentry")
        if state == True:
            (state,response) = self.check_entered_sleepdata(client_args = client_args)
            if state == True:
                client_args['sleep_duration'] = self.calculate_sleepduration(bedtime = client_args['bedtime'], wake_up_time = client_args['wake_up_time'])
                (state,entry_id) = self.db.create_entry(data = client_args)
                if state == True:
                    response = f"Added entry at date {client_args['date']} with entry-id "+Fore.LIGHTCYAN_EX+f"'{entry_id}'"
                else:
                    response = Fore.LIGHTRED_EX+f"Couldn't add entry: {entry_id}"
        else:
            response = Fore.LIGHTRED_EX+f"Invalid arguments for 'create-sleepentry'-command."
        print(self.get_now()+self.info.strip()+b+response)
        state = self.send(client_socket = client_socket, msg = response)
        if type(state) != bool:
            print(self.get_now()+self.error.strip()+b+f"Couldn't send a response to the client: {state}")
        del response, client_args
            
        
    def get_now(self) -> str:
        n = datetime.now(pytz.timezone(self.timezone))
        return Fore.RESET+"["+Fore.LIGHTBLUE_EX+f"{n.day}.{n.month}.{n.year}-{n.hour}:{n.minute}:{n.second}"+Fore.RESET+"]"
        
    def create_socket(self) -> socket.socket or bool:
        sys.stdout.write("\r"+self.get_now()+self.info+"Creating TCP-socket at "+Fore.CYAN+f"{self.server_ip}"+Fore.WHITE+":"+Fore.CYAN+f"{self.server_port}"+Fore.WHITE+"...")
        sys.stdout.flush()
        try:
            server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # TCP
            server.bind((self.server_ip,self.server_port))
            server.listen(self.max_incoming_conns)
            print(self.success)
            return server
        except Exception as error:
            print(self.failed)
            print(self.get_now()+self.error+str(error))
            return False
        
    def send(self,client_socket:socket.socket,msg:str) -> bool or str:
        try:
            if len(msg) > self.max_msg_len:
                (state,encrypted_msg) = self.encr.encrypt(msg = self.conf.get("socket","buffer_start_keyword"), public_key = self.PUB_KEYS[client_socket])
                if state == True:
                    client_socket.send(encrypted_msg)
                else:
                    raise Exception(encrypted_msg)
                to_send_msg:str = msg
                last:bool = False
                counter:int = len(to_send_msg)
                start_point:int = 0
                while last == False:
                    frag:list[str] = []
                    for i in range(start_point,start_point+self.max_msg_len):
                        counter -= 1
                        start_point += 1
                        frag.append(to_send_msg[i])
                        if counter == self.max_msg_len:
                            break
                    if counter == 0:
                        last = True
                    (state,encrypted_msg) = self.encr.encrypt(msg = "".join(frag), public_key = self.PUB_KEYS[client_socket])
                    if state == True:
                        client_socket.send(encrypted_msg)
                        time.sleep(0.1) ### 
                    else:
                        raise Exception(encrypted_msg)
                    if last == True:
                        (state,encrypted_msg) = self.encr.encrypt(msg = self.conf.get("socket","buffer_stop_keyword"), public_key = self.PUB_KEYS[client_socket])
                        if state == True:
                            client_socket.send(encrypted_msg)
                        else:
                            raise Exception(encrypted_msg)
                        break
                return True
            else:
                (state,encrypted_msg) = self.encr.encrypt(msg = msg, public_key = self.PUB_KEYS[client_socket])
                if state == True:
                    client_socket.send(encrypted_msg)
                    return True
                else:
                    raise Exception(encrypted_msg)
        except Exception as error:
            return str(error)
    
    def receive(self,client_socket:socket.socket) -> tuple((bool,str)):
        try:
            (state,decrypted_msg) = self.encr.decrypt(encrypted_msg = client_socket.recv(self.buffer_size))
            if state == True:
                return (True,decrypted_msg)
            else:
                raise Exception(decrypted_msg)
        except Exception as error:
            return (False,str(error))
        
    def handle_client(self,client_socket:socket.socket,client_addr:tuple) -> None:
        b:str = Fore.LIGHTBLUE_EX+" @client"+Fore.WHITE+">"+Fore.YELLOW+str(client_addr[0])+Fore.YELLOW+":"+str(client_addr[1])+Fore.WHITE+"> "
        error_counter:int = 0
        client_up_state:bool = True
        try:
            client_socket.send(self.encr.get_server_public_key())
            # print(self.get_now()+self.info.strip()+b+"Sent client the public-rsa-key")
            response = client_socket.recv(65507)
            # print(self.get_now()+self.info.strip()+b+f"Received the client public-rsa-key")
            if len(response) == len(self.encr.get_server_public_key()):
                self.PUB_KEYS[client_socket] = self.encr.import_key(key = response)
            else:
                raise Exception("The client public-rsa-key is invalid!")
        except Exception as error:
            print(self.get_now()+self.error.strip()+b+"Key-exchange failed")
            print(self.get_now()+self.error.strip()+b+str(error))
            client_up_state = False
        if client_up_state == True:
            print(self.get_now()+self.info.strip()+b+"Exchanged public-rsa-keys with client")
            (state,client_pwd) = self.receive(client_socket = client_socket)
            if state == True:
                auth_response:str = ""
                if self.conf.get("encryption","user_pwd") == self.encr.hash_pwd(password = client_pwd):
                    if client_addr[0] in list(self.LOGIN_ATTEMPTS.keys()):
                        del self.LOGIN_ATTEMPTS[client_addr[0]]
                    print(self.get_now()+self.info.strip()+b+"Received correct password from client")
                    auth_response = "True"
                else:
                    if client_addr[0] not in list(self.LOGIN_ATTEMPTS.keys()):
                        self.LOGIN_ATTEMPTS[client_addr[0]] = {
                            'time': self.get_now(),
                            'attempts': 1
                        }
                    else:
                        self.LOGIN_ATTEMPTS[client_addr[0]]['attempts'] += 1
                    print(self.get_now()+self.error.strip()+b+f"Received wrong password from client (attempts: {self.LOGIN_ATTEMPTS[client_addr[0]]['attempts']})")
                    if self.LOGIN_ATTEMPTS[client_addr[0]]['attempts'] >= self.conf.get("socket","max_login_attempts"):
                        print(self.get_now()+self.warning.strip()+b+"Too many login attempts")
                        block_reason:str = self.conf.get("socket","block_reason_for_too_many_login_attempts")
                        (state,response) = self.db.add_blacklist_address(data = {'ip':client_addr[0],'reason':block_reason})
                        if state == True:
                            print(self.get_now()+self.info.strip()+b+Fore.LIGHTYELLOW_EX+"Added this client to blacklist")
                        else:
                            print(self.get_now()+self.error.strip()+b+Fore.LIGHTRED_EX+f"Couldn't add blacklist-entry: {response}")
                        del self.LOGIN_ATTEMPTS[client_addr[0]]
                    auth_response = "Wrong password!"
                    client_up_state = False
                state = self.send(client_socket = client_socket, msg = auth_response)
                if type(state) != bool:
                    print(self.get_now()+self.error.strip()+b+"Couldn't send client response: "+state)
                    client_up_state = False
            else:
                print(self.get_now()+self.error.strip()+b+"Couldn't receive the password from client")
                print(self.get_now()+self.error.strip()+b+client_pwd)
                client_up_state = False
        while self.server_up_state == True and client_up_state == True:
            try:
                (state,client_command) = self.receive(client_socket = client_socket)
                response:str = ""
                if state == True:
                    client_comm:str = client_command.lower().strip().split(" ")[0]
                    if client_command.lower().strip() == self.exit_command:
                        print(self.get_now()+self.info.strip()+b+"Received 'exit' command. Client wants to close connection.")
                        state = self.send(client_socket = client_socket, msg = self.exit_command)
                        if type(state) == bool:
                            print(self.get_now()+self.info.strip()+b+"Sent client the 'exit' command.")
                        else:
                            print(self.get_now()+self.error.strip()+b+f"Couldn't send client the 'exit' command: {state}")
                        break
                    elif client_comm in list(self.commands.keys()):
                        client_comm = client_comm.replace("-","_").lower().strip()
                        # print(self.get_now()+self.info.strip()+b+client_comm)
                        myVars = locals()
                        myVars[client_comm] = client_comm
                        exec(f"self.{client_comm}(client_socket=client_socket,b=b,client_msg=client_command)")
                    else:
                        response = f"'{client_command}' is an unknown command!"
                        state = self.send(client_socket = client_socket, msg = response)
                        if type(state) != bool:
                            raise Exception(state)
                else:
                    raise Exception(client_command)
            except Exception as error:
                print(self.get_now()+self.error.strip()+b+str(error))
                error_counter += 1
            if error_counter >= self.max_errors:
                print(self.get_now()+self.error.strip()+b+"Too many errors!")
                break
        client_socket.close()
        print(self.get_now()+self.info.strip()+b+"Closed connection to client")
        try:
            del self.PUB_KEYS[client_socket]
        except Exception as error:
            print(self.get_now()+self.warning.strip()+b+"There is no public key from the client")
        del b
        sys.exit()
        
    def close_all_connections(self) -> None:
        self.server_up_state = False
        conns:list[str] = [connection for connection in self.PUB_KEYS]
        print(self.get_now()+self.info+f"Closing all {len(list(self.PUB_KEYS.keys()))} connections")
        for connection in conns:
            sys.stdout.write("\r"+self.get_now()+self.info+"Closing connection to "+Fore.CYAN+f"{connection.getpeername()}"+Fore.RESET+"...")
            sys.stdout.flush()
            try:
                connection.close()
                del self.PUB_KEYS[connection]
                print(self.success)
            except Exception as error:
                print(self.failed+"\n"+self.get_now()+self.error+str(error))
            
    def run(self) -> None:
        print(self.get_now()+self.info+"Started")
        server = self.create_socket()
        if type(server) != bool:
            self.server_up_state = True
            self.server = server
            print(self.get_now()+self.info+f"Listening for maximum {self.max_incoming_conns} incoming connections")
            while self.server_up_state == True:
                try:
                    try:
                        (client,addr) = self.server.accept()
                        print(self.get_now()+self.info+"New incoming connection at "+Fore.CYAN+f"{addr[0]}"+Fore.WHITE+":"+Fore.CYAN+f"{addr[1]}"+Fore.RESET)
                        (blacklisted,reason) = self.db.check_addr_in_blacklist(ip = addr[0])
                        if blacklisted == False and len(reason) == 0:
                            client_thread = threading.Thread(
                                target = self.handle_client,
                                args = (client,addr),
                                daemon = True
                            )
                            client_thread.start()
                        elif blacklisted == True and len(reason) > 0:
                            print(self.get_now()+self.warning+"The client with the address "+Fore.CYAN+f"{addr[0]}"+Fore.WHITE+":"+Fore.CYAN+f"{addr[1]}"+Fore.RESET+" was found in the blacklist!")
                            client.send(f"Forbidden: {reason}".encode())
                            client.close()
                            print(self.get_now()+self.info+"Closed connection to "+Fore.CYAN+f"{addr[0]}"+Fore.WHITE+":"+Fore.CYAN+f"{addr[1]}"+Fore.RESET)
                        else:
                            print(self.get_now()+self.error+"Couldn't check if address "+Fore.CYAN+f"{addr[0]}"+Fore.WHITE+":"+Fore.CYAN+f"{addr[1]}"+Fore.RED+f" is in the blacklist: {reason}")
                    except KeyboardInterrupt:
                        raise Exception("Keyboard interrupt detected")
                except Exception as error:
                    print(self.get_now()+self.error+f"An error occured: {str(error)}")
                    break
            if len(self.PUB_KEYS) > 0:
                print(self.get_now()+self.info+"Not accepting more incoming connections")
                self.close_all_connections()
            self.server.close()
            print(self.get_now()+self.info+"Closed TCP-socket")
        else:
            print(self.get_now()+self.error+"Failed to start server")
        self.LOGIN_ATTEMPTS.clear()
        self.PUB_KEYS.clear()
        print(self.get_now()+self.info+"Closed")


#
init()
pretty.install()
console = cons.Console()
#
conf = config.CONFIG(console = console, filepath = 'src/config.json')
#
default_server_ip:str = conf.get("socket","default_server_ip")
default_server_port:int = conf.get("socket","default_server_port")
default_db_path:str = conf.get("database","default_db_path")
#
parser = argparse.ArgumentParser()
parser.add_argument('-i','--ip',help=f"Server-IP (default='{default_server_ip}')",type=str,
    default=default_server_ip)
parser.add_argument('-p','--port',help=f"Server-PORT (default='{default_server_port}')",type=int,
    default=default_server_port)
parser.add_argument('-d','--db',help=f"Database path (default='{default_db_path}')",type=str,
    default=default_db_path)
args = parser.parse_args()
if ".db" not in args.db:
    parser.print_help()
    sys.exit()
db = database.DATABASE(console = console, conf = conf, db_filepath = args.db)
state:bool = db.create_tables()
if state == False:
    sys.exit()
#
encr = encryption.ENCRYPTION(console = console, conf = conf)
#

if __name__ == '__main__':
    # os.system("clear") # 
    server = SERVER(console = console, dbs_folder_path = args.db, server_ip = args.ip, server_port = args.port,
        conf = conf, db = db, encr = encr
    )
    server.run()