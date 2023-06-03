import sqlite3


class BotDB:
    def __init__(self, db):
        self.base = sqlite3.connect(db)
        self.cur = self.base.cursor()
        self.base.execute("CREATE TABLE IF NOT EXISTS users("
                          "id INTEGER NOT NULL PRIMARY KEY, "
                          "full_name TEXT,"
                          "study_group TEXT,"
                          "phone_number INTEGER,"
                          "date_of_birth DATETIME,"
                          "passport_data INTEGER,"
                          "passport_date DATETIME,"
                          "passport_issued TEXT,"
                          "department_code INTEGER,"
                          "place_of_registration TEXT,"
                          "courses TEXT)")

        self.base.execute("CREATE TABLE IF NOT EXISTS administrators("
                          "id INTEGER NOT NULL PRIMARY KEY,"
                          "full_name TEXT,"
                          "password TEXT)")

        self.base.execute("CREATE TABLE IF NOT EXISTS courses("
                          "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
                          "title TEXT,"
                          "schedule TEXT,"
                          "price INTEGER,"
                          "audience INTEGER,"
                          "teacher TEXT,"
                          "comment TEXT,"
                          "status BOOLEAN DEFAULT (False))")

        self.base.commit()

    def reg_user(self, user_id):
        self.cur.execute("INSERT INTO `user` (`user_id`) VALUES (?)", (user_id,))

    def get_user_id(self, user_id):
        result = self.cur.execute("SELECT `id` FROM `user` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def is_user_exist(self, user_id):
        result = self.cur.execute("SELECT * FROM `user` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def save(self):
        return self.base.commit()

    def close(self):
        self.base.close()
