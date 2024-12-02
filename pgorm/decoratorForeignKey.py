import logging
from typing import Sequence, Mapping, Any

from pgorm.hostitem import get_host_base, HostItem
from pgorm.builderSelect import get_sql_select
from pgorm.logAction import PrintFree
from pgorm.orm import OrmConnectionNotPool
from pgorm.session import _builder_object_from_type


def getRelatives(cls: type,fk:str, add_where: str = None,
               params: Sequence | Mapping[str, Any] | None = None):
    def decorator(func):
        def wrapper(self):
            try:
                #PrintFree(f"ORM DECORATOR: arguments: {cls}, {fk}, {add_where}, {params}, {type(self)}")
                host: HostItem = get_host_base().get_hist_type(type(self))
                name_key = host.pk_property_name
                host_core = get_host_base().get_hist_type(cls)
                value_key = getattr(self, name_key)
                if hasattr(self, value_key):
                    return getattr(self, value_key)
                else:
                    p = []
                    sql = get_sql_select(cls, host_core) + f"WHERE {fk} = %s "
                    p.append(value_key)
                    if add_where is not None:
                        sql += add_where
                    sql += ';'

                    if params is not None:
                        for param in params:
                            p.append(param)
                    PrintFree(f'ORM DECORATOR: sql:{(sql, p)}')
                    with OrmConnectionNotPool().getSession() as session:
                        result_list: list[cls] = []

                        for record in session.execute(sql, tuple(p)):
                           o= _builder_object_from_type(record,cls,host_core)
                           result_list.append(o)

                        setattr(self, value_key, result_list)

                    return getattr(self, value_key)

            except Exception as exc:
                logging.error("%s: %s" % (exc.__class__.__name__, exc))
                raise
        return wrapper
    return decorator



