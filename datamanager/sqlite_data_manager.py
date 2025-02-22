from interface_data_mngt import DataManagerInterface
from sqlalchemy import URL, create_engine, text

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file_name):
        try:
            self._url_obj = URL.create(
                drivername="sqlite",
                database=db_file_name
            )
            self._engine = create_engine(self._url_obj)
        except Exception as err:
            print("Cannot initiate SQLiteDataManager" + str(err))

    def get_all_users(self):
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM users"))
            for row in result:
                print("iam here")
                print("username:", row.name)

    def get_user_movies(self, user_id):
        pass

    def add_user(self, user):
        pass

    def add_movie(self, movie):
        pass

    def update_movie(self, movie):
        pass

    def delete_user(self, user_id):
        pass

    def delete_movie(self, movie_id):
        pass

sqlite_data_obj = SQLiteDataManager("movie_sql_db.sqlite")
sqlite_data_obj.get_all_users()