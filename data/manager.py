import time
import sqlite3
import json

from utils.coordinate import CoordinateClaimedException, Coordinate


class DataManager():
    def __init__(self):
        self.conn = sqlite3.connect("data/data.db")
        self.cursor = self.conn.cursor()
        sql_guilds = """
        CREATE TABLE IF NOT EXISTS guilds(
            id INTEGER PRIMARY KEY NOT NULL,
            discord_id INTEGER NOT NULL,
            notify_channel INTEGER NOT NULL DEFAULT 0,
            overview_channel INTEGER NOT NULL DEFAULT 0,
            overview_message INTEGER NOT NULL DEFAULT 0
        );
        """
        sql_coords = """
        CREATE TABLE IF NOT EXISTS coordinates(
            id INTEGER PRIMARY KEY NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            user INTEGER NOT NULL,
            guild INTEGER NOT NULL,
            start INTEGER NOT NULL,
            end INTEGER NOT NULL,
            notified BOOLEAN NOT NULL DEFAULT false,
            expired BOOLEAN NOT NULL DEFAULT false,
            FOREIGN KEY (guild)
                REFERENCES guilds (id)
        );
        """
        self.cursor.execute(sql_guilds)
        self.cursor.execute(sql_coords)
        self.conn.commit()

    def get_data(file):
        with open(file, "r") as f:
            data = json.load(f)
        f.close()
        return data

    def write_data(file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    def get_claimed_coords(self, guild):
        sql = f"SELECT * FROM coordinates WHERE expired == 0 AND guild == (SELECT id FROM guilds WHERE discord_id == {guild}) ORDER BY x ASC, y ASC;"
        print(sql)
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def claim_coord(self, c: Coordinate, guild):
        self.check_coord_available(c, guild)

        sql = f"""INSERT INTO coordinates (x, y, user, start, end, guild) VALUES (
            {c.x},
            {c.y},
            {c.user},
            {c.start},
            {c.end},
            (SELECT id FROM guilds WHERE discord_id == {guild})
        );"""
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def check_coord_available(self, c: Coordinate, guild):
        data = self.get_active_coord(c, guild)

        if data is None or data == []:
            return
        raise CoordinateClaimedException(
            "Coordinate is already claimed", c.x, c.y, data[0][3], data[0][5])

    def is_coord_available(self, c: Coordinate, guild):
        data = self.get_active_coord(c, guild)

        if data is None or data == []:
            return True
        return False

    def check_coord_claimed(self, c: Coordinate, guild):
        data = self.get_active_coord(c, guild)

        if data is None or data == []:
            raise CoordinateClaimedException(
                "Cordinate is not claimed", c.x, c.y, c.user, 0)

        if data[0][3] != c.user:
            raise CoordinateClaimedException(
                "Not the owner of the coordinate", c.x, c.y, c.user, data[0][5])

    def get_active_coord(self, c: Coordinate, guild):
        sql = f"SELECT * FROM coordinates INNER JOIN guilds ON coordinates.guild == guilds.id WHERE x == {c.x} AND y == {c.y} AND expired == 0 and discord_id == {guild};"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def release_coord(self, c: Coordinate, guild):
        self.check_coord_claimed(c, guild)

        sql = f"UPDATE coordinates SET expired = 1 WHERE x == {c.x} AND y == {c.y} AND user == {c.user} AND guild == (SELECT id FROM guilds WHERE discord_id == {guild});"
        self.cursor.execute(sql)
        self.conn.commit()

    def get_expiring(self):
        sql = f"SELECT * FROM coordinates INNER JOIN guilds ON coordinates.guild == guilds.id WHERE end < {int(time.time()) + 60 * 60 * 23 + 60 * 58} and expired == 0;"
        # sql = f"SELECT * FROM coordinates WHERE end < {int(time.time()) + 60 * 60 * 23 + 60 * 58} and expired == 0;"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_notify(self):
        sql = f"SELECT * FROM coordinates INNER JOIN guilds ON coordinates.guild == guilds.id WHERE end < {int(time.time()) + 60 * 60 * 23 + 60 * 59} and expired == 0 AND notified == 0;"
        # sql = f"SELECT * FROM coordinates WHERE end < {int(time.time()) + 60 * 60 * 23 + 60 * 59} AND expired == 0 AND notified == 0;"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def set_expired(self, coord_id):
        sql = f"UPDATE coordinates SET expired = 1 WHERE id == {coord_id};"
        self.cursor.execute(sql)
        self.conn.commit()

    def set_notify(self, coord_id):
        sql = f"UPDATE coordinates SET notified = 1 WHERE id == {coord_id};"
        self.cursor.execute(sql)
        self.conn.commit()

    def extend_coord(self, c: Coordinate, guild):
        self.check_coord_claimed(c, guild)

        sql = f"UPDATE coordinates SET end = {c.end}, notified = 0 WHERE x == {c.x} AND y == {c.y} AND user == {c.user} AND guild == (SELECT id FROM guilds WHERE discord_id == {guild});"
        self.cursor.execute(sql)
        self.conn.commit()

    def check_guild(self, guild_id) -> bool:
        return any(guild_id in guild for guild in self.get_guilds())

    def get_guilds(self):
        sql = "SELECT discord_id FROM guilds"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def add_guild(self, guild_id, channel=0):
        sql = f"INSERT INTO guilds (discord_id, notify_channel) values ({
            guild_id}, {channel});"
        print(sql)
        # return
        self.cursor.execute(sql)
        self.conn.commit()

    def get_all_guilds(self):
        sql = "SELECT * FROM guilds;"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def set_notify_channel(self, guild_id, channel):
        sql = f"UPDATE guilds SET notify_channel = {channel} WHERE discord_id == {guild_id};"
        self.cursor.execute(sql)
        self.conn.commit()

    def set_overview_channel(self, guild_id, channel):
        sql = f"UPDATE guilds SET overview_channel = {channel} WHERE discord_id == {guild_id};"
        self.cursor.execute(sql)
        self.conn.commit()

    def set_overview_message(self, guild_id, message):
        sql = f"UPDATE guilds SET overview_message = {message} WHERE discord_id == {guild_id};"
        self.cursor.execute(sql)
        self.conn.commit()
