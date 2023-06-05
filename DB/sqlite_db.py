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
                          "password TEXT,"
                          "is_active BOOLEAN DEFAULT (False))")

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
        self.cur.execute("INSERT INTO `users` (`id`) VALUES (?)", (user_id,))

    def get_user_id(self, user_id):
        result = self.cur.execute("SELECT `id` FROM `users` WHERE `id` = ?", (user_id,))
        return result.fetchone()[0]

    def is_user_exist(self, user_id):
        result = self.cur.execute("SELECT * FROM `users` WHERE `id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_courses(self, status):
        result = self.cur.execute("SELECT * FROM `courses` WHERE `status` = ?", (status,))
        return result

    def get_course(self, item_id):
        result = self.cur.execute("SELECT * FROM `courses` WHERE `id` = ?", (item_id,))
        return result.fetchone()

    def is_admin_exist(self, user_id):
        result = self.cur.execute("SELECT * FROM `administrators` WHERE `id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def is_admin_active(self, user_id):
        result = self.cur.execute("SELECT * FROM `administrators` WHERE `id` = ?", (user_id,))
        return result.fetchone()[3]

    def make_admin_active(self, user_id):
        self.cur.execute("UPDATE administrators SET is_active = TRUE WHERE id = ?", (user_id,))
        self.save()
        return True

    def check_admin_password(self, user_id, password):
        result = self.cur.execute("SELECT * FROM `administrators` WHERE `id` = ?", (user_id,))
        if result.fetchone()[2] == password:
            return True
        return False

    def save(self):
        return self.base.commit()

    def close(self):
        self.base.close()
