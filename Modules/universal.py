import datetime
import time

#red error codes
def error_code(text):
    print_combined("[ERROR]:", text, "31")

#green Okay
def okay_code(text):
    print_combined("[OKAY]:", text, "32")

#yellow warnings
def warning_code(text):
    print_combined("[WARNING]:", text, "33")

#prints frist part colored and second normal
def print_combined(colored_text, non_colored_text, color_code):
    reset_code = "\033[0m"
    colored_text = f"\033[{color_code}m{colored_text}\033[0m"
    print(colored_text + non_colored_text)

#prints in one color for the whole message
def print_colored(text, color_code):
    print(f"\033[{color_code}m{text}\033]")

def get_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')



#reading configuration file for setting variables

def split_string_at_char(inputString, splitChar, SectionNum):
    try:
        splitSections = str(inputString).split(splitChar)
        if len(splitSections) > SectionNum:
            return splitSections[SectionNum]
        else:
            return ""
    except ValueError as e:
        error_code(f"Value unable to be split and or returned:{str(inputString)}. Error : {str(e)}")


#write to file
def write_to_file(data, fileName="data.txt"):
    with open(fileName, 'w') as f:
        f.write(str(data))


class connection_retry():
    def __init__(self):
        self.sleep_time = 5
        self.attempts = 0
        self.Maxattempts = 3


    def retry(self):
        self.sleep_time += self.sleep_time
        self.attempts += 1
        if self.attempts > self.Maxattempts:
            self.reset()
            return self.breakLoop()

        time.sleep(self.sleep_time)
        return True


    def breakLoop(self):
        self.reset()
        return False
    def reset(self):
        self.sleep_time = 5
        self.attempts = 0
        
    def get_sleep_time(self):
        return self.sleep_time
    
