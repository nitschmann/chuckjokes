import chuckjokes.api.jokes as jokes_api

from . import category
from chuckjokes.db import Entity

class Joke(Entity):
    __table__ = "jokes"
    __columns__ = ["api_id", "value"]
    __extra_attributes__ = ["categories"]
    __unique_columns__ = ["api_id"]
    __timestampes__ = True

    def save(self, check_uniqueness_conditions = True):
        super(Joke, self).save()
        self.__save_categories()

        return True

    @classmethod
    def random_from_api(cls, category = None):
        """Fetches a new joke from the API and return an instance"""

        joke = jokes_api.random(category)
        return cls(api_id=joke["id"], value=joke["value"], categories=joke["category"])

    @classmethod
    def random_from_api_unique(cls, category = None, max_tries = 10):
        """
        Same as cls.random_from_api with the difference that this method
        ensurces that the Joke was never read before. It is so long executed
        until the limit of max_tries is reached.
        """

        joke = None
        i = 0

        while i < max_tries:
            joke = cls.random_from_api(category=category)

            if cls.find_by("api_id", joke.api_id) is None:
                break
            else:
                i += 1

        return joke

    def __save_categories(self):
        if type(self.categories) == list:
            for category_name in self.categories:
                c = category.Category.find_or_create_by_name(category_name)
                self.__save_categories_relation(category_id = c.id)

    def __save_categories_relation(self, category_id):
        cursor = self.db_client.connection.cursor()

        try:
            sql_query = """
            INSERT INTO joke_categories(jokes_id,categories_id)
                SELECT ?, ?
                WHERE NOT EXISTS(SELECT 1 FROM joke_categories WHERE jokes_id =
                ? AND categories_id = ?);
            """

            cursor.execute(sql_query, (self.id,category_id,self.id,category_id))
            self.db_client.connection.commit()
        finally:
            cursor.close()
