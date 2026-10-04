from django.db import connection


def fetch_all(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_one(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))


def execute(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        return cursor.rowcount


def execute_insert(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        return cursor.lastrowid
