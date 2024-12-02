import os

class ColorPrint:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'


class PrintSettings:
    PRINT: bool
    CLOR:str
    FILE:str

    def __init__(self, use_print=False):
        self.PRINT = use_print
        self.CLOR=ColorPrint.GREEN
        self.FILE=None




host_print_settings: PrintSettings = PrintSettings(False)


def set_print(use_print: bool, color:str=ColorPrint.GREEN,file:str=None):
    host_print_settings.CLOR=color
    host_print_settings.PRINT = use_print
    host_print_settings.FILE=file





os.system("")





def PrintFree(*msg):
    if host_print_settings.PRINT:
        s = ''
        for i in msg:
            s += str(i).strip() + ' '
        if host_print_settings.FILE is not None:
            with open(host_print_settings.FILE, 'a') as f:
                print(s, file=f)
        else:
            print(host_print_settings.CLOR + f'{s}' + '\x1b[0m')







