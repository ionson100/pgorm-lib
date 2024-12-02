


class _ColumnData:
    name_table:str|None=None
    name_property:str|None=None
    type:str|None=None
    isPk:bool=False
    mode_generate_pk_server:bool=False
    default:object|None=None
class HostItem:
    table_name:str|None=None
    table_other:str|None=None
    pk_column_name:str|None=None
    pk_property_name:str|None=None
    pk_generate_server: bool = False # key generation occurs on the server
    columns:dict[str,_ColumnData]={}
class HostAttribute:
    dictHost:dict[str,HostItem]={}




    def get_hist_type(self,cls:type) ->HostItem:
        c=self.dictHost;
        res=self.dictHost.get(str(cls))
        if res is None:
            raise Exception( f"Attention! type {cls} is not described for working with database, please describe the type via MapBuilder")
        return self.dictHost.get(str(cls))
hostBase=HostAttribute()
def get_host_base():
    return hostBase









