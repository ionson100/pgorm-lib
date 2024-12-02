import logging
from collections.abc import Iterator
from typing import Sequence, Mapping, Any
import psycopg2.extras
from pgorm.biulderInsert import get_sql_insert
from pgorm.buildUpdate import get_sql_update
from pgorm.builderSelect import get_sql_select
from pgorm.builderTable import _create_table
from pgorm.hostitem import get_host_base, HostItem
from pgorm.insertBulk import buildInsertBulk
from pgorm.jsonWorker import get_object_from_json
from pgorm.logAction import PrintFree
from pgorm.transaction import Transaction


def _get_attribute(cls: type):
    return get_host_base().get_hist_type(cls)


class Session:

    is_pool:bool
    def __init__(self, cursor: psycopg2.extensions.cursor,is_pool:bool):
        self._cursor = cursor
        self._is_pool = is_pool

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self._cursor is None:
            logging.error('orm:close session. The session is already closed', exc_info=True)
        else:
            self._cursor.close()
            self._cursor = None



    def getCursor(self):
        return self._cursor

    def existTable(self, cls: type) -> bool:
        """Checking for table existence"""
        try:
            ta = _get_attribute(cls).table_name
            sql = f"""SELECT EXISTS  ( SELECT FROM  pg_tables WHERE  schemaname = 'public' AND  tablename  = '{ta}' );"""
            PrintFree(f'ORM SESSION: existTable:{sql}')

            self._cursor.execute(sql)
            for record in self._cursor:
                [d] = record
                return d
        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def createTable(self, cls: type, add_exist: bool = False):
        """
        Creating a table from a class, the class type must have all attributes to be created
        :param cls: type must have all attributes to be created
        :param add_exist:dds to the creation strung: IF NOT EXISTS
        """
        try:
            sql = _create_table(_get_attribute(cls), add_exist)
            PrintFree(f'ORM SESSION: createTable :\n{sql}')
            self._cursor.execute(sql)

        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def truncateTable(self, cls: type) -> int:
        """
        TRUNCATE quickly removes all rows from a set of tables. It has the same effect as an unqualified DELETE on each table,
        but since it does not actually scan the tables it is faster. Furthermore,
        it reclaims disk space immediately, rather than requiring a subsequent VACUUM operation. This is most useful on large tables.
        :param cls: type must have all attributes to be created
        """
        try:

            sql = f'TRUNCATE TABLE  "{_get_attribute(cls).table_name}";'
            PrintFree(f'ORM SESSION: truncateTable:{sql}')
            self._cursor.execute(sql)
            return self._cursor.rowcount

        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def dropTable(self, cls: type, add_exist: bool = False) -> int:
        """
        DROP TABLE removes tables from the database. Only the table owner, the schema owner, and superuser can drop a table.
        To empty a table of rows without destroying the table, use DELETE or TRUNCATE.
        :param cls: type must have all attributes to be created
        :param add_exist:dds to the creation strung: IF EXISTS
        """
        try:
            append: str = ''
            if add_exist:
                append = 'IF EXISTS'
            sql = f'DROP TABLE {append} "{_get_attribute(cls).table_name}";'
            PrintFree(f'ORM SESSION: drop table:{sql}')

            self._cursor.execute(sql)
            return self._cursor.rowcount

        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def deleteFromTable(self, cls: type, where: str = '',
                        params: Sequence | Mapping[str, Any] | None = None) -> int:
        """
        deletes rows that satisfy the WHERE clause from the specified table.
        If the WHERE clause is absent, the effect is to delete all rows in the table. The result is a valid, but empty table.
        By default, DELETE will delete rows in the specified table and all its child tables.
        If you wish to delete only from the specific table mentioned, you must use the deleteFromOnlyTable clause
        :return rows count deleted.
        """
        try:
            if where is not None:
                where = where.strip().strip(';')
            sql = f'DELETE FROM "{_get_attribute(cls).table_name}" {where};'
            PrintFree(f'ORM SESSION: delete table:{sql} {params}')
            self._cursor.execute(sql, params)
            return self._cursor.rowcount

        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def deleteFromOnlyTable(self, cls: type, where: str = '',
                            params: Sequence | Mapping[str, Any] | None = None) -> int:
        """
        deletes rows that satisfy the WHERE clause from the specified table.
        If the WHERE clause is absent, the effect is to delete all rows in the table. The result is a valid, but empty table
        :return rows count deleted.
        """
        try:
            if where is not None:
                where = where.strip().strip(';')
            sql = f'DELETE FROM ONLY "{_get_attribute(cls).table_name}" {where};'
            PrintFree(f'ORM SESSION: delete only table:{sql} {params}')
            self._cursor.execute(sql, params)
            return self._cursor.rowcount

        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def insert(self, ob: any) -> int:
        """
        Inserting an object into a database, the object must have all the attributes that describe it in the database
        :param ob: object to insert
        :return: count of rows affected in the database
        """

        try:
            host: HostItem = _get_attribute(type(ob))
            sql: tuple[any, None] = get_sql_insert(ob, host)
            PrintFree(f'ORM SESSION: insert:{sql}')
            self._cursor.execute(sql[0], sql[1])

            if host.pk_generate_server:
                for record in self._cursor:
                    [d] = record
                    setattr(ob, host.pk_property_name, d)

            return self._cursor.rowcount
        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def update(self, ob: any) -> int:
        """
        Updating an object into a database, the object must have all the attributes that describe it in the database
        :param ob: object to update
        :return: count of rows affected in the database
        """
        try:
            host: HostItem = _get_attribute(type(ob))
            sql: tuple[any, None] = get_sql_update(ob, host)
            PrintFree(f'ORM SESSION: update:{sql}')
            self._cursor.execute(sql[0], sql[1])
            return self._cursor.rowcount

        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def select(self, cls: type, where: str = None,
               params:  Sequence | Mapping[str, Any] | None = None) -> Iterator[Any]:
        """
        Getting an iterator to a selection from a database
        :param cls: Table type
        :param where: the string in a query that comes after the FROM word
        :param params: array of parameters according to psycopg2 specification
        :return: count of rows affected in the database
        """
        try:
            host: HostItem = _get_attribute(cls)
            sql = get_sql_select(cls, host)
            if where is not None:
                sql += where.strip().strip(';')
            sql += ';'
            PrintFree(f'ORM SESSION: select:{(sql, params)}')
            self._cursor.execute(sql, params)

            for record in self._cursor:
                ob = _builder_object_from_type(record, cls, host)
                yield ob
        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def selectList(self, cls: type, where: str = None,
                   params: Sequence | Mapping[str, Any] | None = None) -> list[Any]:
        """
        Getting  list to a selection from a database
        :param cls: Table type
        :param where: the string in a query that comes after the FROM word
        :param params: array of parameters according to psycopg2 specification
        :return: count of rows affected in the database
        """
        try:
            host: HostItem = _get_attribute(cls)
            sql = get_sql_select(cls, host)
            if where is not None:
                sql += where.strip().strip(';')
            sql += ';'
            PrintFree(f'ORM SESSION: selectList:{(sql, params)}')
            self._cursor.execute(sql, params)

            list_result: list[cls] = []
            for record in self._cursor:
                ob = _builder_object_from_type(record, cls, host)
                list_result.append(ob)

            return list_result
        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def execute(self, sql: str | bytes,
                params: Sequence | Mapping[str, Any] | None = None):  # Sequence | Mapping[str, Any] | None = None
        """
        Getting an iterator for an arbitrary query string
        :param sql: request string
        :param params: array of parameters according to psycopg2 specification
        :return: count of rows affected in the database
        """


        try:
            PrintFree(f'ORM SESSION: execute:{(sql, params)}')
            self._cursor.execute(sql, params)
            for record in self._cursor:
                yield record
        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def executeQuery(self, sql: str | bytes,
                     params: Sequence | Mapping[str, Any] | None = None) -> list[
        tuple[Any, ...]]:  # Sequence | Mapping[str, Any] | None = None
        """

        :param sql: query string
        :param params: array of parameters according to psycopg2 specification
        :return: count of rows affected in the database
        """

        try:
            PrintFree(f'ORM SESSION: executeNotQuery:{(sql, params)}')

            # self._cursor.connection.cursor_factory=psycopg2.extras.DictCursor
            self._cursor.execute(sql, params)
            # for record in self._cursor:
            #
            #     yield record

            return self._cursor.fetchall()

        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise


    def executeNonQuery(self, sql: str | bytes,
                        params: Sequence | Mapping[
                            str, Any] | None = None) -> int:  # Sequence | Mapping[str, Any] | None = None
        """
        Execute a query without returning a result
        :param sql: query string
        :param params: array of parameters according to psycopg2 specification
        :return: count of rows affected in the database
        """
        try:
            PrintFree(f'ORM SESSION: executeNotQuery:{(sql, params)}')
            self._cursor.execute(sql, params)
            return self._cursor.rowcount
        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def beginTransaction(self, level: int | None = None) -> Transaction:
        """
        Getting a transaction to execute a request
        :param level: insulation level
        :return: Transaction
        """

        t = Transaction(self._cursor.connection, level)

        return t

    def insertBulk(self, ob: [any]) -> int:
        """
        Batch insert an array of objects into a database.
        All objects must be of the same type.
        The type must have description attributes for the database
        :param ob: Array of objects
        :return: count of rows affected in the database
        """
        try:
            if len(ob) == 0:
                return 0
            host: HostItem = _get_attribute(type(ob[0]))
            sql = buildInsertBulk(host, *ob)
            PrintFree(f'ORM SESSION: insertBulk:{sql}')
            self._cursor.execute(sql[0], sql[1])
            index = 0
            if host.pk_generate_server:
                for record in self._cursor:
                    setattr(ob[index], host.pk_property_name, record)
                    index = index + 1

            return self._cursor.rowcount
        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def cancel(self):
        """Canceling execution of long queries"""
        self._cursor.connection.cancel()

    def getByPrimaryKey(self, cls: type, id_value: any) -> object | None:
        """
        Getting an object of type by primary key value
        :param cls: A type that has descriptions of database attributes
        :param id_value:Primary Key Value
        :return:Object of type or None
        """
        try:
            host: HostItem = _get_attribute(cls)
            sql = get_sql_select(cls, host)
            sql += f'WHERE "{host.pk_column_name}" = %s'
            PrintFree(f'ORM SESSION:  getByPrimaryKey:{sql}, {[id_value]}')
            self._cursor.execute(sql, [id_value])
            ob = None
            for record in self._cursor:
                ob = _builder_object_from_type(record, cls, host)
                # index = 0
                # ob = cls()
                # for key, value in host.columns.items():
                #     if value.type.strip() == 'jsonb':
                #         v = get_object_from_json(record[index])
                #         setattr(ob, key, v)
                #     else:
                #         setattr(ob, key, record[index])
                #     index = index + 1
            return ob

        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def any(self, cls: type, where: str = None,
            params: Sequence | Mapping[str, Any] | None = None) -> bool:
        """
        Checks for rows in the database based on the query condition
        :param cls:  A type that has descriptions of database attributes
        :param where: query string
        :param params: array of parameters according to psycopg2 specification
        :return: True - rows is  found, False rows not found
        """
        try:
            host: HostItem = _get_attribute(cls)
            sql = f'SELECT EXISTS (SELECT 1 FROM "{host.table_name}" '
            if where is not None:
                sql += where.strip().strip(';')
            sql += ');'
            PrintFree(f'ORM SESSION:  any:{(sql, params)}')
            self._cursor.execute(sql, params)
            for record in self._cursor:
                [d] = record
                return d
            pass
        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def firstOrNull(self, cls: type, where: str = None,
                    params: Sequence | Mapping[str, Any] | None = None) -> object | None:
        """
        Gets the object from the first row of the query, if there is no row, returns none.
        :param cls: a type that has descriptions of database attributes
        :param where: query string
        :param params: array of parameters according to psycopg2 specification
        :return: params: Object of a given type
        """
        try:
            host: HostItem = _get_attribute(cls)
            sql = get_sql_select(cls, host)
            if where is not None:
                sql += where.strip().strip(';')
            sql += ' LIMIT 1;'
            PrintFree(f'ORM SESSION: firstOrNull:{(sql, params)}')
            self._cursor.execute(sql, params)
            ob = None
            for record in self._cursor:
                ob = _builder_object_from_type(record, cls, host)

            return ob
        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    def singleOrException(self, cls: type, where: str = None,
                          params: Sequence | Mapping[str, Any] | None = None) -> object:
        """
        Gets an object from a single row according to the request,
        if the row is not found or more than one row is found, an exception is raised
        :param cls: a type that has descriptions of database attributes
        :param where: query string
        :param params: array of parameters according to psycopg2 specification
        :return: Object of a given type or raise Error
        """
        try:
            host: HostItem = _get_attribute(cls)
            sql = get_sql_select(cls, host)
            if where is not None:
                sql += where.strip().strip(';')
            sql += ';'
            PrintFree(f'ORM SESSION: singleOrException:{(sql, params)}')
            self._cursor.execute(sql, params)
            ob = None
            for record in self._cursor:

                if ob is None:
                    ob = _builder_object_from_type(record, cls, host)
                else:
                    raise Exception("""
                            An error occurred while selecting a single value, the number of rows in the selection is greater than one.
                            """)
                # index = 0
                # for key, value in host.columns.items():
                #     if value.type.strip() == 'jsonb':
                #         v = get_object_from_json(record[index])
                #         setattr(ob, key, v)
                #     else:
                #         setattr(ob, key, record[index])
                #     index = index + 1

            if ob is None:
                raise Exception("""
                An error occurred while selecting a single value, the number of rows in the selection is zero.
                """)

            return ob

        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise


def _builder_object_from_type(record: tuple[Any, ...], cls: type, host: HostItem):
    index = 0
    ob = cls()
    for key, value in host.columns.items():
        if value.type.strip() == 'jsonb':

            v = get_object_from_json(record[index])
            setattr(ob, key, v)
        else:
            setattr(ob, key, record[index])
        index = index + 1
    return ob
