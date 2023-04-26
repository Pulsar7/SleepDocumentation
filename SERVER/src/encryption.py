#!
# SleepDocumentation / SERVER / encryption.py
# by Benedikt Fichtner
# Python 3.10.6
#
import hashlib,base64,sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class ENCRYPTION():
    def __init__(self,console,conf) -> None:
        (self.console,self.conf) = (console,conf)
        key_pair = self.generate_key_pair()
        if type(key_pair) == bool:
            sys.exit()
        self.server_public_key = key_pair.publickey()
        self.key_pair = key_pair
        
    def generate_key_pair(self) -> RSA.generate:
        with self.console.status("[yellow]Generating server rsa-key-pair..."): # as state:
            try:
                keyPair = RSA.generate(self.conf.get("encryption","rsa_key_size"))
                self.console.log("[green]Generated server-rsa-key-pair")
                return keyPair
            except Exception as error:
                self.console.log(f"[red]Couldn't generate server-rsa-key-pair:[bold red] {str(error)}")
        return False
    
    def get_server_public_key(self) -> bytes:
        return self.server_public_key.exportKey()
    
    def import_key(self,key:bytes) -> bool or RSA.importKey:
        this_key = None
        try:
            this_key = RSA.importKey(key.decode())
        except ValueError as error:
            return str(error)
        return this_key
    
    def encrypt(self,msg:str,public_key) -> tuple((bool,str or bytes)):
        try:
            encrypted_msg:bytes = b''
            encryptor = PKCS1_OAEP.new(public_key)
            encrypted_msg = encryptor.encrypt(msg.encode())
            return (True,base64.b64encode(encrypted_msg))
        except Exception as error:
            return (False,f"Encryption-Error: {str(error)}")
        
    def decrypt(self,encrypted_msg:bytes) -> tuple((bool,str)):
        try:
            decrypted_msg:str = ""
            decryptor = PKCS1_OAEP.new(self.key_pair)
            decrypted_msg = decryptor.decrypt(base64.b64decode(encrypted_msg))
            return (True,decrypted_msg.decode())
        except Exception as error:
            return (False,f"Decryption-Error: {str(error)}")
        
    def hash_pwd(self,password:str) -> hashlib.sha256:
        hash_object = hashlib.sha256(password.encode())
        hashed_pwd = hash_object.hexdigest()
        return hashed_pwd