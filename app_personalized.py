#!/usr/bin/env python3
"""
Personalized Movie Recommender System - Questionnaire-Based
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import sys
from pathlib import Path
from models.recommendation_engine import PersonalizedRecommendationEngine
from models.llm_engine import CohereLLMEngine
import random
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Page configuration
st.set_page_config(
    page_title="Personalized Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme with matte finish
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Global text styling */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #00d4aa !important;
    }
    
    .stApp p, .stApp div, .stApp span, .stApp label {
        color: #fafafa !important;
    }
    
    /* Specific text color fixes */
    .stMarkdown {
        color: #fafafa !important;
    }
    
    .stMarkdown p {
        color: #fafafa !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #00d4aa !important;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #00d4aa;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(0, 212, 170, 0.3);
    }
    
    .movie-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: #fafafa;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        border: 1px solid rgba(0, 212, 170, 0.2);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .movie-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(0, 212, 170, 0.05) 50%, transparent 70%);
        pointer-events: none;
    }
    
    .movie-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #00d4aa;
        text-shadow: 0 0 10px rgba(0, 212, 170, 0.3);
    }
    
    .movie-info {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0.3rem 0;
        color: #e0e0e0;
    }
    
    .question-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #fafafa;
        padding: 2rem;
        border-radius: 1rem;
        border-left: 5px solid #00d4aa;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .profile-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: #fafafa;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        border: 1px solid rgba(0, 212, 170, 0.3);
    }
    
    .streaming-link {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-decoration: none;
        display: inline-block;
        margin: 0.2rem 0.2rem 0.2rem 0;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
        transition: all 0.3s ease;
    }
    
    .streaming-link:hover {
        background: linear-gradient(135deg, #ff5252 0%, #e53935 100%);
        color: white;
        text-decoration: none;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00d4aa 0%, #00a085 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(0, 212, 170, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00a085 0%, #007a6b 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.4);
    }
    
    /* Secondary button styling */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
        color: white;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #5a6268 0%, #495057 100%);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: #1a1a2e;
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 0.5rem;
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div {
        background-color: #1a1a2e;
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 0.5rem;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background: linear-gradient(135deg, #00d4aa 0%, #00a085 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #0e1117 !important;
    }
    
    /* Sidebar specific styling */
    .css-1lcbmhc {
        background-color: #0e1117 !important;
    }
    
    .css-1d391kg .css-1lcbmhc {
        background-color: #0e1117 !important;
    }
    
    /* Additional sidebar selectors */
    section[data-testid="stSidebar"] {
        background-color: #0e1117 !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background-color: #0e1117 !important;
    }
    
    .stSidebar {
        background-color: #0e1117 !important;
    }
    
    /* Sidebar text styling */
    .css-1d391kg h1,
    .css-1d391kg h2,
    .css-1d391kg h3,
    .css-1d391kg p,
    .css-1d391kg div,
    .css-1d391kg span {
        color: #fafafa !important;
    }
    
    /* Sidebar selectbox styling */
    .css-1d391kg .stSelectbox > div > div {
        background-color: #1a1a2e;
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 0.5rem;
        color: #fafafa;
    }
    
    /* Sidebar success message styling */
    .css-1d391kg .stSuccess {
        background-color: rgba(0, 212, 170, 0.1);
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 0.5rem;
        color: #00d4aa;
    }
    
    /* Sidebar info message styling */
    .css-1d391kg .stInfo {
        background-color: rgba(0, 123, 255, 0.1);
        border: 1px solid rgba(0, 123, 255, 0.3);
        border-radius: 0.5rem;
        color: #00d4aa;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background-color: rgba(0, 212, 170, 0.1);
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 0.5rem;
    }
    
    .stError {
        background-color: rgba(255, 107, 107, 0.1);
        border: 1px solid rgba(255, 107, 107, 0.3);
        border-radius: 0.5rem;
    }
    
    .stWarning {
        background-color: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 0.5rem;
    }
    
    /* AI Explanation styling */
    .ai-explanation {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.1) 0%, rgba(0, 123, 255, 0.1) 100%);
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    .ai-explanation p {
        margin: 0;
        color: #00d4aa !important;
    }
    
    .stInfo {
        background-color: rgba(0, 123, 255, 0.1);
        border: 1px solid rgba(0, 123, 255, 0.3);
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load the processed data from CSV files"""
    try:
        data_dir = Path("data")
        if (data_dir / "processed_movies.csv").exists() and (data_dir / "processed_ratings.csv").exists():
            movies_df = pd.read_csv(data_dir / "processed_movies.csv")
            ratings_df = pd.read_csv(data_dir / "processed_ratings.csv")
            return movies_df, ratings_df
        else:
            st.error("❌ Data not found. Please run setup.py first.")
            return None, None
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None, None

def load_user_profile():
    """Load user profile from JSON file"""
    profile_file = Path("user_profile.json")
    if profile_file.exists():
        try:
            with open(profile_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_profile(profile):
    """Save user profile to JSON file"""
    profile_file = Path("user_profile.json")
    try:
        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2)
        return True
    except:
        return False

def load_user_history():
    """Load user's movie history"""
    history_file = Path("user_history.json")
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except:
            return {"watched_movies": [], "liked_movies": [], "disliked_movies": [], "current_recommendations": []}
    return {"watched_movies": [], "liked_movies": [], "disliked_movies": [], "current_recommendations": []}

def save_user_history(history):
    """Save user's movie history"""
    history_file = Path("user_history.json")
    try:
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        return True
    except:
        return False

class PersonalizedRecommendationEngine:
    """Personalized recommendation engine based on questionnaire and user history"""
    
    def __init__(self, movies_df, ratings_df):
        self.movies_df = movies_df
        self.ratings_df = ratings_df
        
        # Create user-movie matrix for collaborative filtering
        self.user_movie_matrix = ratings_df.pivot(
            index='userId', 
            columns='movieId', 
            values='rating'
        ).fillna(0)
        
        # Movie metadata for enhanced recommendations
        self.movie_stats = ratings_df.groupby('movieId').agg({
            'rating': ['count', 'mean']
        }).round(2)
        self.movie_stats.columns = ['rating_count', 'avg_rating']
    
    def get_movie_metadata(self, movie_id):
        """Get enhanced movie metadata including IMDB-style rating and cast info"""
        movie_info = self.movies_df[self.movies_df['movieId'] == movie_id]
        if movie_info.empty:
            return None
        
        movie = movie_info.iloc[0]
        
        # Get rating info
        if movie_id in self.movie_stats.index:
            rating_info = self.movie_stats.loc[movie_id]
            imdb_rating = f"{rating_info['avg_rating']:.1f}/5.0"
            rating_count = int(rating_info['rating_count'])
        else:
            imdb_rating = "N/A"
            rating_count = 0
        
        # Generate mock cast (in real app, this would come from TMDB API)
        cast = self._generate_mock_cast(movie['title'], movie_id)
        
        # Generate streaming links (in real app, this would come from JustWatch API)
        streaming_links = self._generate_streaming_links(movie['title'], movie_id)
        
        return {
            'title': movie['title'],
            'year': movie['year'] if pd.notna(movie['year']) else 'Unknown',
            'genres': eval(movie['genres']) if isinstance(movie['genres'], str) else movie['genres'],
            'imdb_rating': imdb_rating,
            'rating_count': rating_count,
            'cast': cast,
            'streaming_links': streaming_links
        }
    
    def _generate_mock_cast(self, title, movie_id):
        """Generate consistent mock cast information based on movie ID"""
        # Use movie_id as seed for consistent results
        random.seed(movie_id)
        mock_cast = [
            "Tom Hanks", "Meryl Streep", "Leonardo DiCaprio", "Emma Stone",
            "Ryan Gosling", "Jennifer Lawrence", "Brad Pitt", "Scarlett Johansson",
            "Robert Downey Jr.", "Chris Evans", "Natalie Portman", "Ryan Reynolds"
        ]
        result = random.sample(mock_cast, min(3, len(mock_cast)))
        random.seed()  # Reset seed
        return result
    
    def _generate_streaming_links(self, title, movie_id):
        """Generate consistent mock streaming links based on movie ID"""
        # Use movie_id as seed for consistent results
        random.seed(movie_id)
        streaming_platforms = [
            {"name": "Netflix", "url": "https://netflix.com"},
            {"name": "Amazon Prime", "url": "https://primevideo.com"},
            {"name": "Disney+", "url": "https://disneyplus.com"},
            {"name": "Hulu", "url": "https://hulu.com"},
            {"name": "HBO Max", "url": "https://hbomax.com"}
        ]
        result = random.sample(streaming_platforms, random.randint(1, 3))
        random.seed()  # Reset seed
        return result
    
    def get_personalized_recommendations(self, profile, user_history, n_recommendations=10, exclude_movies=None, include_current=False):
        """Get personalized recommendations based on profile and history"""
        # Get user preferences from profile
        preferred_genres = profile.get('preferred_genres', [])
        mood = profile.get('mood', 'neutral')
        personality = profile.get('personality', 'balanced')
        
        # Get watched movies to avoid recommending them
        watched_movies = set(user_history.get('watched_movies', []))
        liked_movies = set(user_history.get('liked_movies', []))
        disliked_movies = set(user_history.get('disliked_movies', []))
        current_recommendations = set(user_history.get('current_recommendations', []))
        
        # Start with all movies
        candidate_movies = self.movies_df.copy()
        
        # Filter out watched movies and disliked movies
        exclude_set = watched_movies | disliked_movies
        
        # Only exclude current recommendations if not including them
        if not include_current:
            exclude_set = exclude_set | current_recommendations
            
        if exclude_movies:
            exclude_set.update(exclude_movies)
        
        candidate_movies = candidate_movies[~candidate_movies['movieId'].isin(exclude_set)]
        
        # Apply genre preferences
        if preferred_genres:
            genre_mask = candidate_movies['genres'].apply(
                lambda x: any(genre in (eval(x) if isinstance(x, str) else x) for genre in preferred_genres)
            )
            candidate_movies = candidate_movies[genre_mask]
        
        # Apply mood-based filtering
        candidate_movies = self._apply_mood_filter(candidate_movies, mood)
        
        # Apply personality-based filtering
        candidate_movies = self._apply_personality_filter(candidate_movies, personality)
        
        # Score movies based on multiple factors
        scored_movies = []
        for _, movie in candidate_movies.iterrows():
            score = self._calculate_movie_score(movie, profile, user_history)
            scored_movies.append((movie['movieId'], score))
        
        # Sort by score and return top recommendations
        scored_movies.sort(key=lambda x: x[1], reverse=True)
        
        # Add some randomness to avoid always getting the same recommendations
        import random
        if len(scored_movies) > n_recommendations:
            # Take top 50% and shuffle them, then take top n_recommendations
            top_candidates = scored_movies[:min(50, len(scored_movies))]
            random.shuffle(top_candidates)
            return top_candidates[:n_recommendations]
        
        return scored_movies[:n_recommendations]
    
    def _apply_mood_filter(self, movies_df, mood):
        """Apply mood-based filtering to movies"""
        mood_genre_mapping = {
            'happy': ['Comedy', 'Musical', 'Animation', 'Family'],
            'sad': ['Drama', 'Romance', 'Musical'],
            'excited': ['Action', 'Adventure', 'Thriller', 'Sci-Fi'],
            'relaxed': ['Drama', 'Romance', 'Documentary', 'Mystery'],
            'adventurous': ['Action', 'Adventure', 'Sci-Fi', 'Fantasy'],
            'romantic': ['Romance', 'Drama', 'Comedy'],
            'mysterious': ['Mystery', 'Thriller', 'Crime', 'Horror'],
            'neutral': []  # No filtering for neutral mood
        }
        
        if mood in mood_genre_mapping and mood_genre_mapping[mood]:
            preferred_genres = mood_genre_mapping[mood]
            genre_mask = movies_df['genres'].apply(
                lambda x: any(genre in (eval(x) if isinstance(x, str) else x) for genre in preferred_genres)
            )
            return movies_df[genre_mask]
        
        return movies_df
    
    def _apply_personality_filter(self, movies_df, personality):
        """Apply personality-based filtering to movies"""
        personality_genre_mapping = {
            'introvert': ['Drama', 'Mystery', 'Documentary', 'Romance'],
            'extrovert': ['Comedy', 'Action', 'Musical', 'Adventure'],
            'analytical': ['Mystery', 'Thriller', 'Sci-Fi', 'Documentary'],
            'creative': ['Fantasy', 'Animation', 'Musical', 'Drama'],
            'balanced': []  # No filtering for balanced personality
        }
        
        if personality in personality_genre_mapping and personality_genre_mapping[personality]:
            preferred_genres = personality_genre_mapping[personality]
            genre_mask = movies_df['genres'].apply(
                lambda x: any(genre in (eval(x) if isinstance(x, str) else x) for genre in preferred_genres)
            )
            return movies_df[genre_mask]
        
        return movies_df
    
    def _calculate_movie_score(self, movie, profile, user_history):
        """Calculate personalized score for a movie"""
        score = 0.0
        
        # Base popularity score
        movie_id = movie['movieId']
        if movie_id in self.movie_stats.index:
            rating_info = self.movie_stats.loc[movie_id]
            popularity_score = rating_info['avg_rating'] * np.log(rating_info['rating_count'] + 1)
            score += popularity_score * 0.3
        
        # Genre preference score
        movie_genres = eval(movie['genres']) if isinstance(movie['genres'], str) else movie['genres']
        preferred_genres = profile.get('preferred_genres', [])
        if preferred_genres:
            genre_overlap = len(set(movie_genres) & set(preferred_genres))
            score += genre_overlap * 0.4
        
        # Year preference score
        preferred_decade = profile.get('preferred_decade', 'any')
        if preferred_decade != 'any' and pd.notna(movie['year']):
            movie_year = int(movie['year'])
            if preferred_decade == 'recent' and movie_year >= 2010:
                score += 0.2
            elif preferred_decade == 'classic' and movie_year < 2000:
                score += 0.2
            elif preferred_decade == '2000s' and 2000 <= movie_year < 2010:
                score += 0.2
        
        # Add some randomness for variety
        score += random.uniform(0, 0.1)
        
        return score

def show_questionnaire():
    """Display the personality and mood questionnaire"""
    st.markdown('<h1 class="main-header">🎬 Personalized Movie Recommender</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="question-card">
        <h2>🎭 Tell us about yourself!</h2>
        <p>Answer these questions to get personalized movie recommendations tailored just for you.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("questionnaire_form"):
        # Question 1: Favorite Genres
        st.subheader("🎭 What are your favorite movie genres? (Select up to 3)")
        all_genres = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 
                     'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 
                     'Sci-Fi', 'Thriller', 'War', 'Western']
        
        selected_genres = st.multiselect(
            "Choose your favorite genres:",
            all_genres,
            max_selections=3,
            help="Select the genres you enjoy most"
        )
        
        # Question 2: Current Mood
        st.subheader("😊 How are you feeling right now?")
        mood = st.selectbox(
            "Select your current mood:",
            ['happy', 'sad', 'excited', 'relaxed', 'adventurous', 'romantic', 'mysterious', 'neutral'],
            help="This helps us recommend movies that match your current mood"
        )
        
        # Question 3: Personality Type
        st.subheader("🧠 What's your personality like?")
        personality = st.selectbox(
            "Select your personality type:",
            ['introvert', 'extrovert', 'analytical', 'creative', 'balanced'],
            help="This influences the type of movies we recommend"
        )
        
        # Question 4: Preferred Era
        st.subheader("📅 What era of movies do you prefer?")
        preferred_decade = st.selectbox(
            "Select your preferred movie era:",
            ['recent', '2000s', 'classic', 'any'],
            help="Recent (2010+), 2000s (2000-2009), Classic (before 2000), or Any"
        )
        
        # Question 5: Movie Length Preference
        st.subheader("⏱️ How long do you like your movies?")
        length_preference = st.selectbox(
            "Select your preferred movie length:",
            ['short', 'medium', 'long', 'any'],
            help="Short (<90 min), Medium (90-120 min), Long (>120 min), or Any"
        )
        
        # Question 6: Viewing Context
        st.subheader("🏠 How do you usually watch movies?")
        viewing_context = st.selectbox(
            "Select your typical viewing context:",
            ['alone', 'with_friends', 'with_family', 'with_partner', 'any'],
            help="This helps us recommend movies suitable for your viewing situation"
        )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Get My Personalized Recommendations!", type="primary")
        
        if submitted:
            if len(selected_genres) == 0:
                st.error("Please select at least one genre!")
                return None
            
            # Create user profile
            profile = {
                'preferred_genres': selected_genres,
                'mood': mood,
                'personality': personality,
                'preferred_decade': preferred_decade,
                'length_preference': length_preference,
                'viewing_context': viewing_context,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            # Save profile
            if save_user_profile(profile):
                st.success("✅ Profile saved successfully!")
                return profile
            else:
                st.error("❌ Failed to save profile. Please try again.")
                return None
    
    return None

def show_recommendations_page(profile, movies_df, ratings_df):
    """Display personalized recommendations"""
    st.markdown('<h1 class="main-header">🎬 Your Personalized Recommendations</h1>', unsafe_allow_html=True)
    
    # Load user history
    user_history = load_user_history()
    
    # Initialize recommendation engine
    engine = PersonalizedRecommendationEngine(movies_df, ratings_df)
    
    # Check if we need to generate initial recommendations
    if not user_history.get('current_recommendations'):
        # Generate initial recommendations
        recommendations = engine.get_personalized_recommendations(profile, user_history, 10)
        if recommendations:
            # Save current recommendations
            user_history['current_recommendations'] = [movie_id for movie_id, _ in recommendations]
            save_user_history(user_history)
    else:
        # Use existing recommendations
        current_movie_ids = user_history['current_recommendations']
        recommendations = [(movie_id, 1.0) for movie_id in current_movie_ids]  # Placeholder scores
    
    if not recommendations:
        st.warning("No recommendations found. Please try adjusting your preferences.")
        return
    
    # Display profile summary
    st.markdown(f"""
    <div class="profile-card">
        <h3>👤 Your Profile</h3>
        <p><strong>Mood:</strong> {profile['mood'].title()}</p>
        <p><strong>Personality:</strong> {profile['personality'].title()}</p>
        <p><strong>Favorite Genres:</strong> {', '.join(profile['preferred_genres'])}</p>
        <p><strong>Preferred Era:</strong> {profile['preferred_decade'].title()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display recommendations
    st.subheader("🎬 Your Personalized Movie Recommendations")
    
    # Recommendation type selection
    st.markdown("### 🎯 Choose Your Recommendation Type")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🧠 Algorithm-Based Recommendations**
        - Based on your personality profile
        - Uses genre preferences and mood
        - Learns from your interaction history
        """)
    
    with col2:
        st.markdown("""
        **🤖 AI-Powered Search**
        - Natural language queries
        - "movies like inception"
        - "Brad Pitt movies"
        - "romantic comedy from the 90s"
        """)
    
    # Recommendation type selector
    recommendation_type = st.radio(
        "How would you like to get recommendations?",
        ["🧠 Algorithm-Based", "🤖 AI-Powered Search"],
        key="recommendation_type_selector"
    )
    
    if recommendation_type == "🤖 AI-Powered Search":
        # Natural language search interface
        st.markdown("### 🔍 Natural Language Search")
        st.markdown("Ask for movies in natural language! Try queries like:")
        st.markdown("- *'movies like inception'*")
        st.markdown("- *'Brad Pitt movies'*")
        st.markdown("- *'I want a romantic comedy from the 90s'*")
        st.markdown("- *'thriller movies with strong female leads'*")
        
        # Search input
        search_query = st.text_input(
            "What kind of movie are you looking for?",
            placeholder="e.g., 'Brad Pitt movies' or 'movies like inception'",
            key="natural_search_input"
        )
        
        # Search button
        if st.button("🔍 Search with AI", key="ai_search_btn"):
            if search_query.strip():
                with st.spinner("🤖 AI is analyzing your request..."):
                    try:
                        # Initialize LLM engine
                        llm_engine = CohereLLMEngine(movies_df, ratings_df)
                        
                        # Get LLM recommendations
                        llm_recommendations = llm_engine.get_llm_recommendations(
                            search_query, user_history, n_recommendations=10
                        )
                        
                        if llm_recommendations:
                            st.success(f"🎯 Found {len(llm_recommendations)} AI-powered recommendations!")
                            
                            # Display LLM recommendations
                            st.markdown("### 🤖 AI-Powered Recommendations")
                            
                            # Create columns for movie cards
                            cols = st.columns(2)
                            
                            for i, rec in enumerate(llm_recommendations):
                                col_idx = i % 2
                                with cols[col_idx]:
                                    # Get movie metadata
                                    movie_metadata = engine.get_movie_metadata(rec['movie_id'])
                                    if movie_metadata:
                                        # Display movie card with AI explanation
                                        display_movie_card_with_explanation(
                                            movie_metadata, rec['movie_id'], user_history, 
                                            engine, profile, i, rec['explanation']
                                        )
                            
                            # Add to current recommendations
                            new_movie_ids = [rec['movie_id'] for rec in llm_recommendations]
                            user_history['current_recommendations'].extend(new_movie_ids)
                            save_user_history(user_history)
                            
                        else:
                            st.warning("No recommendations found. Try a different search query.")
                            
                    except Exception as e:
                        st.error(f"Error processing search: {str(e)}")
                        st.info("Make sure you have set your COHERE_API_KEY environment variable.")
            else:
                st.warning("Please enter a search query.")
        
        # Don't show algorithm recommendations if AI search is selected
        st.stop()
    
    else:
        # Algorithm-based recommendations
        st.markdown("### 🧠 Algorithm-Based Recommendations")
        st.markdown("These recommendations are based on your personality profile and interaction history.")
    
    # Create columns for movie cards
    cols = st.columns(2)
    
    for i, (movie_id, score) in enumerate(recommendations):
        col_idx = i % 2
        with cols[col_idx]:
            # Get movie metadata
            movie_metadata = engine.get_movie_metadata(movie_id)
            if movie_metadata:
                display_movie_card(movie_metadata, movie_id, user_history, engine, profile, i)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Generate 10 More (Add Below)", type="secondary", key="generate_more_btn"):
            # Generate 10 more recommendations and add them to current ones
            new_recommendations = engine.get_personalized_recommendations(profile, user_history, 10, include_current=True)
            if new_recommendations:
                # Add new recommendations to current ones
                current_movie_ids = user_history.get('current_recommendations', [])
                new_movie_ids = [movie_id for movie_id, _ in new_recommendations]
                user_history['current_recommendations'] = current_movie_ids + new_movie_ids
                if save_user_history(user_history):
                    st.success("Added 10 more recommendations!")
                    st.rerun()
                else:
                    st.error("Failed to save recommendations. Please try again.")
            else:
                st.warning("No new recommendations found. Try refreshing all recommendations.")
    
    with col2:
        if st.button("🎲 Refresh All Recommendations", type="primary", key="refresh_all_btn"):
            # Generate completely new set of recommendations
            new_recommendations = engine.get_personalized_recommendations(profile, user_history, 10)
            if new_recommendations:
                user_history['current_recommendations'] = [movie_id for movie_id, _ in new_recommendations]
                if save_user_history(user_history):
                    st.success("Generated fresh recommendations!")
                    st.rerun()
                else:
                    st.error("Failed to save recommendations. Please try again.")
            else:
                st.warning("No recommendations found. Please try adjusting your preferences.")
    
    with col3:
        if st.button("🗑️ Clear All Recommendations", type="secondary", key="clear_all_btn"):
            user_history['current_recommendations'] = []
            if save_user_history(user_history):
                st.success("Cleared all recommendations!")
                st.rerun()
            else:
                st.error("Failed to clear recommendations. Please try again.")
    
    # Show user history
    if user_history['watched_movies']:
        st.subheader("📚 Your Movie History")
        st.write(f"You've watched {len(user_history['watched_movies'])} movies!")
        
        if st.button("📊 View Full History"):
            show_user_history(user_history, movies_df)

def display_movie_card(movie_metadata, movie_id, user_history, engine, profile, card_index):
    """Display a movie card with all the requested information"""
    # Create movie card HTML
    streaming_links_html = ""
    for link in movie_metadata['streaming_links']:
        streaming_links_html += f'<a href="{link["url"]}" target="_blank" class="streaming-link">{link["name"]}</a> '
    
    st.markdown(f"""
    <div class="movie-card">
        <div class="movie-title">{movie_metadata['title']}</div>
        <div class="movie-info">📅 Year: {movie_metadata['year']}</div>
        <div class="movie-info">⭐ IMDB Rating: {movie_metadata['imdb_rating']} ({movie_metadata['rating_count']} ratings)</div>
        <div class="movie-info">🎭 Genres: {', '.join(movie_metadata['genres'])}</div>
        <div class="movie-info">👥 Cast: {', '.join(movie_metadata['cast'])}</div>
        <div class="movie-info">📺 Available on: {streaming_links_html}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add interaction buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"✅ Watched", key=f"watched_{movie_id}_{card_index}"):
            if movie_id not in user_history['watched_movies']:
                user_history['watched_movies'].append(movie_id)
                # Remove from current recommendations and replace with new one
                if movie_id in user_history.get('current_recommendations', []):
                    user_history['current_recommendations'].remove(movie_id)
                    # Get a new recommendation to replace this one
                    new_recommendations = engine.get_personalized_recommendations(
                        profile, user_history, 1, exclude_movies=[movie_id]
                    )
                    if new_recommendations:
                        user_history['current_recommendations'].append(new_recommendations[0][0])
                save_user_history(user_history)
                st.success("Added to your watched list! Replaced with a new recommendation.")
                st.rerun()
    
    with col2:
        if st.button(f"❤️ Liked", key=f"liked_{movie_id}_{card_index}"):
            if movie_id not in user_history['liked_movies']:
                user_history['liked_movies'].append(movie_id)
                save_user_history(user_history)
                st.success("Added to your liked movies!")
                st.rerun()
    
    with col3:
        if st.button(f"👎 Disliked", key=f"disliked_{movie_id}_{card_index}"):
            if movie_id not in user_history['disliked_movies']:
                user_history['disliked_movies'].append(movie_id)
                # Remove from current recommendations and replace with new one
                if movie_id in user_history.get('current_recommendations', []):
                    user_history['current_recommendations'].remove(movie_id)
                    # Get a new recommendation to replace this one
                    new_recommendations = engine.get_personalized_recommendations(
                        profile, user_history, 1, exclude_movies=[movie_id]
                    )
                    if new_recommendations:
                        user_history['current_recommendations'].append(new_recommendations[0][0])
                save_user_history(user_history)
                st.success("Added to your disliked movies! Replaced with a new recommendation.")
                st.rerun()
    
    with col4:
        if st.button(f"🔄 Replace", key=f"replace_{movie_id}_{card_index}"):
            # Replace this movie with a new recommendation
            if movie_id in user_history.get('current_recommendations', []):
                user_history['current_recommendations'].remove(movie_id)
                # Get a new recommendation to replace this one
                new_recommendations = engine.get_personalized_recommendations(
                    profile, user_history, 1, exclude_movies=[movie_id]
                )
                if new_recommendations:
                    user_history['current_recommendations'].append(new_recommendations[0][0])
                    if save_user_history(user_history):
                        st.success("Replaced with a new recommendation!")
                        st.rerun()
                    else:
                        st.error("Failed to save replacement. Please try again.")
                else:
                    st.warning("No replacement found. Try refreshing all recommendations.")

def display_movie_card_with_explanation(movie_metadata, movie_id, user_history, engine, profile, card_index, explanation):
    """Display a movie card with AI explanation"""
    # Create movie card HTML
    streaming_links_html = ""
    for link in movie_metadata['streaming_links']:
        streaming_links_html += f'<a href="{link["url"]}" target="_blank" class="streaming-link">{link["name"]}</a> '
    
    cast_html = ", ".join(movie_metadata['cast'])
    genres_html = ", ".join(movie_metadata['genres'])
    
    st.markdown(f"""
    <div class="movie-card">
        <h3>{movie_metadata['title']}</h3>
        <p><strong>Year:</strong> {movie_metadata['year']}</p>
        <p><strong>IMDB Rating:</strong> {movie_metadata['imdb_rating']}/5.0 ({movie_metadata['rating_count']} ratings)</p>
        <p><strong>Genres:</strong> {genres_html}</p>
        <p><strong>Cast:</strong> {cast_html}</p>
        <p><strong>Available on:</strong> {streaming_links_html}</p>
        <div class="ai-explanation">
            <p><strong>🤖 AI Explanation:</strong> {explanation}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add interaction buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"✅ Watched", key=f"watched_{movie_id}_{card_index}_ai"):
            if movie_id not in user_history['watched_movies']:
                user_history['watched_movies'].append(movie_id)
                # Remove from current recommendations and replace with new one
                if movie_id in user_history.get('current_recommendations', []):
                    user_history['current_recommendations'].remove(movie_id)
                    # Get a new recommendation to replace this one
                    new_recommendations = engine.get_personalized_recommendations(
                        profile, user_history, 1, exclude_movies=[movie_id]
                    )
                    if new_recommendations:
                        user_history['current_recommendations'].append(new_recommendations[0][0])
                save_user_history(user_history)
                st.success("Added to your watched list! Replaced with a new recommendation.")
                st.rerun()
    
    with col2:
        if st.button(f"❤️ Liked", key=f"liked_{movie_id}_{card_index}_ai"):
            if movie_id not in user_history['liked_movies']:
                user_history['liked_movies'].append(movie_id)
                save_user_history(user_history)
                st.success("Added to your liked movies!")
                st.rerun()
    
    with col3:
        if st.button(f"👎 Disliked", key=f"disliked_{movie_id}_{card_index}_ai"):
            if movie_id not in user_history['disliked_movies']:
                user_history['disliked_movies'].append(movie_id)
                # Remove from current recommendations and replace with new one
                if movie_id in user_history.get('current_recommendations', []):
                    user_history['current_recommendations'].remove(movie_id)
                    # Get a new recommendation to replace this one
                    new_recommendations = engine.get_personalized_recommendations(
                        profile, user_history, 1, exclude_movies=[movie_id]
                    )
                    if new_recommendations:
                        user_history['current_recommendations'].append(new_recommendations[0][0])
                save_user_history(user_history)
                st.success("Added to your disliked movies! Replaced with a new recommendation.")
                st.rerun()
    
    with col4:
        if st.button(f"🔄 Replace", key=f"replace_{movie_id}_{card_index}_ai"):
            # Replace this movie with a new recommendation
            if movie_id in user_history.get('current_recommendations', []):
                user_history['current_recommendations'].remove(movie_id)
                # Get a new recommendation to replace this one
                new_recommendations = engine.get_personalized_recommendations(
                    profile, user_history, 1, exclude_movies=[movie_id]
                )
                if new_recommendations:
                    user_history['current_recommendations'].append(new_recommendations[0][0])
                    if save_user_history(user_history):
                        st.success("Replaced with a new recommendation!")
                        st.rerun()
                    else:
                        st.error("Failed to save replacement. Please try again.")
                else:
                    st.warning("No replacement found. Try refreshing all recommendations.")

def show_user_history(user_history, movies_df):
    """Display user's movie history with editing capabilities"""
    st.subheader("📚 Your Complete Movie History")
    
    # Create tabs for different categories
    tab1, tab2, tab3 = st.tabs(["✅ Watched Movies", "❤️ Liked Movies", "👎 Disliked Movies"])
    
    with tab1:
        st.write("**Movies You've Watched:**")
        if user_history['watched_movies']:
            for i, movie_id in enumerate(user_history['watched_movies']):
                movie_info = movies_df[movies_df['movieId'] == movie_id]
                if not movie_info.empty:
                    movie = movie_info.iloc[0]
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"• {movie['title']} ({movie['year']})")
                    with col2:
                        if st.button("🗑️", key=f"remove_watched_{movie_id}", help="Remove from watched list"):
                            user_history['watched_movies'].remove(movie_id)
                            save_user_history(user_history)
                            st.success("Removed from watched list!")
                            st.rerun()
        else:
            st.info("No watched movies yet.")
    
    with tab2:
        st.write("**Movies You Liked:**")
        if user_history['liked_movies']:
            for i, movie_id in enumerate(user_history['liked_movies']):
                movie_info = movies_df[movies_df['movieId'] == movie_id]
                if not movie_info.empty:
                    movie = movie_info.iloc[0]
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"• {movie['title']} ({movie['year']})")
                    with col2:
                        if st.button("🗑️", key=f"remove_liked_{movie_id}", help="Remove from liked list"):
                            user_history['liked_movies'].remove(movie_id)
                            save_user_history(user_history)
                            st.success("Removed from liked list!")
                            st.rerun()
        else:
            st.info("No liked movies yet.")
    
    with tab3:
        st.write("**Movies You Disliked:**")
        if user_history['disliked_movies']:
            for i, movie_id in enumerate(user_history['disliked_movies']):
                movie_info = movies_df[movies_df['movieId'] == movie_id]
                if not movie_info.empty:
                    movie = movie_info.iloc[0]
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"• {movie['title']} ({movie['year']})")
                    with col2:
                        if st.button("🗑️", key=f"remove_disliked_{movie_id}", help="Remove from disliked list"):
                            user_history['disliked_movies'].remove(movie_id)
                            save_user_history(user_history)
                            st.success("Removed from disliked list!")
                            st.rerun()
        else:
            st.info("No disliked movies yet.")
    
    # Clear all buttons
    st.markdown("---")
    st.subheader("🗑️ Clear History")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear All Watched", type="secondary"):
            user_history['watched_movies'] = []
            save_user_history(user_history)
            st.success("Cleared all watched movies!")
            st.rerun()
    
    with col2:
        if st.button("Clear All Liked", type="secondary"):
            user_history['liked_movies'] = []
            save_user_history(user_history)
            st.success("Cleared all liked movies!")
            st.rerun()
    
    with col3:
        if st.button("Clear All Disliked", type="secondary"):
            user_history['disliked_movies'] = []
            save_user_history(user_history)
            st.success("Cleared all disliked movies!")
            st.rerun()

def main():
    """Main application function"""
    # Load data
    movies_df, ratings_df = load_data()
    
    if movies_df is None or ratings_df is None:
        st.error("❌ Could not load data. Please check if setup.py was run successfully.")
        return
    
    # Load user profile
    profile = load_user_profile()
    
    # Sidebar navigation
    st.sidebar.title("🎬 Navigation")
    
    if not profile:
        st.sidebar.info("👋 Welcome! Please complete the questionnaire to get started.")
        show_questionnaire()
    else:
        st.sidebar.success("✅ Profile loaded!")
        
        # Navigation options
        page = st.sidebar.selectbox(
            "Choose a page:",
            ["🎯 Get Recommendations", "📝 Update Profile", "📚 View History"]
        )
        
        if page == "🎯 Get Recommendations":
            show_recommendations_page(profile, movies_df, ratings_df)
        elif page == "📝 Update Profile":
            st.info("To update your profile, please complete the questionnaire again.")
            if st.button("🔄 Retake Questionnaire"):
                # Clear profile
                os.remove("user_profile.json")
                st.rerun()
        elif page == "📚 View History":
            user_history = load_user_history()
            show_user_history(user_history, movies_df)

if __name__ == "__main__":
    main()
