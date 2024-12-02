from .hostitem import HostItem
from .jsonWorker import get_json


def _portion(h:HostItem, ob:any, p:list[any]):
    s='('
    for key, value in h.columns.items():
        if value.isPk == True and value.mode_generate_pk_server == True:
            continue
        s=s+"%s, "
        if value.type== "jsonb":
            if hasattr(ob,key):
                v = getattr(ob, key)
                p.append(get_json(v))
            else:
                p.append(None)


        else:
            if hasattr(ob, key):
                p.append(getattr(ob,key))
            else:
                p.append(None)


    s=s.strip(' ').strip(',')+'), '
    return s

def buildInsertBulk(h:HostItem,*ob)->(str,list[any]):
    params:list[any]=[]
    sql=f'INSERT INTO "{h.table_name}" ('
    for key,value in h.columns.items():
        if value.isPk == True and value.mode_generate_pk_server == True:
            continue
        sql=sql+f'"{value.name_table}", '
    sql=sql.rstrip(' ').strip(',')+') VALUES '
    for o in ob:
        sql= sql +_portion(h, o, params)
    sql=sql.strip(' ').strip(',')
    if h.pk_generate_server:
        sql+= ' RETURNING '
        sql += f'"{h.pk_column_name}" ;'
    else:
        sql+=';'

    return sql,params



