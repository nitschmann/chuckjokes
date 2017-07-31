import os, sqlite3

from appdirs import user_data_dir

class DbClient(object):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(DbClient, cls).__new__(cls)
            cls.__instance.__initialized = False

        return cls.__instance

    def __init__(self):
        if (self.__initialized): return

        self.__setup_db_connection()
        self.__initialized = True

    def close_connection(self, commit = False):
        """Closes the connection to the DB"""
        if self.connection:
            if commit == True:
                self.connection.commit()

            self.connection.close()

    def reconnect(self):
        """Reconnects to the DB if wanted"""
        self.connection = sqlite3.connect(self.__db_file)

        if os.getenv("ENV") == "test":
            self.__setup_db_schema()

    # private

    def __create_db_file_dir_if_not_exists(self):
        if not os.path.exists(self.__db_file_dir):
            try:
                os.makedirs(self.__db_file_dir)
            except Exception as e:
                print(e)

    def __read_db_schema_file_contents(self):
        contents = None
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")

        with open(filepath, "r") as file_obj:
            contents = file_obj.read()

        return contents

    def __setup_db_connection(self):
        if os.getenv("ENV") == "test":
            self.__db_file = ":memory:"
        else:
            self.__db_file_dir = user_data_dir("chuckjokes")
            self.__create_db_file_dir_if_not_exists()
            self.__db_file = os.path.join(self.__db_file_dir, "jokes_db.sqlite")

        self.connection = sqlite3.connect(self.__db_file)

        self.__setup_db_schema()

    def __setup_db_schema(self):
        contents = self.__read_db_schema_file_contents()
        cursor = self.connection.cursor()

        try:
            cursor.executescript(contents)
        finally:
            cursor.close()
