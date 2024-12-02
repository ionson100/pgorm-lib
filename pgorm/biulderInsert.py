from .hostitem import HostItem
from .jsonWorker import get_json

_dictInsert:dict[type,str]={}




def _inner_builder(h:HostItem,t:type):
    sql=f'INSERT INTO "{h.table_name}" ('
    for key,value in h.columns.items():
        if value.isPk == True and value.mode_generate_pk_server == True:
            continue
        sql+=f'"{value.name_table}", '
    sql=sql.strip(' ').strip(',')+ ') VALUES ('
    for key, value in h.columns.items():
        if value.isPk==True and value.mode_generate_pk_server==True:
            continue
        sql+='(%s), '
    if h.pk_generate_server:
        sql = sql.strip(' ').strip(',') + ') RETURNING '
        sql += f'"{h.pk_column_name}" ;'
    else:
        sql = sql.strip(' ').strip(',') + ') ;'
    _dictInsert[t]= sql



def _inner_build_param(o:any,h:HostItem):
    d:list[any]=[]
    for key, value in h.columns.items():
        if value.isPk==True and value.mode_generate_pk_server==True:
            continue
        if value.type== "jsonb":
            if hasattr(o,key):
                v = getattr(o, key)
                d.append(get_json(v))
            else:
                d.append(None)
        else:
            if hasattr(o,key):
                d.append(getattr(o,key))
            else:
                d.append(None)
            #
            # v = getattr(o, key)
            # d.append(v)


    return d


def get_sql_insert(o: any ,h:HostItem):
    t=type(o)
    c = _dictInsert.get(t)
    if c is None:
        _inner_builder(h,t)

    return _dictInsert.get(t), _inner_build_param(o, h)
