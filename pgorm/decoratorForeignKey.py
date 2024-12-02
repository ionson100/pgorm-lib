import logging
from typing import Sequence, Mapping, Any

from pgorm import Session
from pgorm.hostitem import get_host_base, HostItem
from pgorm.builderSelect import get_sql_select
from pgorm.logAction import PrintFree
from pgorm.session import _builder_object_from_type


def getRelatives(cls: type, fk:str, where_and: str = None,
                 params: Sequence | Mapping[str, Any] | None = None):

    def decorator(func):
        def wrapper(self,session:Session):
            try:
                if session is None:
                    raise Exception(f'You did not specify the required parameter session in the  {func.__name__} function')
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
                    if where_and is not None:
                        sql += where_and
                    sql += ';'

                    if params is not None:
                        for param in params:
                            p.append(param)
                    PrintFree(f'ORM DECORATOR: sql:{(sql, p)}')

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



