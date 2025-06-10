import time
import sqlite3
import json

from utils.coordinate import CoordinateClaimedException, Coordinate


class DataManager():
    def __init__(self):
        self.conn = sqlite3.connect("data/data.db")
        self.cursor = self.conn.cursor()
        sql = """CREATE TABLE IF NOT EXISTS coordinates(
            id INTEGER PRIMARY KEY NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            user INTEGER NOT NULL,
            start INTEGER NOT NULL,
            end INTEGER NOT NULL
        );"""
        self.cursor.execute(sql)
        self.conn.commit()

    def get_data(file):
        with open(file, "r") as f:
            data = json.load(f)
        f.close()
        return data

    def write_data(file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    def get_all_coords(self):
        sql = "SELECT * FROM coordinates ORDER BY x ASC, y ASC;"
        print(sql)
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def claim_coord(self, c: Coordinate):
        if not self.is_coord_available(c.x, c.y):
            sql = f"SELECT * FROM coordinates WHERE x == {c.x} AND y == {c.y};"
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            print(data)
            raise CoordinateClaimedException(
                "Coordinate is already claimed", c.x, c.y, data[0][3], data[0][5])

        sql = f"""INSERT INTO coordinates (x, y, user, start, end) VALUES (
            {c.x},
            {c.y},
            \"{c.user}\",
            {c.start},
            {c.end}
        );"""
        self.cursor.execute(sql)
        self.conn.commit()

    def is_coord_available(self, x, y):
        sql = f"SELECT * FROM coordinates WHERE x == {x} AND y == {y};"
        self.cursor.execute(sql)
        data = self.cursor.fetchall()

        if data is None or data == []:
            return True
        return False

    def get_coord(self, x, y):
        sql = f"SELECT * FROM coordinates WHERE x == {x} AND y == {y};"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def release_coord(self, x, y, user):
        sql = f"SELECT user FROM coordinates WHERE x == {x} AND y == {y};"
        self.cursor.execute(sql)
        data = self.cursor.fetchall()

        if data is None or data == []:
            raise CoordinateClaimedException(
                "Cordinate is not claimed", x, y, user, 0)

        if data[0][0] != user:
            raise CoordinateClaimedException(
                "Not the owner of the coordinate", x, y, user, data[0][5])

        sql = f"DELETE FROM coordinates WHERE x == {
            x} AND y == {y} AND user == \"{user}\";"
        self.cursor.execute(sql)
        self.conn.commit()

    def get_expired(self):
        sql = f"SELECT * FROM coordinates WHERE end < {int(time.time())};"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def extend_coord(self, x, y, user, end):
        sql = f"SELECT user FROM coordinates WHERE x == {x} AND y == {y};"
        self.cursor.execute(sql)
        data = self.cursor.fetchall()

        if data is None or data == []:
            raise CoordinateClaimedException(
                "Cordinate is not claimed", x, y, user, 0)

        if data[0][0] != user:
            raise CoordinateClaimedException(
                "Not the owner of the coordinate", x, y, user, data[0][5])

        sql = f"UPDATE coordinates SET end = {end} WHERE x == {
            x} AND y == {y} AND user == \"{user}\";"
        self.cursor.execute(sql)
        self.conn.commit()
