
import mysql.connector
from mysql.connector import errorcode


class MysqlWriter:

    def __init__(self, attribute_objects):
        config = {'user': 'INSERT_USER',
                  'password': 'INSERT_PASSWORD',
                  'host': "127.0.0.1",
                  'database': 'bmtoolb_callout_scrape'}
        connection = cursor = None

        try:
            connection = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with the credentials.")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist.")
            else:
                print(err)
        else:
            cursor = connection.cursor()
            cursor.execute('use bmtoolb_callout_scrape')

            new_table_name = self.make_new_table(cursor)

            self.insert_attributes(cursor, attribute_objects, new_table_name)

            print("Great Success!!!")
            connection.commit()

        finally:
            if connection:
                connection.close()
            if cursor:
                cursor.close()

    @classmethod
    def make_new_table(cls, cursor):
        try:
            cursor.execute('SELECT MAX(id) AS id FROM call_log')
            increment_id = cursor.fetchone()[0] + 1
            new_table_name = "active_calls_{0}".format(increment_id)
            print("Making Table: {0}...".format(new_table_name))
            cursor.execute('CREATE TABLE {0} LIKE calls_template'.format(new_table_name))

            cursor.execute('INSERT INTO call_log (date_time) VALUES (NOW())')
            print("Success!")
            return new_table_name
        except mysql.connector.Error as error:
            print(error)
            return "failed to make table"

    @classmethod
    def insert_attributes(cls, cursor, attr_objects, table_name):
        try:
            for obj in attr_objects:
                print("Inserting Attributes for callId: {0}...".format(obj.id))
                attributes = obj.attribute_dictionary

                data = list(attributes.values())
                keys = list(attributes.keys())
                fillers = ",".join("%s" for i in range(len(data)))
                call = "INSERT INTO {0} ({1}) VALUES ({2})" \
                    .format(table_name, ", ".join(keys), fillers)

                cursor.execute(call, data)

                print("Success!")
        except mysql.connector.Error as error:
            print(error)

    # cursor.execute('INSERT INTO call_log(date_time) VALUES(NOW());')

    # 'CREATE TABLE call_log (id INT NOT NULL AUTO_INCREMENT,' \
    # 'date_time DATETIME NOT NULL,' \
    # 'PRIMARY KEY(id));'

    # 'SELECT MAX(id) AS id FROM call_log'

    # SELECT *, MAX(id) FROM `call_log`

    # 'SELECT * from call_log ORDER BY id ASC LIMIT 1' # better one.

    # SET SQL_SAFE_UPDATES = 0;
    # DELETE FROM instructor
    # SQL_SAFE_UPDATES = 1;

    # SET @tbls = (SELECT GROUP_CONCAT(TABLE_NAME)
    # FROM information_schema.TABLES
    # WHERE TABLE_NAME LIKE 'active_calls_%'
    # AND SUBSTRING_INDEX( table_name, '_', -1 ) < 6);
    # PREPARE stmt FROM 'DROP TABLE @tbls';
    # EXECUTE stmt USING @tbls;
    # DEALLOCATE PREPARE stmt;
