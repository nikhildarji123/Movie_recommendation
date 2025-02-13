from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests

app = Flask(__name__)

def fetch_poster(movie_id):
    try:

        response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id))
        data = response.json()
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    except:
        return "https://via.placeholder.com/150x225?text=No+Image"

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]
    
        recommend_movies = []
        recommended_posters = []
        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
    
            recommend_movies.append(movies.iloc[i[0]].title)
            recommended_posters.append(fetch_poster(movie_id))
        return recommend_movies, recommended_posters
    except IndexError:
        flask("movie not found. please select a valid movie.")
        return [],[]

# Load the movie data from the pickle file
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity_movies.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

def get_random_movies(num=15):
    random_movies = movies.sample(n=num)
    movie_data = []
    for _, row in random_movies.iterrows():
        movie_name = row['title']
        movie_id = row['movie_id']
        poster = fetch_poster(movie_id)
        movie_data.append((movie_name, poster))
    return movie_data

@app.route('/', methods=['GET', 'POST'])
def movie_recommendation():
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        if movie_name not in movies['title'].values:
            flash("Invalid movie selected. Please choose a movie from the list.")
            return redirect(url_for('movie_recommendation'))

        names, posters = recommend(movie_name)
        movie_data = list(zip(names, posters))
        return render_template('recommendation.html', movie_name=movie_name, movie_data=movie_data)
    
    random_movie_data = get_random_movies()
    return render_template('index.html', movie_names=movies['title'].values.tolist(), random_movie_data=random_movie_data)

if __name__ == '__main__':
    app.run(debug=True)

