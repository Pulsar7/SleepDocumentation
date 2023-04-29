#!
# SleepDocumentation / CLIENT
# by Benedikt Fichtner
# Python 3.10.6
#
import socket,argparse,os,sys,pytz,time
from getpass import getpass
from colorama import (Fore,init)
from datetime import datetime
from rich import (pretty,console as cons)
sys.dont_write_bytecode = True
from src import encryption


class CLIENT():
    def __init__(self,server_ip:str,server_port:int,client_port:int,encr,tz:str,client_ip:str) -> None:
        (self.server_ip,self.server_port,self.client_port,self.encr,self.timezone,self.client_ip) = (server_ip,server_port,client_port,encr,tz,client_ip)
        #
        self.info:str = Fore.RESET+"["+Fore.YELLOW+"INFO"+Fore.RESET+"] "
        self.error:str = Fore.RESET+"["+Fore.RED+"ERROR"+Fore.RESET+"]"+Fore.RED+" "
        self.warning:str = Fore.RESET+f"["+Fore.MAGENTA+"WARNING"+Fore.RESET+"] "
        self.failed:str = Fore.RED+"FAILED "+Fore.RESET
        self.success:str = Fore.GREEN+"O.K. "+Fore.RESET
        #
        self.client_up_state:bool = True
        self.server_public_key = ""
        self.buffer_size:int = 2048
        self.max_errors:int = 10
        self.buffer_start_keyword:str = "#BEGIN-BUFFERING#"
        self.buffer_stop_keyword:str = "#END-BUFFERING#"
        
    def get_now(self) -> str:
        n = datetime.now(pytz.timezone(self.timezone))
        return Fore.RESET+"["+Fore.LIGHTBLUE_EX+f"{n.day}.{n.month}.{n.year}-{n.hour}:{n.minute}:{n.second}"+Fore.RESET+"]"
    
    def create_socket(self) -> socket.socket or str:
        try:
            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # TCP
            client.bind((self.client_ip,self.client_port)) # probably not neccessary
            return client
        except Exception as error:
            return str(error) 
    
    def send(self,msg:str) -> bool or str:
        try:
            (state,encrypted_msg) = self.encr.encrypt(msg = msg, public_key = self.server_public_key)
            if state == True:
                self.client.send(encrypted_msg)
                return True
            else:
                raise Exception(encrypted_msg)
        except Exception as error:
            return str(error)
    
    def receive(self) -> tuple((bool,str)):
        try:
            (state,decrypted_msg) = self.encr.decrypt(encrypted_msg = self.client.recv(self.buffer_size))
            if self.buffer_start_keyword in decrypted_msg:
                sys.stdout.write("\r"+self.get_now()+self.info+"Buffering...")
                sys.stdout.flush()
                msg_parts:list[str] = []
                msg_parts.append(decrypted_msg.split(self.buffer_start_keyword)[1])
                counter:int = 0
                while True:
                    (state,decrypted_msg) = self.encr.decrypt(encrypted_msg = self.client.recv(self.buffer_size))
                    if self.buffer_stop_keyword in decrypted_msg:
                        msg_parts.append(decrypted_msg.split(self.buffer_stop_keyword)[0])
                        break
                    else:
                        msg_parts.append(decrypted_msg)
                decrypted_msg = "".join(msg_parts)
                del msg_parts, counter
                print(self.success)
            if state == True:
                return (True,decrypted_msg)
            else:
                raise Exception(decrypted_msg)
        except Exception as error:
            return (False,str(error))
    
    def run(self) -> None:
        print(self.get_now()+self.info+f"Server-Address: {self.server_ip}:{self.server_port}")
        print(self.get_now()+self.info+f"Timezone: {self.timezone}")
        print(self.get_now()+self.info+f"Own Port: {self.client_port}")
        print(self.get_now()+self.info+f"Client-RSA-key-size: {self.encr.rsa_key_size}")
        client = self.create_socket()
        if type(client) == socket.socket:
            self.client = client
            sys.stdout.write("\r"+self.get_now()+self.info+"Try to connect to server "+Fore.CYAN+self.server_ip+Fore.WHITE+":"+Fore.CYAN+str(self.server_port)+Fore.RESET+"...")
            sys.stdout.flush()
            b:str = ""
            try:
                self.client.connect((self.server_ip,self.server_port))
                print(self.success)
                sys.stdout.write("\r"+self.get_now()+self.info+"Exchanging keys with server...")
                sys.stdout.flush()
                server_response:bytes = self.client.recv(65507)
                if "Forbidden:" in server_response.decode():
                    raise Exception(server_response.decode())
                self.server_public_key = self.encr.import_key(key = server_response)
                self.client.send(self.encr.get_client_public_key())
                print(self.success)
                b = Fore.LIGHTBLUE_EX+"@server"+Fore.WHITE+">"+Fore.YELLOW+self.server_ip+Fore.WHITE+">"+Fore.YELLOW+str(self.server_port)+Fore.WHITE+"> "
            except Exception as error:
                print(self.failed+"\n"+self.error+str(error))
                self.client_up_state = False
            if self.client_up_state == True:
                try:
                    client_pwd = getpass(b.strip()+Fore.YELLOW+"Authentication"+Fore.RESET+">"+Fore.MAGENTA+" ")
                    state = self.send(msg = client_pwd)
                    if type(state) == bool:
                        (state,response) = self.receive()
                        if state == True:
                            if response.lower().strip() == "true":
                                print(self.get_now()+self.info+b+"Logged in")
                            else:
                                raise Exception(response)
                        else:
                            raise Exception("Receive-error -> "+response)
                    else:
                        raise Exception(response)
                except Exception as err:
                    print(self.error+"Couldn't authenticate: "+str(err))
                    self.client_up_state = False
            error_counter:int = 0
            while self.client_up_state == True:
                try:
                    try:
                        client_command:str = input(b)
                        if len(client_command) == 0 or client_command == " " or client_command == ' ' or client_command.lower().strip() == "clear":
                            if client_command.lower().strip() == "clear":
                                os.system("clear")
                        else:
                            state = self.send(msg = client_command)
                            if type(state) == bool:
                                (state,response) = self.receive()
                                if state == True:
                                    if response.lower().strip() != "exit":
                                        print(Fore.WHITE+"> "+Fore.RESET+response)
                                    else:
                                        print(Fore.LIGHTBLUE_EX+"> "+Fore.RED+"Received EXIT-Command from server")
                                        raise Exception("execute exit-command")
                                else:
                                    print(self.get_now()+self.error+"Couldn't receive response from server: "+response)
                                    error_counter += 1
                            else:
                                print(self.get_now()+self.error+"Couldn't send message to server: "+state)
                                error_counter += 1
                        if error_counter >= self.max_errors:
                            raise Exception("Too many errors!")
                    except KeyboardInterrupt:
                        raise Exception("Detected Keyboard interrupt")
                except Exception as error:
                    print(self.get_now()+self.error+str(error))
                    break
            if type(self.server_public_key) != str and self.client_up_state == True:
                state = self.send(msg = "exit")
                time.sleep(1)
            self.client.close()
            print(self.get_now()+self.info+"Closed TCP-socket")
        else:
            print(self.get_now()+self.error+f"Failed to create client-socket: {client}")



#
pretty.install()
init()
console = cons.Console()
#
default_server_ip:str = 'localhost'
client_ip:str = '0.0.0.0'
default_server_port:int = 1337
default_client_port:int = 1345
default_rsa_key_size:int = 3072
default_timezone:str = "CET"
#
parser = argparse.ArgumentParser()
parser.add_argument('-i','--ip',help=f"Server-IP (default={default_server_ip})",default=default_server_ip,type=str)
parser.add_argument('-s','--sport',help=f"Server-PORT (default={default_server_port})",default=default_server_port,type=int)
parser.add_argument('-c','--cport',help=f"Client-PORT (default={default_client_port})",default=default_client_port,type=int)
parser.add_argument('-r','--rsa',help=f"RSA-Key-Size (default={default_rsa_key_size})",default=default_rsa_key_size,type=int)
parser.add_argument('-t','--timezone',help=f"Timezone (default={default_timezone})",default=default_timezone,type=str)
args = parser.parse_args()
if args.ip == "" or args.cport == "" or args.sport == "" or args.rsa  == "" or args.timezone not in pytz.all_timezones:
    parser.print_help()
    sys.exit()
#

encr = encryption.ENCRYPTION(console = console, rsa_key_size = args.rsa)

if __name__ == '__main__':
    os.system("clear") #
    client = CLIENT(server_ip = args.ip, server_port = args.sport, 
        client_port = args.cport, encr = encr, tz = args.timezone, client_ip = client_ip)
    client.run()