import chuckjokes.api.jokes as jokes

from chuckjokes.api import Request as ApiRequest
from chuckjokes.db.client import DbClient

class Joke:
    def __init__(self, api_id, value, categories = None):
        self.id = None
        self.api_id = api_id
        self.value = value
        self.categories = categories
        self.created_at = None
        self.updated_at = None

    def api_url(self):
        return ApiRequest.API_BASE_URL + "/jokes/" + self.api_id

    @classmethod
    def all(cls):
        cursor = DbClient().connection.cursor()
        results = []

        try:
            sql_query = "SELECT * FROM jokes ORDER BY created_at DESC;"
            cursor.execute(sql_query)
            db_results = cursor.fetchall()

            if len(db_results) > 0:
                for record in db_results:
                    results.append(cls.__init_from_sql_row(record))
        finally:
            cursor.close()

        return results

    @classmethod
    def find(cls, record_id):
        cursor = DbClient().connection.cursor()
        result = None

        try:
            sql_query = "SELECT * FROM jokes WHERE id=? LIMIT 1;"
            cursor.execute(sql_query, (record_id,))
            db_results = cursor.fetchall()

            if len(db_results) > 0:
                result = cls.__init_from_sql_row(db_results[0])
        finally:
            cursor.close()

        return result

    @classmethod
    def find_by_api_id(cls, api_id):
        cursor = DbClient().connection.cursor()
        result = None

        try:
            sql_query = "SELECT * FROM jokes WHERE api_id=? LIMIT 1;"
            cursor.execute(sql_query, (api_id,))
            db_results = cursor.fetchall()

            if len(db_results) > 0:
                result = cls.__init_from_sql_row(db_results[0])
        finally:
            cursor.close()

        return result

    @classmethod
    def random_from_api(cls, category = None):
        joke = jokes.random(category)
        return cls(api_id=joke["id"], value=joke["value"], categories=joke["category"])


    # TODO: Clean this method a little bit later
    def save(self):
        was_persisted = False

        if self.id:
            was_persisted = True
        elif self.api_id and not was_persisted:
            record = self.__class__.find_by_api_id(self.api_id)

            if record:
                self.id = record.id
                was_persisted = True
            else:
                record_id = self.__create_new_record()
                self.id = record_id
                was_persisted = False
        else:
            record_id = self.__create_new_record()
            self.id = record_id
            was_persisted = False

        if was_persisted:
            self.__update_record()

        return True

    def __create_new_record(self):
        cursor = DbClient().connection.cursor()
        record_id = None

        try:
            sql_query = """
            INSERT INTO jokes(api_id,value,created_at,updated_at)
                VALUES(?,?,DATETIME('NOW'),DATETIME('NOW'));
            """
            cursor.execute(sql_query, (self.api_id, self.value))
            record_id = cursor.lastrowid

            DbClient().connection.commit()
        finally:
            cursor.close()

        return record_id

    def __update_record(self):
        cursor = DbClient().connection.cursor()

        try:
            sql_query = """
            UPDATE jokes SET
                api_id = ?,
                value = ?,
                updated_at = DATETIME('NOW')
            WHERE id = ?;
            """
            cursor.execute(sql_query, (self.api_id, self.value, self.id))
            DbClient().connection.commit()
        finally:
            cursor.close()

    @classmethod
    def __init_from_sql_row(cls, record):
        instance = cls(api_id=record[1], value=record[2])
        instance.id = record[0]
        instance.created_at = record[3]
        instance.updated_at = record[4]

        return instance
