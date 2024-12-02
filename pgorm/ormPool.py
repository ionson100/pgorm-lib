import logging

import psycopg2
import psycopg2.pool
import psycopg2.extras

from .session import Session


class _HostPool:
    pool: psycopg2.pool.AbstractConnectionPool = None


_self_host_pool = _HostPool()


class OrmConnectionPool:
    @staticmethod
    def init(type_pool: int, minconn: int, maxconn: int, *args, **kwargs):
        """
             Initialize the connection pool.

            ew 'minconn' connections are created immediately calling 'connfunc'
            with given parameters. The connection pool will support a maximum of
            about 'maxconn' connections.
            database:
            port:
            host:
            user:
            password:
            :param type_pool 1-SimpleConnectionPool other value=ThreadedConnectionPool
            :param minconn: min connection init start
            :param maxconn: max connection
                
                """

        try:
            if type_pool == 0:
                _self_host_pool.pool = psycopg2.pool.SimpleConnectionPool(minconn, maxconn, *args, **kwargs)
            else:
                _self_host_pool.pool = psycopg2.pool.ThreadedConnectionPool(minconn, maxconn, args, kwargs)
            pass
        except Exception as exc:
            logging.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

    @staticmethod
    def getConnection():
        """
        getting connection
        :return: ConnectionPool
        """
        return ConnectionPool(_self_host_pool.pool)

    @staticmethod
    def ClosePool():
        """Close pool ena app"""
        _self_host_pool.pool.closeall()
        _self_host_pool.pool = None

    @staticmethod
    def getContext():
        """ return context for use context with"""
        return ContextPool()


class ContextPool:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        OrmConnectionPool.ClosePool()


class ConnectionPool:
    _connection: psycopg2.extensions.connection

    def __init__(self, pool: psycopg2.pool.AbstractConnectionPool):
        self._connection = pool.getconn()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close current connection"""
        _self_host_pool.pool.putconn(self._connection)

    def getConnection(self):
        """Getting a connection for independent work"""
        return self._connection

    def getSession(self, *, cursor_factory: psycopg2.extras = None):
        """getting session for independent work"""
        return Session(self._connection.cursor(cursor_factory=cursor_factory), True)
