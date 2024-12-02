from .hostitem import HostItem

_dictSelect:dict[type,str]={}

def _inner_builder(h:HostItem,t:type):
    sql='SELECT '
    for key, value in h.columns.items():
        sql += f'"{value.name_table}", '
    sql = sql.strip(' ').strip(',')+ f' FROM "{h.table_name}" '
    _dictSelect[t]=sql

def get_sql_select(t:type,h:HostItem):
    c = _dictSelect.get(t)
    if c is None:
        _inner_builder(h,t)

    return _dictSelect.get(t)