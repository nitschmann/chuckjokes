from chuckjokes.db import Entity

from . import joke

class Category(Entity):
    __table__ = "categories"
    __columns__ = ["name"]
    __unique_columns__ = ["name"]

    @classmethod
    def find_or_create_by_name(cls, name):
        """Find an category entity by its name or create it new"""

        record = cls.find_by("name", name)

        if not record:
            record = cls(name=name)
            record.save()

        return record

    def jokes(self):
        """Returns all jokes related to this category"""

        cursor = self.db_client.connection.cursor()
        jokes = []

        try:
            sql_query = """
            SELECT * FROM jokes j
                LEFT JOIN joke_categories jc ON jc.jokes_id = j.id
                WHERE jc.categories_id = ?
            """

            cursor.execute(sql_query, (self.id,))
            db_results = cursor.fetchall()

            for record in db_results:
                jokes.append(joke.Joke._init_from_sql_row(record))
        finally:
            cursor.close()

        return jokes
