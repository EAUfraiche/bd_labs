from datetime import date, datetime
from decimal import Decimal

import pymysql

from ... import db


class ProcedureError(Exception):
    """Помилка збереженої процедури (SIGNAL або помилка СУБД)."""

    def __init__(self, message, errno=None):
        super().__init__(message)
        self.errno = errno


def _jsonable(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


class ProcedureDAO:
    """Виклик збережених процедур MySQL (CALL ...)."""

    def call(self, name, args=()):
        conn = db.session.connection().connection  # DBAPI-з'єднання PyMySQL
        cur = conn.cursor()
        result = None
        try:
            cur.callproc(name, tuple(args))
            while True:
                if cur.description and result is None:  # перший набір результатів
                    cols = [d[0] for d in cur.description]
                    result = [{c: _jsonable(v) for c, v in zip(cols, row)} for row in cur.fetchall()]
                if not cur.nextset():
                    break
            db.session.commit()
        except pymysql.MySQLError as e:
            db.session.rollback()
            errno = e.args[0] if e.args and isinstance(e.args[0], int) else None
            message = e.args[1] if len(e.args) > 1 else str(e)
            raise ProcedureError(str(message), errno)
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return result or []
