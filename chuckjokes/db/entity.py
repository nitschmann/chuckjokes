from .client import DbClient
from .exceptions import ValuesAreNotUniqueException

class Entity:
    __columns__ = []
    __default_order__ = "id DESC"
    __extra_attributes__ = []
    __id_column__ = "id"
    __timestampes__ = False
    __table__ = ""
    __unique_columns__ = []

    def __init__(self, **kwargs):
        self.db_client = DbClient()

        self.__create_and_set_inital_attributes(kwargs)

    @classmethod
    def all(cls):
        """Returns a list of all entities."""
        cursor = DbClient().connection.cursor()
        results = []

        try:
            sql_query = """
            SELECT * FROM {table} ORDER BY {order};
            """.format(**{
                "table": cls.__table__,
                "order": cls.__default_order__
                })
            cursor.execute(sql_query)
            db_results = cursor.fetchall()

            if len(db_results) > 0:
                for record in db_results:
                    results.append(cls._init_from_sql_row(record))
        finally:
            cursor.close()

        return results

    def columns(self):
        return self.__columns__

    @classmethod
    def find(cls, record_id):
        """Finds an entity by its ID"""

        cursor = DbClient().connection.cursor()
        result = None

        try:
            sql_query = """
            SELECT * FROM {table} WHERE {id_column}=? LIMIT 1;
            """.format(**{
                "table": cls.__table__,
                "id_column": cls.__id_column__
                })
            cursor.execute(sql_query, (record_id,))
            db_results = cursor.fetchall()

            if len(db_results) > 0:
                result = cls._init_from_sql_row(db_results[0])
        finally:
            cursor.close()

        return result

    @classmethod
    def find_by(cls, column, value):
        """Finds an entity by a specific column and its value"""

        if column not in cls.__columns__:
            raise NameError("unknown column '{}'".format(column))

        cursor = DbClient().connection.cursor()
        result = None

        try:
            sql_query = """
            SELECT * FROM {table} WHERE {column}=? ORDER BY {order} LIMIT 1;
            """.format(**{
                "table": cls.__table__,
                "column": column,
                "order": cls.__default_order__
                })
            cursor.execute(sql_query, (value,))
            db_results = cursor.fetchall()

            if len(db_results) > 0:
                result = cls._init_from_sql_row(db_results[0])
        finally:
            cursor.close()

        return result

    # TODO: Reduce this call to an OR SQL statement to speed it up later
    def is_unique(self):
        """
        Checks if the current object is unique if it was not was persisted
        yet
        """

        values_unique = True

        if len(self.__unique_columns__) > 0:
            for column in self.__unique_columns__:
                value = getattr(self, column)

                if self.__class__.find_by(column, value) is None:
                    continue
                else:
                    values_unique = False
                    break

        return values_unique

    def save(self, check_uniqueness_conditions = True):
        """Saves the current object to the DB"""

        passed = False

        if getattr(self, self.__id_column__) is not None:
            passed = self._update_record()
        else:
            if check_uniqueness_conditions == True and not self.is_unique():
                error_msg = "One or more attributes of {} are already taken".format(self.__unique_columns__)
                raise ValuesAreNotUniqueException(error_msg)

            record_id = self._create_new_record()
            self.id = record_id
            passed = True

        return passed


    def settable_attributes(self):
        self.__class__.settable_attributes

    @classmethod
    def settable_attributes(cls):
        attributes = cls.__columns__ + cls.__extra_attributes__
        attributes.insert(0, cls.__id_column__)

        if cls.__timestampes__ == True:
            attributes.append("created_at")
            attributes.append("updated_at")

        return attributes

    def _create_new_record(self):
        cursor = self.db_client.connection.cursor()
        record_id = None

        try:
            columns_string = ",".join(str(e) for e in self.__columns__)
            values_string = ",".join(map((lambda e: "?"), self.__columns__))

            if self.__timestampes__:
                columns_string += ",created_at,updated_at"
                values_string += ",DATETIME('NOW'),DATETIME('NOW')"

            sql_query = """
            INSERT INTO {table}({columns})
                VALUES({values});
            """.format(**{
                "table": self.__table__,
                "columns": columns_string,
                "values": values_string
                })

            values = []
            for column in self.__columns__:
                values.append(getattr(self, column))
            values = tuple(values)

            cursor.execute(sql_query, values)
            record_id = cursor.lastrowid

            self.db_client.connection.commit()
        finally:
            cursor.close()

        return record_id

    def _update_record(self):
        cursor = self.db_client.connection.cursor()

        try:
            sets_string = ",".join(map((lambda e: "{} = ?".format(e)), self.__columns__))

            if self.__timestampes__ == True:
                columns = ["created_at", "updated_at"]
                sets_string += "," + ",".join(map((lambda e: "{} = DATETIME('NOW')".format(e)), columns))


            sql_query = """
            UPDATE {table} SET {sets} WHERE {id_column}=?;
            """.format(**{
                "table": self.__table__,
                "sets": sets_string,
                "id_column": self.__id_column__
                })

            values = []
            for column in self.__columns__:
                values.append(getattr(self, column))
            values.append(getattr(self, self.__id_column__))
            values = tuple(values)

            cursor.execute(sql_query, values)
            self.db_client.connection.commit()
        finally:
            cursor.close()

        return True



    @classmethod
    def _init_from_sql_row(cls, record):
        instance = cls()
        setattr(instance, cls.__id_column__, record[0])
        record_count = 1

        for column in cls.__columns__:
            setattr(instance, column, record[record_count])
            record_count += 1

        if cls.__timestampes__ == True:
            for column in ["created_at", "updated_at"]:
                setattr(instance, column, record[record_count])
                record_count += 1

        return instance

    def __create_and_set_inital_attributes(self, inital_attributes = {}):
        attributes = self.settable_attributes()

        if not set(inital_attributes.keys()).issubset(set(attributes)):
            raise AttributeError("invalid attributes passed")

        for attribute in attributes:
            setattr(self, attribute, inital_attributes.get(attribute))
