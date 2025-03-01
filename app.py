from flask import Flask, render_template, request, url_for
from flask_cors import CORS
from werkzeug.utils import redirect
from dotenv import load_dotenv
import os
import requests

load_dotenv()
OMDB_API_KEY = os.getenv('OMDB_API_KEY')

from datamanager.sqlite_data_manager import SQLiteDataManager

app = Flask(__name__)
CORS(app)
data_manager = SQLiteDataManager('./datamanager/movie_sql_db.sqlite')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/users')
def list_users():
    """
    This route will present a list of all users registered in our MovieWeb App.
    :return:
    """
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def get_user_movies(user_id):
    """
    This route will exhibit a specific user’s list of favorite movies.
    We will use the <user_id> in the route
    to fetch the appropriate user’s movies.
    :param user_id:
    :return:
    """
    movies = data_manager.get_user_movies(user_id)
    user = data_manager.get_user_by_id(user_id)
    return render_template('user_movies.html', user=user, movies=movies)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    This route will present a form that enables the addition
    of a new user to our MovieWeb App.
    :return:
    """
    if request.method == 'GET':
        return render_template('add_user.html')
    if request.method == 'POST':
        new_user_name = request.form['username']
        print("new_user_name: ", new_user_name)
        try:
            data_manager.add_user(new_user_name)
            return redirect(url_for('list_users'))
        except Exception as err:
            error_msg = "Can not add user: " + str(err)
            return render_template('error_msg.html', error_msg=error_msg)


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie_to_user(user_id):
    """
    This route will display a form to add a new movie to a user’s list of favorite movies.
    :param user_id:
    :return:
    """
    if request.method == 'GET':
        user = data_manager.get_user_by_id(user_id)
        return render_template("add_movie_to_user.html", user=user, existing_movie={})

    if request.method == 'POST':
        user = data_manager.get_user_by_id(user_id)
        movie_name = request.form.get('movie_name')
        director = request.form.get('director')
        year = None
        rating = None
        # fetching movie details from OMDB database
        if movie_name and director:
            url_get_movie_by_title_omdb = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_name}"
            try:
                response = requests.get(url_get_movie_by_title_omdb, timeout=2.50)
            except Exception as err:
                error_msg = "Something went wrong when trying to connect to omdb database: " + str(err)
                return render_template("error_msg.html", error_msg=error_msg),400
            else:
                response_json = response.json()
                if "Director" not in response_json:
                    return render_template("error_msg.html", error_msg="Movie not found in OMDB database"), 404
                else:
                    director_omdb = response_json['Director'].lower()
                # if the input director matches the director from OMDB, get year and rating details
                # from OMDB to complete the movie info
                if director.lower() == director_omdb:
                    year = response.json()['Year']
                    rating = response.json()['imdbRating']
                    print(movie_name, director, year, rating)
                else:
                    return render_template("error_msg.html",
                                           error_msg="can not find the movie title from the given director in OMDB database"),404

        # get the POST response from add_movie_to_user when
        # there is an existing title in the sqlite database with the same director
        # but with conflicting information (unmatched year or rating)
        use_existing_movie = request.form.get('use_existing_movie')
        existing_movie_id = request.form.get('movie_id')
        if movie_name and year and rating and director:
            input_movie = {
                f"{movie_name}": {
                    "year": f"{year}",
                    "rating": f"{rating}",
                    "director": f"{director}"
                }
            }
            # Check if the movie already existed in the sqlite database
            is_movie, movie_info_dict = data_manager.is_movie_exist(input_movie)
            print("movie_info_dict:", movie_info_dict)
            print("is_movie:", is_movie)
            # check if the movie exists in the database
            if is_movie:
                return render_template("add_movie_to_user.html", user=user, existing_movie=movie_info_dict),200
            # if the movie doesn't exist and movie_info_dict is empty
            elif not is_movie and not movie_info_dict:
                # add the new movie into the database
                data_manager.add_movie(input_movie)
                # find the movie_id of the newly added movie from the database
                movies = data_manager.get_all_movies()
                input_movie_id = 0
                # extract the movie information from the database
                print("movies:", movies, type(movies))
                for movie, details in movies.items():
                    # if the user input movie_name and director match the movie's name and director from the database
                    if movie_name == movie and director == details['director']:
                        input_movie_id = details['id']
                # check if input_movie_id receives a meaningful value from the extraction instead of the init value 0
                if input_movie_id != 0:
                    # add the movie_id to the user_favorite table in database
                    data_manager.add_movie_to_user_favorite(user_id=user_id, movie_id=input_movie_id)
                return redirect(url_for('get_user_movies', user_id=user_id))
        if use_existing_movie is not None:
            if use_existing_movie == "true":
                data_manager.add_movie_to_user_favorite(user_id=user_id, movie_id=int(existing_movie_id))
                return redirect(url_for('get_user_movies', user_id=user_id))
            else:
                return redirect(url_for('get_user_movies', user_id=user_id))
        else:
            return render_template("error_msg.html",
                            error_msg="Something when wrong while choosing whether or not to take the existing movie in the sqlite database to add to user's favorite list"),404

@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    This route will display a form allowing for
    the updating of details
    of a specific movie in a user’s list.
    :return:
    """
    if request.method == "GET":
        movie = data_manager.get_movie_by_id(movie_id)
        user = data_manager.get_user_by_id(user_id)
        return render_template("update_movie.html", movie=movie, user=user)

    if request.method == "POST":
        movie_name = request.form.get('movie_name')
        year = request.form.get('year')
        rating = request.form.get('rating')
        director = request.form.get('director')
        movie = {f"{movie_name}": {"year": year, "rating": rating, "director": director, "id": movie_id}}
        if year and rating and director and movie:
            try:
                update_movie_status = data_manager.update_movie(movie)
            except Exception as err:
                error_msg = "Can not update movie" + str(err)
                return render_template('error_msg.html', error_msg=error_msg)
            else:
                if update_movie_status:
                    return redirect(url_for('get_user_movies', user_id=user_id))
                else:
                    return render_template('error_msg.html', error_msg="Can not update movie")
        else:
            return render_template('error_msg.html',
                                   error_msg="Can not update movie because the required data was not complete")

@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    """
    Upon visiting this route,
    a specific movie will be removed
    from a user’s favorite movie list.
    :param user_id: INT
    :param movie_id: INTEGER
    :return: go back to get_user_movies route
    to show the refreshed list of user's favorite movies
    """
    data_manager.delete_user_favorite_movie(user_id, movie_id)
    return redirect(url_for('get_user_movies', user_id=user_id))


if __name__ == '__main__':
    app.run(debug=True)
