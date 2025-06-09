import time
import sqlite3
import json


class CoordinateException(Exception):
    def __init__(self, message, x, y, user):
        super().__init__(message)
        self.x = x,
        self.y = y,
        self.user = user

    def __str__(self):
        return f"Coordinate ({self.x},{self.y}) claimed by user {self.user}"


class DataManager():
    def __init__(self):
        conn = sqlite3.connect("data/data.db")
        self.cursor = conn.cursor()
        sql = """CREATE TABLE IF NOT EXISTS coordinates(
            id INTEGER PRIMARY KEY NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            user STRING NOT NULL,
            start INTEGER NOT NULL,
            end INTEGER NOT NULL
        );"""
        self.cursor.execute(sql)

    def get_data(file):
        with open(file, "r") as f:
            data = json.load(f)
        f.close()
        return data

    def write_data(file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    def claim_coord(self, x, y, user, start, end):
        sql = f"""INSERT INTO coordinates (x, y, user, start, end) VALUES (
            {x},
            {y},
            \"{user}\",
            {start},
            {end}
        );"""
        self.cursor.execute(sql)
        pass

    def check_coord(self, x, y):
        sql = f"SELECT user, end FROM coordinates WHERE x == {x} AND y == {y};"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def release_coord(self, x, y, user) -> bool:
        sql = f"SELECT user FROM coordinates WHERE x == {x} AND y == {y};"
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        print(data)

        if data[0][0] != user:
            raise CoordinateException(
                "Not the owner of the coordinate", x, y, user)

        sql = f"DELETE FROM coordinates WHERE x == {
            x} AND y == {y} AND user == \"{user}\";"
        return True

    def get_expired(self):
        sql = f"SELECT * FROM coordinates WHERE end < {int(time.time())};"
        self.cursor.execute(sql)
        return self.cursor.fetchall()
