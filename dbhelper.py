import sqlite3


class DBHelper:
    def __init__(self, dbname="users.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS states (chatid Int PRIMARY KEY, state INT)"
        self.conn.execute(stmt)
        self.conn.commit()
        stmt = "CREATE TABLE IF NOT EXISTS user_info (chatid Int PRIMARY KEY, Target text, City text, Ability text, " \
               "Level text)"
        self.conn.execute(stmt)
        self.conn.commit()
        stmt = "CREATE TABLE IF NOT EXISTS vacancies (Name_area text, Ability text, Level text, " \
               "Amount INT, answer_mean INT, answer_min INT, answer_max INT, answer_median INT, answer_std REAL)"
        self.conn.execute(stmt)
        self.conn.commit()
        stmt = "CREATE TABLE IF NOT EXISTS resumes (Name_area text, Ability text, Level text, " \
               "Amount INT, answer_mean INT, answer_min INT, answer_max INT, answer_median INT, answer_std REAL)"
        self.conn.execute(stmt)
        self.conn.commit()
        # stmt = "CREATE TABLE IF NOT EXISTS contacts (chatid Int PRIMARY KEY, contact text"
        # self.conn.execute(stmt)
        # self.conn.commit()

    # def update_contact(self, chatid, user_contact):
    #     stmt = "UPDATE contacts SET contact = (?) WHERE chatid = (?)"
    #     args = (user_contact, chatid)
    #     self.conn.execute(stmt, args)
    #     self.conn.commit()


    def add_user(self, chatid):
        stmt = "INSERT INTO states (chatid, state) VALUES (?,?)"
        args = (chatid, 1)
        self.conn.execute(stmt, args)
        self.conn.commit()
        stmt = "INSERT INTO user_info (chatid) VALUES (?)"
        args = (chatid, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def add_user_info(self, chatid, column, value):
        stmt = "UPDATE user_info SET {} = '{}' WHERE chatid = (?)".format(column, value)
        args = (chatid, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_user_info(self, chatid):
        stmt = "SELECT * FROM user_info WHERE chatid = (?)"
        args = (chatid, )
        info = [x for x in self.conn.execute(stmt, args)]
        keys = ('chatid', 'Target', 'City', 'Ability', 'Level')
        return dict(zip(keys, info[0]))

    def delete_user_info(self, chatid, column):
        stmt = "UPDATE user_info SET {} = NULL WHERE chatid = (?)".format(column)
        args = (chatid, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_all_user_info(self, chatid):
        stmt = "UPDATE user_info SET Target = NULL WHERE chatid = (?)"
        args = (chatid, )
        self.conn.execute(stmt, args)
        self.conn.commit()
        stmt = "UPDATE user_info SET City = NULL WHERE chatid = (?)"
        args = (chatid,)
        self.conn.execute(stmt, args)
        self.conn.commit()
        stmt = "UPDATE user_info SET Ability = NULL WHERE chatid = (?)"
        args = (chatid,)
        self.conn.execute(stmt, args)
        self.conn.commit()
        stmt = "UPDATE user_info SET Level = NULL WHERE chatid = (?)"
        args = (chatid,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_state(self, chatid):
        stmt = "SELECT state FROM states WHERE chatid = (?)"
        args = (chatid, )
        state = [x[0] for x in self.conn.execute(stmt, args)]
        return state[0] if state else None

    def update_state(self, chatid, state):
        stmt = "UPDATE states SET state = (?) WHERE chatid = (?)"
        args = (state, chatid)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def add_vacancy(self, Name_area, Ability, Level, Amount, answer_mean,
                    answer_min, answer_max, answer_median, answer_std):
        stmt = "INSERT INTO vacancies (Name_area, Ability, Level, Amount, answer_mean, " \
               "answer_min, answer_max, answer_median, answer_std) VALUES (?,?,?,?,?,?,?,?,?)"
        args = (Name_area, Ability, Level, Amount, answer_mean, answer_min, answer_max, answer_median, answer_std)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def add_resume(self, Name_area, Ability, Level, Amount, answer_mean,
                    answer_min, answer_max, answer_median, answer_std):
        stmt = "INSERT INTO resumes (Name_area, Ability, Level, Amount, answer_mean, " \
               "answer_min, answer_max, answer_median, answer_std) VALUES (?,?,?,?,?,?,?,?,?)"
        args = (Name_area, Ability, Level, Amount, answer_mean, answer_min, answer_max, answer_median, answer_std)
        self.conn.execute(stmt, args)
        self.conn.commit()


    def get_vacancy(self, Name_area, Ability, Level):
        stmt = "SELECT * FROM vacancies WHERE Name_area = '{}' and Ability = '{}' and Level = '{}'".format(str(Name_area), str(Ability), str(Level))
        # args = (Name_area, Ability, Level)
        vacancy_info = [x for x in self.conn.execute(stmt)]
        if len(vacancy_info) == 0:
            return dict()
        keys = ('Name_area', 'Ability', 'Level', 'Amount', 'answer_mean',
               'answer_min', 'answer_max', 'answer_median', 'answer_std')
        return dict(zip(keys, vacancy_info[0]))

    def get_resume(self, Name_area, Ability, Level):
        stmt = "SELECT * FROM resumes WHERE Name_area = '{}' and Ability = '{}' and Level = '{}'".format(str(Name_area), str(Ability), str(Level))

        # args = (Name_area, Ability, Level,)
        resume_info = [x for x in self.conn.execute(stmt)]
        if len(resume_info) == 0:
            return dict()
        keys = ('Name_area', 'Ability', 'Level', 'Amount', 'answer_mean',
               'answer_min', 'answer_max', 'answer_median', 'answer_std')
        return dict(zip(keys, resume_info[0]))


    def close(self):
        self.conn.close()