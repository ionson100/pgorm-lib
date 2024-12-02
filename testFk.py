from uuid import uuid4
from pgorm import MapBuilder, OrmConnectionPool, set_print, ColorPrint, getRelatives, Session

set_print(True,ColorPrint.CYAN)


class UserFriends:
    id: str
    name: str
    id_user: str

    def __init__(self, name: str = 'friend'):
        self.name = name
        self.id = str(uuid4())
    def __str__(self):
        return f'{self.id} name:{self.name}'


b = MapBuilder(UserFriends, "user_friends")
b.AppendField(name_field="id", name_column="id", type_column="uuid",
              default="primary key", is_pk=True, use_server_generation=False)
b.AppendField(name_field="name", name_column="name", type_column='TEXT', default='NULL')
b.AppendField(name_field="id_user", name_column="id_user", type_column="uuid", default="null")
b.ValidateMap()

class User:
    id:str
    name:str

    @getRelatives(UserFriends,'id_user','and name = %s',['name-1'])
    def getFriends(self, current_session:Session)->list[UserFriends]:
        pass

    def __init__(self,name="ion"):
        self.name = name
        self.id=str(uuid4())
b=MapBuilder(User,"user")
b.AppendField(name_field="id",name_column="id",type_column="uuid",
              default="primary key",is_pk=True,use_server_generation=False)
b.AppendField(name_field="name",name_column="name",type_column='TEXT',default='NULL')
b.ValidateMap()






OrmConnectionPool.init(type_pool=0,minconn=1,maxconn=10,password='postgres',
                       host='localhost', port=5432, user='postgres1', database='test',)
with OrmConnectionPool.getContext() as ctx:
    with OrmConnectionPool.getConnection() as connection:
        with connection.getSession() as session:
            session.dropTable(User,True)
            session.createTable(User,True)

            session.dropTable(UserFriends,True)
            session.createTable(UserFriends,True)
            user=User()
            session.insert(user)
            l=[]
            for i in range(10):
                f=UserFriends(name=f'name-{i}')
                f.id_user=user.id
                l.append(f)
            session.insertBulk(l)
            for u in user.getFriends(session):
                print(u)
            print('from base')
            for u in user.getFriends(session):
                print(u)
            print('from cache')



