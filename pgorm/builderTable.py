from pgorm.hostitem import HostItem
from pgorm.utils import StringBuilder


def _create_table(host: HostItem, exist:bool) -> str:
    builder=StringBuilder()
    append= 'IF NOT EXISTS'
    if not exist:
        append=''
    builder.Append(f'CREATE TABLE {append}  "{host.table_name}" (\n ')
    for key,value in host.columns.items():
        if value.isPk:
            builder.Append(f'   "{value.name_table}" {value.type}  {value.default},\n')
    for key,value in host.columns.items():
        if not value.isPk:
            builder.Append(f'   "{value.name_table}" {value.type} {value.default},\n')

    sql=builder.ToString().strip('\n').strip(',')
    sql+='\n);'
    return sql
