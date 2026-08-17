from datetime import datetime, timedelta
import dotenv
import os
import bcrypt
from typing import Union

import jwt
# Load .env from Application/configuration files/.env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'configuration files', '.env')
dotenv.load_dotenv(dotenv_path=dotenv_path)
SECRET_KEY=os.getenv("SECRET_KEY")
def encodere(password:str):
    # converting password to array of bytes
    bytes = password.encode('utf-8')

    # generating the salt
    salt = bcrypt.gensalt()

    # Hashing the password
    hash = bcrypt.hashpw(bytes, salt)
    string_hash=hash.decode('utf-8')

    return string_hash

def decodere(password:str, h: Union[str, bytes]):
    checkByte = password.encode('utf-8')
    if isinstance(h, str):#if h is a string
        ogByte = h.encode('utf-8')# change to bytes
    else:
        ogByte = h
    try:
        return bcrypt.checkpw(checkByte, ogByte)# returns true if the hashes are the same , else false
    except ValueError:
        return False

