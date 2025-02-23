from flask import Flask, render_template
from flask_cors import CORS
from datamanager.sqlite_data_manager import SQLiteDataManager

app = Flask(__name__)
CORS(app)
data_manager = SQLiteDataManager('./datamanager/movie_sql_db.sqlite')

@app.route('/')
def home():
    return "Welcome to MovieWeb App!"

@app.route('/users')
def list_users():
    """
    This route will present a list of all users registered in our MovieWeb App.
    :return:
    """
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)

@app.route('/users/<user_id>')
def get_user_movies(user_id):
    """
    This route will exhibit a specific user’s list of favorite movies.
    We will use the <user_id> in the route
    to fetch the appropriate user’s movies.
    :param user_id:
    :return:
    """
    pass

@app.route('/add_user')
def add_user():
    """
    This route will present a form that enables the addition
    of a new user to our MovieWeb App.
    :return:
    """
    pass
@app.route('/users/<user_id>/add_movie')
def add_movie_to_user(user_id):
    """
    This route will display a form to add a new movie to a user’s list of favorite movies.
    :param user_id:
    :return:
    """
    pass

@app.route('/users/<user_id>/update_movie/<movie_id>')
def update_movie(user_id, movie_id):
    """
    This route will display a form allowing for
    the updating of details
    of a specific movie in a user’s list.
    :return:
    """
    pass

@app.route('/users/<user_id>/update_movie/<movie_id>')
def delete_movie(user_id, movie_id):
    """
    Upon visiting this route,
    a specific movie will be removed
    from a user’s favorite movie list.
    :param user_id:
    :param movie_id:
    :return:
    """
    pass

if __name__ == '__main__':
    app.run(debug=True)