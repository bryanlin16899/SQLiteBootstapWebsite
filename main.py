from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
TMDB_API_KEY = "bb100261e5ce720c7dea6336df10ad40"
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies_data_n.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Movie> {self.title}"


db.create_all()


class EditForm(FlaskForm):
    rating = StringField(label="Rating Out Of 10 e.g.7.5", validators=[DataRequired()])
    review = StringField(label="Your Review")
    submit = SubmitField(label="Done")

class AddForm(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    print(all_movies)
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies)-i
    db.session.commit()
    return render_template("index.html", all_movies=all_movies)


@app.route("/add", methods=["GET", "POST"])
def find_movie():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        rqst = requests.get(url="https://api.themoviedb.org/3/search/movie",
                            params={"api_key": TMDB_API_KEY, "query": movie_title})
        data = rqst.json()["results"]
        return render_template("select.html", options=data)
    return render_template("add.html", form=form)


@app.route("/add_movie")
def add_movie():
    movie_id = request.args.get("selected")
    if movie_id:
        rqst = requests.get(url=f"https://api.themoviedb.org/3/movie/{movie_id}",
                            params={"api_key": TMDB_API_KEY}).json()
        print(rqst)
        new_movie = Movie(
            title=rqst["original_title"],
            year=rqst["release_date"],
            description=rqst["overview"],
            img_url=f"https://www.themoviedb.org/t/p/w300_and_h450_bestv2{rqst['poster_path']}")
        db.session.add(new_movie)
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/edit", methods=["POST", "GET"])
def edit_movie():
    form = EditForm()
    if form.validate_on_submit():
        # Get selected movie id
        movie_id = request.args.get("id")
        movie_selected = Movie.query.get(movie_id)
        movie_selected.rating = form.rating.data
        movie_selected.review = form.review.data
        db.session.commit()
        print("check")
        return redirect(url_for('home'))
    return render_template("edit.html", form=form)


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie_selected = Movie.query.get(movie_id)
    db.session.delete(movie_selected)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
