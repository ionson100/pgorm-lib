import psycopg2
import logging


class Transaction:
    """Performing a transaction in isolation"""


    def __init__(self, con: psycopg2.extensions.connection,level:int|None):
        self.connection: psycopg2.extensions.connection | None = con
        self.connection.autocommit=False
        if level is not None:
            self.connection.set_isolation_level(level)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is not None:
            self.rollback()
        else:
            self.commit()

    def getStatusTransaction(self) -> int:
        """Returns the status of the current transaction"""
        if self.connection is None:
            logging.error('orm:getStatusTransaction. Transaction already used', exc_info=True)
        else:
            return self.connection.info.transaction_status

    def commit(self):
        """Recording a successful transaction"""
        if self.connection is None:
            return
        else:
            self.connection.commit()
            self.connection.autocommit = True
            self.connection.set_isolation_level(None)
            self.connection = None

    def rollback(self):
        """Transaction rollback"""
        if self.connection is None:
            return
        else:
            self.connection.rollback()
            self.connection.autocommit = True
            self.connection.set_isolation_level(None)
            self.connection = None
