import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

# Set the OMDb API_KEY - use only the key without the full URL
OMDB_API_KEY = 'a6d89722'  # Replace with your own OMDb API Key

# Set the page layout and design
st.set_page_config(
    page_title="Advanced Movie Recommendation System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fetch movie poster using OMDb API
def get_movie_poster_from_omdb(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get('Response') == 'True':
            return data.get('Poster')  # Movie poster from OMDb
        else:
            return None
    except Exception as e:
        st.error(f"Error occurred while fetching the poster from OMDb: {str(e)}")
        return None

@st.cache_data
def load_data():
    try:
        data = pd.read_csv(r'D:\assignment data engineering\transform\integrate_Data.csv')
        
        # Check for the presence of essential columns
        required_columns = ['Title', 'Genres', 'Rating', 'Directors', 'Actors']
        if not all(col in data.columns for col in required_columns):
            st.error("The file does not contain all the required columns!")
            return None

        # Process the genres column
        def process_genres(genre_str):
            try:
                if pd.isna(genre_str):
                    return ''
                if isinstance(genre_str, str):
                    genre_str = genre_str.replace('[', '').replace(']', '').replace("'", "")
                    genres = [g.strip() for g in genre_str.split(',')]
                    return ' '.join(genres)
                return str(genre_str)
            except:
                return ''
        
        data['Genres_Processed'] = data['Genres'].apply(process_genres)
        return data
    
    except Exception as e:
        st.error(f"Error occurred while loading the file: {str(e)}")
        return None

data = load_data()

if data is None:
    st.stop()

@st.cache_resource
def train_model(_data):
    try:
        _data['Combined_Features'] = _data['Genres_Processed'] + ' ' + \
                                   _data['Directors'].str.replace(',', ' ') + ' ' + \
                                   _data['Actors'].str.replace(',', ' ')
        
        tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = tfidf.fit_transform(_data['Combined_Features'])
        return cosine_similarity(tfidf_matrix), tfidf
    except Exception as e:
        st.error(f"Error occurred while training the model: {str(e)}")
        return None, None

cosine_sim, tfidf_model = train_model(data)

if cosine_sim is None:
    st.stop()

# Custom CSS styling for the app
st.markdown("""
<style>
    .main {
        background-color: #0d1117;
        color: #ffffff;
        padding: 20px;
    }
    .movie-card {
        background-color: #161b22;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(255,255,255,0.05);
        padding: 20px;
        margin-bottom: 25px;
        border: 1px solid #30363d;
    }
    .movie-title {
        color: #58a6ff;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .movie-info {
        margin-top: 15px;
        padding: 10px;
        background-color: #21262d;
        border-radius: 8px;
        color: #c9d1d9;
    }
    .similarity-score {
        background-color: #238636;
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    .rating-badge {
        background-color: #fbbf24;
        color: #1f2937;
        padding: 5px 10px;
        border-radius: 10px;
        font-weight: bold;
        display: inline-block;
    }
    .genre-badge {
        background-color: #10b981;
        color: white;
        padding: 5px 10px;
        border-radius: 10px;
        margin-right: 5px;
        display: inline-block;
    }
    .director-badge {
        background-color: #3b82f6;
        color: white;
        padding: 5px 10px;
        border-radius: 10px;
        display: inline-block;
    }
    .section-divider {
        margin: 40px 0;
        border-top: 2px solid #30363d;
    }
    .recommendation-title {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 25px;
        color: #58a6ff;
        text-align: center;
    }
    [data-testid="stMetric"] {
        background-color: #21262d;
        color: white;
        padding: 5px;
        border-radius: 10px;
    }
    [data-testid="stMetricValue"] {
        color: white !important;
    }
    [data-testid="stMetricLabel"] {
        color: #c9d1d9 !important;
    }
</style>
""", unsafe_allow_html=True)


st.title('🎬 Advanced Movie Recommendation System')

# Default movie index
try:
    default_index = int(data[data['Title'] == "The Shawshank Redemption"].index[0]) \
        if "The Shawshank Redemption" in data['Title'].values else 0
except:
    default_index = 0

movie_title = st.selectbox(
    'Choose a movie:',
    data['Title'].sort_values(),
    index=default_index
)

# Display information about the selected movie
selected_idx = data[data['Title'] == movie_title].index[0]
selected_movie = data.iloc[selected_idx]
poster_url = get_movie_poster_from_omdb(movie_title)

# Add space before displaying selected movie details
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Display movie poster and details
st.markdown(f"<h2 class='movie-title'>Movie Information: {movie_title}</h2>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        if poster_url:
            st.image(poster_url, caption=movie_title, width=250)
        else:
            st.image("https://via.placeholder.com/250x375?text=No+Poster", caption=movie_title, width=250)

    with col2:
        st.markdown("<div class='movie-info'>", unsafe_allow_html=True)
        st.markdown(f"<span class='rating-badge'>⭐ Rating: {selected_movie['Rating']}</span>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"<span class='genre-badge'>🎭 Genres: {selected_movie['Genres_Processed']}</span>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"<span class='director-badge'>🎬 Director: {selected_movie['Directors']}</span>", unsafe_allow_html=True)
        
        if 'Actors' in selected_movie and not pd.isna(selected_movie['Actors']):
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.write(f"**🎭 Actors:** {selected_movie['Actors']}")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Add space before recommendation button
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    recommendation_button = st.button('Recommend Similar Movies', use_container_width=True)

if recommendation_button:
    try:
        idx = data[data['Title'] == movie_title].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:6]  # Top 5 recommendations
        
        # Add space before displaying recommendations
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='recommendation-title'>Similar Movies to {movie_title}</h2>", unsafe_allow_html=True)
        
        cols = st.columns(2)
        for i, (movie_idx, score) in enumerate(sim_scores):
            movie = data.iloc[movie_idx]
            movie_poster_url = get_movie_poster_from_omdb(movie['Title'])  # Fetch movie poster
            
            with cols[i % 2]:
                st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                st.markdown(f"<h3 class='movie-title'>{i+1}. {movie['Title']}</h3>", unsafe_allow_html=True)
                
                # Display image - if not available, show placeholder
                if movie_poster_url:
                    st.image(movie_poster_url, caption=movie['Title'], use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/250x375?text=No+Poster", 
                            caption=movie['Title'], use_column_width=True)
                
                # Adjust similarity score display
                st.markdown(f"<div class='similarity-score'>Similarity Score: {score:.2f}</div>", unsafe_allow_html=True)
                st.markdown("<div class='movie-info'>", unsafe_allow_html=True)
                st.markdown(f"<span class='rating-badge'>⭐ Rating: {movie['Rating']}</span>", unsafe_allow_html=True)
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown(f"<span class='genre-badge'>🎭 Genres: {movie['Genres_Processed']}</span>", unsafe_allow_html=True)
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown(f"<span class='director-badge'>🎬 Director: {movie['Directors'].split(',')[0]}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Error occurred while generating recommendations: {str(e)}")

# Add space before displaying raw data
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Display raw data
with st.expander("Show Raw Data", expanded=False):
    st.dataframe(data[['Title', 'Genres', 'Rating', 'Directors']].head(20))

# System Information Section
with st.sidebar:
    st.header("System Information")
    st.write(f"Number of movies: {len(data)}")
    st.write("Available columns:")
    st.write(list(data.columns))
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
