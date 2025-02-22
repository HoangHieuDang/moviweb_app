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
        """
        get all users from the table users of the sqlite database
        :return: RETURN a LIST of all users
        """
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM users"))
            users_list = []
            for row in result:
                users_list.append(row.name)
            return users_list

    def get_user_movies(self, user_id):
        """
        get the movies the user of user_id has chosen
        :param user_id: INTEGER
        :return:
        + A dict of all movies from user_id with the following format:
        Example:
            {
            "Titanic":{"year":1995,
                    "rating":9.0,
                    "director":"James Cameron"},
            "Transformers":{"year":2010,
                    "rating":8.0,
                    "director":"Michale Bay"}
        }
        + empty dict {} if fail
        """
        query_get_movies_from_user_id = text("""SELECT * FROM movies WHERE movies.user_id = :user_id""")
        if isinstance(user_id, int):
            params = {"user_id": user_id}
            with self._engine.connect() as connection:
                result = connection.execute(query_get_movies_from_user_id, params)
                #print(f"Query result: {list(result)}")
                movies_dict = dict()
                for row in result:
                    movies_dict[row.name] = {"year":f"{row.year}","rating":f"{row.rating}", "director":f"{row.director}", "user_id":f"{row.user_id}"}
                return movies_dict
        else:
            print("invalid user_id!")
            return {}

    def get_all_movies(self):
        """
        get all movies from table movies of the sqlite database
        :return: return a DICT of movies with the following structure
        as example:
        {
            "Titanic":{"year":1995,
                    "rating":9.0,
                    "director":"James Cameron"},
            "Transformers":{"year":2010,
                    "rating":8.0,
                    "director":"Michale Bay"}
        }
        """
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM movies"))
            movies_dict = dict()
            for row in result:
                movies_dict[row.name] = {"year":f"{row.year}","rating":f"{row.rating}", "director":f"{row.director}", "user_id":f"{row.user_id}"}
            return movies_dict

    def add_user(self, user):
        """
        :param user: a string of user name
        :return:
        False when add operation fails
        True when add operation succeeds
        """
        # Check if the user is already in the sqlite database
        # Only add the new username if the name hasn't been taken yet
        if user in self.get_all_users():
            print("user name already taken!")
            return False
        else:
            query = text("INSERT INTO users (name) VALUES (:user)")
            params = {"user": user}
            #add user to the database using parameterised query
            with self._engine.connect() as connection:
                result = connection.execute(query, params)
                connection.commit()
                return True

    def add_movie(self, movie):
        """
        :param movie: should be a dict with a following structure as an example:
        {"movie_name":{"year":1994, "rating":9.8, "director":"Michael Bay"}}
        :return:
        False when the add operation fails
        True when the add operation succeeds
        """
        query_add_movie = text("""INSERT INTO movies (name, year, rating, director) VALUES(:name, :year, :rating, :director)""")
        query_check_movie_exist = text("""SELECT * FROM movies WHERE name = :name AND director = :director LIMIT 1""")
        if isinstance(movie, dict) and movie:
            try:
                movie_title_key = list(movie.keys())[0]
                params = {
                    "name":movie_title_key,
                    "year":movie[movie_title_key]['year'],
                    "rating":movie[movie_title_key]['rating'],
                    "director": movie[movie_title_key]['director']
                }
            except Exception as err:
                print("Something went wrong when extracting movie info:" + str(err))
                return False
            else:
                # check if the movie is already in the database
                with self._engine.connect() as connection:
                    search_result = connection.execute(query_check_movie_exist, params).fetchone()
                    if search_result is not None:
                        print("Movie is already in the database!")
                        return False
                    else:
                        with self._engine.connect() as connection:
                            connection.execute(query_add_movie, params)
                            connection.commit()
                            print("Movie added successfully!")
                            return True
        else:
            print("""input should be a dict with the following format: Example: {"movie_name":{"year":1994, "rating":9.8, "director":"Michael Bay"}}
            """)
            return False

    def update_movie(self, movie):
        """
        update_movie only allows updating rating, release_year
        update_movie will take director and movie's title as search criteria for updating

        :param movie: should be a dict with a following structure as an example:
        {"movie_name":{"year":1994, "rating":9.8, "director":"Michael Bay"}}
        :return:
        False when the update operation fails
        True when the update operation succeeds
        """
        query_update_movie = text(
            """UPDATE movies 
               SET year = :year, rating = :rating
               WHERE name = :name AND director = :director
               """)
        query_check_movie_exist = text(
            """SELECT * FROM movies WHERE name = :name AND director = :director LIMIT 1""")

        #check if the input movie was a dict and not empty
        if isinstance(movie, dict) and movie:
            try:
                movie_title_key = list(movie.keys())[0]
                params = {
                    "name": movie_title_key,
                    "year": movie[movie_title_key]['year'],
                    "rating": movie[movie_title_key]['rating'],
                    "director": movie[movie_title_key]['director']
                }
            except Exception as err:
                print("Something went wrong when extracting movie info:" + str(err))
                return False
            else:
                # check if the movie is already in the database
                with self._engine.connect() as connection:
                    search_result = connection.execute(query_check_movie_exist, params).fetchone()
                    # if the search_result is not empty, update the movie using the parameterised sql query
                    if search_result is not None:
                        #with self._engine.connect() as connection:
                        connection.execute(query_update_movie, params)
                        connection.commit()
                        print("Movie's info updated successfully!")
                        return True
                    else:
                        print("Movie doesn't exist in the database to update")
                        return False
        else:
            print("""input should be a dict with the following format: Example: {"movie_name":{"year":1994, "rating":9.8, "director":"Michael Bay"}}
                    """)
            return False

    def delete_user(self, user_id):
        """
        Delete an user from database by user_id
        :param user_id: INTEGER
        :return:
            True if delete operation succeeds
            False if delte operation fails
        """
        query_delete_user = text("""
            DELETE FROM users WHERE users.id = :user_id
        """)
        query_search_user = text("""
            SELECT name FROM users WHERE users.id = :user_id LIMIT 1
        """)
        if isinstance(user_id, int):
            params = {"user_id": user_id}
            with self._engine.connect() as connection:
                search_result = connection.execute(query_search_user, params).fetchone()
                if search_result is not None:
                    #with self._engine.connect() as connection:
                    connection.execute(query_delete_user, params)
                    connection.commit()
                    print("The user was deleted from the database")
                    return True
                else:
                    print("The user doesn't exist in the database")
                    return False


    def delete_movie(self, movie_id):
        """
        Delete a movie from database by movie_id
        :param movie_id: INTEGER
        :return:
            True if delete operation succeeds
            False if delte operation fails
        """
        query_delete_movie = text("""
            DELETE FROM movies WHERE movies.id = :movie_id
        """)
        query_search_movie = text("""
            SELECT name FROM movies WHERE movies.id = :movie_id LIMIT 1
        """)
        if isinstance(movie_id, int):
            params = {"movie_id": movie_id}
            with self._engine.connect() as connection:
                search_result = connection.execute(query_search_movie, params).fetchone()
                if search_result is not None:
                    #with self._engine.connect() as connection:
                    connection.execute(query_delete_movie, params)
                    connection.commit()
                    print("The movie was deleted from the database")
                    return True
                else:
                    print("The movie doesn't exist in the database")
                    return False


sqlite_data_obj = SQLiteDataManager("movie_sql_db.sqlite")
print(sqlite_data_obj.get_all_users())
print(sqlite_data_obj.get_all_movies())
print(sqlite_data_obj.get_all_users())
print(sqlite_data_obj.get_user_movies(2))