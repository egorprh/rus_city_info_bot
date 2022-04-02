import csv
import sqlite3

titles = {
    0: "address",
    1: "postal_code",
    2: "country",
    3: "federal_district",
    4: "region_type",
    5: "region",
    6: "area_type",
    7: "area",
    8: "city_type",
    9: "city",
    10: "settlement_type",
    11: "settlement",
    12: "kladr_id",
    13: "fias_id",
    14: "fias_level",
    15: "capital_marker",
    16: "okato",
    17: "oktmo",
    18: "tax_office",
    19: "timezone",
    20: "geo_lat",
    21: "geo_lon",
    22: "population",
    23: "foundation_year"
}


class Database:
    def __init__(self, path_to_db='main.db'):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, params: tuple = tuple(), fetchone=False, fetchall=False, commit=False):
        connection = self.connection
        # Задаем чтобы возвращались словари, а не туплы
        connection.row_factory = sqlite3.Row
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        cursor.execute(sql, params)
        data = None

        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
            # Преобразуем объект sqlite3.Row в словарь
            dictone = {}
            for key, item in enumerate(cursor.description):
                dictone[item[0]] = data[key]
            data = dictone
        if fetchall:
            # data = cursor.fetchall()
            # Преобразуем объекты sqlite3.Row в словари
            data = [dict(row) for row in cursor.fetchall()]

        connection.close()

        return data

    @staticmethod
    def format_args(sql, params: dict, separator: str = " AND "):
        sql += separator.join(
            f"{item} = ?" for item in params.keys()
        )
        return sql, tuple(params.values())

    def get_record(self, table, **kwargs):
        sql = f"SELECT * FROM {table} WHERE "
        sql, params = self.format_args(sql, kwargs)
        return self.execute(sql, params, fetchone=True)

    def get_records(self, table, data: dict = {}):
        sql = f"SELECT * FROM {table}"
        params = ()
        if len(data) > 0:
            sql += " WHERE "
            sql, params = self.format_args(sql, data)
        # TODO check
        print(sql)
        print(params)
        return self.execute(sql, params, fetchall=True)

    def insert_record(self, table_name: str, **kwargs):
        keys = ', '.join(
            f"{item}" for item in kwargs.keys()
        )
        params_mask = ', '.join(
            '?' for item in kwargs.keys()
        )
        params = tuple(kwargs.values())
        sql = f"INSERT OR IGNORE INTO {table_name} ({keys}) VALUES ({params_mask})"
        self.execute(sql, params, commit=True)

    def update_record(self, table_name: str, recordid: int, **kwargs):
        sql = f"UPDATE {table_name} SET "
        sql, params = self.format_args(sql, kwargs, ", ")
        sql += " WHERE id = ?"
        params += (recordid,)
        self.execute(sql, params, commit=True)

    def get_records_sql(self, sql: str, *args):
        # params = ()
        # if len(kwargs) >= 1:
        #     sql += ' WHERE TRUE '
        #     sql, params = self.format_args(sql, kwargs)
        # TODO check
        print(sql)
        print(args)
        return self.execute(sql, args, fetchall=True)

    def delete_records(self, table_name: str):
        self.execute(f"DELETE FROM {table_name} WHERE TRUE", commit=True)

    def create_table_cities(self):
        sql = """CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                address VARCHAR(255) NOT NULL,
                city VARCHAR(255),
                postal_code INTEGER,
                region VARCHAR(255),
                district VARCHAR(255),
                timezone VARCHAR(255),
                geo_lat REAL,
                geo_lon REAL,
                population INTEGER,
                foundation_year INTEGER
            );"""
        self.execute(sql, commit=True)

    def fill_cities_table(self):
        with open('tgbot/misc/city.csv', newline='') as csvfile:
            cityreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            i = 1
            for row in cityreader:

                # Пропускаем первую строку, там заголовки
                if i == 1:
                    i += 1
                    continue

                self.insert_record('cities',
                                   address=row[0].lower(),
                                   city=row[8] + ' ' + row[9],
                                   postal_code=row[1],
                                   region=row[4] + ' ' + row[5],
                                   district=row[3],
                                   timezone=row[19],
                                   geo_lat=row[20],
                                   geo_lon=row[21],
                                   population=row[22],
                                   foundation_year=row[23]
                                   )

    def create_table_users(self):
        sql = """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                telegram_id INTEGER UNIQUE NOT NULL,
                first_name varchar(255),
                last_name varchar(255),
                username varchar(255) UNIQUE,
                language_code varchar(255),
                email varchar(255)
                ); 
              """
        self.execute(sql, commit=True)

    def count_users(self, **kwargs):
        sql = "SELECT COUNT(id) FROM users WHERE "
        sql, params = self.format_args(sql, kwargs)
        return self.execute(sql, params, fetchone=True)

    def update_user(self, userid: int, **kwargs):
        sql = "UPDATE users SET "
        sql, params = self.format_args(sql, kwargs, ", ")
        sql += " WHERE id = ?"
        params += (userid,)
        self.execute(sql, params, commit=True)
        return sql, params


def logger(statement):
    print(f'''
    ------------------------------------------
    Executing:
    {statement}
    ------------------------------------------
    ''')
