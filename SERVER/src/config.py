#!
# SleepDocumentation / SERVER / config.py
# by Benedikt Fichtner
# Python 3.10.6
#
import json


class CONFIG():
    def __init__(self,console,filepath:str) -> None:
        (self.console,self.filepath) = (console,filepath)
        
    def get(self,*args:list[str or int]):
        try:
            with open(self.filepath,'r') as json_file:
                data = json.load(json_file)
                for arg in args: data = data[arg]
        except Exception as error:
            self.console.log(f"[red]Couldn't read config-file '{self.filepath}' properly:[bold red] {str(error)}")
        return data