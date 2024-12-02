from .hostitem import HostItem

_dictUpdate:dict[type,str]={}
def _inner_builder(h:HostItem,t:type):
    sql=f'UPDATE "{h.table_name}" SET '
    for key,value in h.columns.items():
        if value.isPk is True:
            continue

        sql+=f'"{value.name_table}" = (%s), '
    sql = sql.strip(' ').strip(',') + ' WHERE '

    for key, value in h.columns.items():
        if not value.isPk:
            continue
        sql+=f'"{value.name_table}" = (%s);'
    _dictUpdate[t]= sql



def _inner_build_param(o:any,h:HostItem):
    d:list[any]=[]
    for key, value in h.columns.items():
        if not value.isPk:
            v = getattr(o, key)
            d.append(v)
    for key, value in h.columns.items():
        if value.isPk is True:
            v = getattr(o, key)
            d.append(v)

    return d


def get_sql_update(o: any ,h:HostItem):


    t=type(o)
    c = _dictUpdate.get(t)
    if c is None:
        _inner_builder(h,t)

    return _dictUpdate.get(t), _inner_build_param(o, h)