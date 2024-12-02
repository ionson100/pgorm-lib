from dataclasses import dataclass
from uuid import uuid4

from pgorm import OrmConnectionPool, ColorPrint
from pgorm import set_print, MapBuilder

set_print(True,ColorPrint.BLUE)  # говорит что нужно печатать все запросы в консоль








class UserBase:
    name: str = ''
    age: int = 10

class UserClient(UserBase):
    id: str
    def __init__(self):
        self.id=str(uuid4())
    def __str__(self):
        return f'{self.id} {self.name} {self.age}'


class UserDatabase(UserBase):
    id: int
    def __init__(self, name: str = 'user'):
        self.name = name

    def __str__(self):
        return f'{self.id} {self.name} {self.age}'

b=MapBuilder(UserDatabase,'myUser2')
b.AppendField(name_field="id",name_column="id",type_column='SERIAL',default='PRIMARY KEY',is_pk=True,use_server_generation=True)
b.AppendField(name_field="name",name_column="name",type_column='TEXT',default='NULL')
b.AppendField(name_field="age",name_column="age",type_column='integer',default='DEFAULT 0')
s=b.ValidateMap()

b=MapBuilder(UserClient,'myUser1')
b.AppendField(name_field="id",name_column="id",type_column='uuid',default='PRIMARY KEY',is_pk=True,use_server_generation=False)
b.AppendField(name_field="name",name_column="name",type_column='TEXT',default='NULL')
b.AppendField(name_field="age",name_column="age",type_column='integer',default='DEFAULT 0')
b.ValidateMap()


OrmConnectionPool.init(type_pool=0,minconn=1,maxconn=10,password='postgres',
                       host='192.168.70.119', port=5432, user='postgres', database='test',)
with OrmConnectionPool.getContext() as ctx:
    with OrmConnectionPool.getConnection() as connection:
        with connection.getSession() as session:
            with session.beginTransaction() as tx:
                session.dropTable(UserDatabase, True)
                session.createTable(UserDatabase, True)

                session.dropTable(UserClient, True)
                session.createTable(UserClient, True)

                session.truncateTable(UserDatabase)
                session.insert(UserDatabase("user1"))
                l=[]
                for i in range(10):
                    l.append(UserDatabase(f'name-{i}'))
                session.insertBulk(l)

                for r in session.select(UserDatabase,"where name <> %s",['user1']):
                    print(r)

                l=[]
                for i in range(10):
                    l.append(UserClient())
                session.insertBulk(l)
                df=session.selectList(UserClient)
                for u in df:
                    print(u)
                print(session.getByPrimaryKey(UserClient,l[0].id))




# в ручном режиме
# OrmConnectionPool.init(type_pool=0,minconn=1,maxconn=10,password='postgres', host='192.168.70.119', port=5432, user='postgres', database='test',)
# connect=OrmConnectionPool.getConnection()
# session=connect.getSession()
# try:
#     session.dropTable(UserDatabase, True)
# except Exception as e:
#     print(e)
#     raise
# finally:
#     session.close()
#     connect.close()
#     OrmConnectionPool.ClosePool()
# print(getTemplateTableAttributesDoc(name="my_name",type_column="TEXT",default=" null",pk=False,mode=False))
"""
orm{'name': 'my_name', 'type': 'TEXT', 'default': ' null', 'pk': False, 'mode': False}orm
"""


