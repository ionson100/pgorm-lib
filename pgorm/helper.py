import logging


from pgorm import get_host_base, HostItem, get_sql_select, PrintFree
from pgorm.hostitem import _ColumnData
from pgorm.session import _get_attribute


def getAttribute(cls: type) -> HostItem:
    """Get all attributes that describe a type in the database"""
    return get_host_base().get_hist_type(cls)


def getTemplateTableAttributesDoc(*, name: str, default: str = 'null', type_column: str = 'TEXT',
                                  pk: bool = False, mode: bool = False):
    """
    Getting a property description string for a database
    :param mode: who generates the primary key value False: user generated, True: server generated
    :param name: column name in table
    :param default: default value
    :param type_column: column type
    :param pk: is it a primary key
    :return: a string that can be inserted into the description of a type property
    """
    dec: dict[str, any] = {'name':name, 'type':type_column, 'default':default, 'pk':pk, 'mode':mode}
    return 'orm' + str(dec) + 'orm'


def getSqlForType(cls: type):
    host: HostItem = _get_attribute(cls)
    sql = get_sql_select(cls, host)
    return sql


def tableName(cls: type) -> str:
    """Get the name of the table in the database associated with the type"""
    return f'"{_get_attribute(cls).table_name}"'


def columnName(cls: type, field_name: str) -> str:
    """
    Getting the name of a column in a table by the associated field in the type
    :param cls: class
    :param field_name: property name
    :return: str or error
    """
    for key, value in _get_attribute(cls).columns.items():
        if value.name_property == field_name:
            return f'"{value.name_table}"'
    logging.error(
        f'The name of the column associated with the field {field_name}, in the table : {cls} is missing',
        exc_info=True)
class MapBuilder:
    doc_string: str
    cls:type
    host: HostItem
    def __init__(self,cls:type,table_name:str):
        self.host=HostItem()
        self.host.table_name=table_name
        self.cls=cls
        self.host.columns={}
        self.dictHost:dict[str,HostItem]=get_host_base().dictHost
    def AppendField(self, *, name_field:str, name_column: str, default: str = 'null', type_column: str = 'TEXT',
                    is_pk: bool = False, use_server_generation: bool = False):

        column_data = _ColumnData()
        column_data.name_table = name_column
        column_data.type = type_column
        column_data.default = default
        column_data.isPk = is_pk
        column_data.name_property = name_field

        column_data.mode_property = use_server_generation
        column_data.mode_generate_pk_server = use_server_generation == True
        self.host.columns[name_field] = column_data

        if is_pk:
            self.host.pk_property_name=name_field
            self.host.pk_column_name=name_column
            self.host.pk_generate_server=use_server_generation

        self.dictHost[str(self.cls)] = self.host


    def ValidateMap(self)->HostItem:
        if self.host.pk_column_name is None:
            raise Exception('PK is missing')
        if self.host.table_name is None:
            raise Exception('Table name is missing')
        list_column_name:[]=[]
        for key,value in self.host.columns.items():
            if value.name_table is None:
                raise Exception('name_column is missing')
            else:
                if value.name_table in list_column_name:
                    raise Exception(f"Повторяющееся название в колонках таблицы: {self.cls} название: {value.name_table}")
                else:
                    list_column_name.append(value.name_table)
            if value.name_property is None:
                raise Exception(f"Для типа {self.cls} не указано name_field")
        PrintFree(printMap(self.host,self.cls))


        return self.dictHost
def printMap(host:HostItem,cls:type):
    c = f"""
  table_name:         {host.table_name}
  pk_column_name:     {host.pk_column_name}
  pk_generate_server: {host.pk_generate_server}
  pk_field_name:      {host.pk_property_name}
  columns:            {printColumns(host.columns)}
                    """
    return f'ORM MAP BUILD: {cls}  {c}'
def printColumns (col:dict[str, _ColumnData]):
    sb:str=''
    for key, value in col.items():
        sb+=f'\n      {key}: {printColumnData(value)}'
    return sb
def printColumnData(c:_ColumnData):
    return '{'+f'"field_name":"{c.name_property}", "column_mame":"{c.name_table}", "type_column":"{c.type}", default:"{c.default}",  "is_pk":{c.isPk}, "use_server_generation":{c.mode_generate_pk_server}'+'}'



