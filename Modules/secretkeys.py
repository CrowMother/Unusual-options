import os
from dotenv import load_dotenv
from Modules import universal


#returns the secret based on the keyName
def load_secret(keyName):
    # load the .env file from the config folder
    load_dotenv("config/.env")
    return os.getenv(keyName)