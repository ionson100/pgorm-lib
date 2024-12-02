
class StringBuilder:
    _file_str =''

    def __init__(self,string:str=''):
        self._file_str = string

    def Append(self, string:str):
        self._file_str+=string

    def __str__(self):
        return self._file_str;
    def ToString(self):
        return self._file_str
