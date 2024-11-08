import os
from dotenv import load_dotenv
from Modules import universal

APP_KEY = ""
SECRET = ""
APP_URL = ""

def set_secrets():
    global APP_KEY, SECRET, APP_URL
    # Get the current directory of the script
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the .env file located in the config directory
    dotenv_path = os.path.join(current_directory, '..', 'config', '.env')

    # Load the .env file
    load_dotenv(dotenv_path)

    APP_KEY = os.getenv('APP_KEY')
    SECRET = os.getenv('SECRET')
    APP_URL = os.getenv('SERVER_URL')
    check_set(APP_KEY, 'a')
    check_set(SECRET, 's')
    check_set(APP_URL, 'u')


def get_app_key():
    global APP_KEY
    if_empty(APP_KEY)
    return APP_KEY

def get_secret():
    global SECRET
    if_empty(SECRET)
    return SECRET

def get_url():
    global APP_URL
    if_empty(APP_URL)
    return APP_URL

def if_empty(key):
    if(key == ""):
        set_secrets()

def check_set(key, type):
    try:
        if(key == ""):
            if(type == 'a'):
                universal.error_code("APP_KEY not set from .env file. (check config folder for proper env file)")
            else:
                universal.error_code("SECRET not set from .env file. (check config folder for proper env file)")

        else:
            if(type == 'a'):
                universal.okay_code("APP_KEY set: " )
            elif(type == 'u'):
                universal.okay_code(f"SERVER_URL set:")
            else:
                universal.okay_code("SECRET set: ")
    except:
        universal.error_code("APP KEY and or SECRET not found in .env")

def get_debug_level():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    dotenv_path = os.path.join(current_directory, '..', 'config', '.env')

    # Load the .env file
    load_dotenv(dotenv_path)

    debug_level = os.getenv('DEBUG_LEVEL')

    return debug_level