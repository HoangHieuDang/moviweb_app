from datamanager.interface_data_mngt import DataManagerInterface
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
        :return:
        RETURN a LIST of all users in this format:
        [{"name":"John", "id":1}{...}]
        """
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM users"))
            users_list = []
            for row in result:
                users_list.append({"name": row.name, "id": row.id})
            return users_list

    def get_user_by_id(self, user_id):
        """
        get the name of a user by user_id from the table users of the sqlite database
        :return:
        RETURN the dict format {"name":"John", "id":1} of the user if found
        RETURN empty string "" if fail
        """
        try:
            with self._engine.connect() as connection:
                params = {"user_id": user_id}
                result = connection.execute(text("SELECT users.name FROM users WHERE users.id = :user_id"), params)
                return {"name": [row.name for row in result][0], "id": user_id}
        except Exception as err:
            print("Can not find user:" + str(err))
            return ""

    def get_movie_by_id(self, movie_id):
        """
        Check if a
        movie
        already
        exists in the
        database
        :param movie_id: INTEGER
        :return
        movie: {
               < movie_name>:{
                            < year_key >: < year_value >,
                            < rating_key >: < rating_value >,
                            < director_key >: < director_value >,
                            }
                }
        """
        query_get_movie_info = text("SELECT * FROM movies WHERE movies.id = :movie_id")
        try:
            with self._engine.connect() as connection:
                params = {"movie_id": movie_id}
                result = connection.execute(query_get_movie_info, params)
                movie_dict = {}
                for row in result:
                    movie_dict[row.name] = {"year":row.year, "rating":row.rating, "director":row.director, "id":row.id}
                return movie_dict
        except Exception as err:
            print("Can not find movie:" + str(err))
            return ""

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
        + empty dict {} if fail or no match
        """
        query_get_movies_from_user_id = text(
            """SELECT movies.name, movies.year, movies.rating, movies.director, movies.id FROM user_favorites JOIN movies ON movies.id = user_favorites.movie_id WHERE user_favorites.user_id = :user_id;""")
        if isinstance(user_id, int):
            params = {"user_id": user_id}
            with self._engine.connect() as connection:
                # The result will be a list of all movie_ids of the given user_id
                result = connection.execute(query_get_movies_from_user_id, params)
                movies_dict = dict()
                for row in result:
                    movies_dict[row.name] = {"year": row.year, "rating": row.rating,
                                             "director": f"{row.director}", "id": row.id}
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
                    "director":"James Cameron",
                    "id": 2
                    },

            "Transformers":{"year":2010,
                    "rating":8.0,
                    "director":"Michale Bay",
                    "id": 3
                    }
        }
        """
        with self._engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM movies"))
            movies_dict = dict()
            for row in result:
                movies_dict[row.name] = {"year": f"{row.year}", "rating": f"{row.rating}",
                                         "director": f"{row.director}", "id": f"{row.id}"}
            return movies_dict

    def is_movie_exist(self, movie):
        """
        Check if a movie already exists in the database
        :param movie: {
                            <movie_name>:{
                                <year_key>:<year_value>,
                                <rating_key>:<rating_value>,
                                <director_key>:<director_value>,
                          }
                      }
        :return:
            True if yes and found_movie_info with the same format as mentioned in the param section for
                    parameter "movie"
            False if no
            None if invalid use of the function (wrong argument or connection error)
        """
        query_check_movie_exist = text("""SELECT * FROM movies WHERE name = :name AND director = :director LIMIT 1""")
        if isinstance(movie, dict) and movie:
            try:
                movie_title_key = list(movie.keys())[0]
                params = {
                    "name": movie_title_key,
                    "rating": movie[movie_title_key]['rating'],
                    "year": movie[movie_title_key]['year'],
                    "director": movie[movie_title_key]['director']
                }
            except Exception as err:
                print("Something went wrong when extracting movie info:" + str(err))
                return None, {}
            else:
                # check if the combination of movie's name and director is already in the database
                with self._engine.connect() as connection:
                    search_result = connection.execute(query_check_movie_exist, params).fetchone()
                    if search_result is not None:
                        search_result = connection.execute(query_check_movie_exist, params)
                        for row in search_result:
                            found_movie_info = {
                                row.name: {"year": row.year, "rating": row.rating, "director": row.director,
                                           "id": row.id}}
                        # if there is a match,
                        # check if "year" and "rating" info of input movie
                        # match the found_movie from database
                        if found_movie_info[list(found_movie_info.keys())[0]]["year"] == params["year"] and \
                                found_movie_info[list(found_movie_info.keys())[0]]["rating"] == params["rating"]:
                            print("the movie exists in the database")
                            return True, {}
                        else:
                            print(
                                f"The Movie {params['name']} from director {params['director']} already exists the database!")
                            print(
                                "However there are some conflicting information between the input movie and the matched movie in the database")
                            return True, found_movie_info
                    else:
                        return False, {}
        else:
            print("""input should be a dict with the following format: Example: {"movie_name":{"year":1994, "rating":9.8, "director":"Michael Bay"}}
                        """)
            return None, {}

    def add_user(self, user):
        """
        :param user: a string of user name
        :return:
        False when add operation fails
        True when add operation succeeds
        """
        # SQL Check if the user is already in the sqlite database
        # Since the user's name in the table users is set to UNIQUE in SQL
        # Only add the new username if the name hasn't been taken yet
        try:
            query = text("INSERT INTO users (name) VALUES (:user)")
            params = {"user": user}
            # add user to the database using parameterised query
            with self._engine.connect() as connection:
                connection.execute(query, params)
                connection.commit()
        except Exception as err:
            print("Can not add user into database:" + str(err))
            return False
        else:
            print("User added successfully")
            return True

    def add_movie(self, movie):
        """
        :param movie: should be a dict with a following structure as an example:
        {"movie_name":{"year":1994, "rating":9.8, "director":"Michael Bay"}}
        :return:
        False when the add operation fails
        True when the add operation succeeds
        """
        query_add_movie = text(
            """INSERT INTO movies (name, year, rating, director) VALUES(:name, :year, :rating, :director)""")
        query_check_movie_exist = text("""SELECT * FROM movies WHERE name = :name AND director = :director LIMIT 1""")
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
                    if search_result is not None:
                        print("Movie is already in the database!")
                        return False
                    else:
                        connection.execute(query_add_movie, params)
                        connection.commit()
                        print("Movie added successfully!")
                        return True
        else:
            print("""input should be a dict with the following format: Example: {"movie_name":{"year":1994, "rating":9.8, "director":"Michael Bay"}}
            """)
            return False

    def add_movie_to_user_favorite(self, user_id: int, movie_id: int):
        """
        :param user_id: INTEGER
        :param movie_id: INTEGER
        :return:
            TRUE when operation success
            FALSE when operation fails
        """
        query_check_user_id = text("SELECT * FROM users WHERE users.id = :user_id LIMIT 1;")
        query_check_movie_id = text("SELECT * FROM movies WHERE movies.id = :movie_id LIMIT 1;")
        query_check_userid_movieid_pair = text("SELECT * FROM user_favorites WHERE user_id = :user_id AND movie_id = :movie_id")
        query_add_user_favorite = text("INSERT INTO user_favorites (user_id, movie_id) VALUES (:user_id, :movie_id);")
        params = {
            "user_id": user_id,
            "movie_id": movie_id,
        }
        # check if user_id and movie_id exists
        try:
            with self._engine.connect() as connection:
                user_result = connection.execute(query_check_user_id, params).scalar()
                movie_result = connection.execute(query_check_movie_id, params).scalar()
                print("user_result: ", user_result)
                print("movie_result: ", movie_result)
        except Exception as err:
            print("Something is wrong when connection with database: " + str(err))
        else:
            # user_result and movie_result not empty (meaning user and movie found)
            # add them to the user_favorites table
            if user_result and movie_result:
                try:
                    with self._engine.connect() as connection:
                        #check if user_id and movie_id pair exists in user_favorites table
                        user_movie_pair_result = connection.execute(query_check_userid_movieid_pair, params).scalar()
                        #if the pair doesn't exist, add the input user_id and movie_id pair to the user_favorites table
                        if not user_movie_pair_result:
                            connection.execute(query_add_user_favorite, params)
                            connection.commit()
                        else:
                            print("the user_id and movie_id pair already exists in user_favorites database")
                            return False
                except Exception as err:
                    print("Something is wrong when adding user and movie to database: " + str(err))
                    return False
                else:
                    print("User and movie added successfully to the user_favorites database")
                    return True
            else:
                print("User_id or movie_id or both don't exist! Can't add them to the user favorite list")
                return False

    def update_movie(self, movie):
        """
        update the information of an existing movie in the database
        User should be able to input updated information for the to be updated movie
        (name, year, title, director, movie_id ) and
        the function will handle the interaction and changes in the database

        :param movie: should be a dict with a following structure as an example:
        {"movie_name":{"year":1994, "rating":9.8, "director":"Michael Bay", "id":2}}

        :return:
        False when the update operation fails
        True when the update operation succeeds
        """
        query_update_movie = text(
            """
               UPDATE movies 
               SET year = :year, rating = :rating, director = :director, name = :name
               WHERE movies.id = :movie_id
            """
        )
        query_check_movie_id = text(
            """SELECT movies.id FROM movies WHERE movies.name = :name AND movies.director = :director LIMIT 1"""
        )

        if not isinstance(movie, dict) or not movie:
            print(
                "Invalid input format. Expected: {'movie_name': {'year': 1994, 'rating': 9.8, 'director': 'Michael Bay', 'id': 2}}")
            return False

        try:
            movie_title_key = list(movie.keys())[0]
            params = {
                "name": movie_title_key,
                "year": movie[movie_title_key]['year'],
                "rating": movie[movie_title_key]['rating'],
                "director": movie[movie_title_key]['director'],
                "movie_id": int(movie[movie_title_key]['id'])
            }
        except Exception as err:
            print("Error extracting movie info:", err)
            return False

        with self._engine.connect() as connection:
            try:
                search_result = connection.execute(query_check_movie_id, params).fetchone()
                search_movie_id = int(search_result[0]) if search_result else None

                if search_movie_id is None:
                    print("The movie does not exist in the database. Proceeding with update.")
                    connection.execute(query_update_movie, params)
                    connection.commit()
                    return True
                elif search_movie_id != params['movie_id']:
                    print(f"Duplicate movie name and director found. Update not allowed. search_movie_id: {search_movie_id}, movie_id: {type(params['movie_id'])}")
                    return False
                else:
                    connection.execute(query_update_movie, params)
                    connection.commit()
                    return True
            except Exception as e:
                print("Database update error:", e)
                return False  # Explicitly return False on failure

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
                    # with self._engine.connect() as connection:
                    connection.execute(query_delete_user, params)
                    connection.commit()
                    print("The user was deleted from the database")
                    return True
                else:
                    print("The user doesn't exist in the database")
                    return False

    def delete_user_favorite_movie(self, user_id, movie_id):
        """
                Delete a movie from an user's favorite list from table user_favorites
                :param user_id: INTEGER, movie_id: INTEGER
                :return:
                    True if delete operation succeeds
                    False if delte operation fails
                """
        query_delete_user = text("""
                    DELETE FROM user_favorites WHERE user_id = :user_id AND movie_id = :movie_id
                """)
        if isinstance(user_id, int) and isinstance(movie_id, int):
            params = {
                "user_id": user_id,
                "movie_id": movie_id
            }
            try:
                with self._engine.connect() as connection:
                    connection.execute(query_delete_user, params)
                    connection.commit()
            except Exception as err:
                print("Can not delete users from database:" + str(err))
                return False
            else:
                print("The user was deleted from the database")
                return True

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
                    # with self._engine.connect() as connection:
                    connection.execute(query_delete_movie, params)
                    connection.commit()
                    print("The movie was deleted from the database")
                    return True
                else:
                    print("The movie doesn't exist in the database")
                    return False

"""
data_manager_obj = SQLiteDataManager('movie_sql_db.sqlite')
data_manager_obj.get_user_movies(2)

"""

