"""
Personalized Movie Recommendation Engine

This module contains the core recommendation logic that combines:
- Content-based filtering (genre preferences)
- Collaborative filtering (user ratings)
- Personality and mood-based filtering
- User history integration
"""

import pandas as pd
import numpy as np
import random
from typing import List, Tuple, Dict, Any


class PersonalizedRecommendationEngine:
    """Personalized recommendation engine based on questionnaire and user history"""
    
    def __init__(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame):
        """Initialize the recommendation engine"""
        self.movies_df = movies_df
        self.ratings_df = ratings_df
        
        # Create user-movie matrix for collaborative filtering
        self.user_movie_matrix = ratings_df.pivot(
            index='userId', 
            columns='movieId', 
            values='rating'
        ).fillna(0)
        
        # Calculate movie popularity scores
        self.movie_popularity = ratings_df.groupby('movieId')['rating'].agg(['mean', 'count'])
        self.movie_popularity.columns = ['avg_rating', 'rating_count']
    
    def get_personalized_recommendations(self, profile: Dict[str, Any], user_history: Dict[str, List], 
                                       n_recommendations: int = 10, exclude_movies: List[int] = None, 
                                       include_current: bool = False) -> List[Tuple[int, float]]:
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
        
        if len(candidate_movies) == 0:
            return []
        
        # Score movies based on multiple factors
        scored_movies = []
        for _, movie in candidate_movies.iterrows():
            score = self._calculate_movie_score(movie, profile, user_history)
            scored_movies.append((movie['movieId'], score))
        
        # Sort by score and return top recommendations
        scored_movies.sort(key=lambda x: x[1], reverse=True)
        
        # Add some randomness to avoid always getting the same recommendations
        if len(scored_movies) > n_recommendations:
            # Take top 50% and shuffle them, then take top n_recommendations
            top_candidates = scored_movies[:min(50, len(scored_movies))]
            random.shuffle(top_candidates)
            return top_candidates[:n_recommendations]
        
        return scored_movies[:n_recommendations]
    
    def _apply_mood_filter(self, movies_df: pd.DataFrame, mood: str) -> pd.DataFrame:
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
    
    def _apply_personality_filter(self, movies_df: pd.DataFrame, personality: str) -> pd.DataFrame:
        """Apply personality-based filtering to movies"""
        personality_genre_mapping = {
            'balanced': [],  # No filtering for balanced personality
            'creative': ['Drama', 'Musical', 'Animation', 'Fantasy'],
            'analytical': ['Documentary', 'Mystery', 'Thriller', 'Sci-Fi'],
            'social': ['Comedy', 'Romance', 'Musical', 'Family'],
            'introverted': ['Drama', 'Documentary', 'Mystery', 'Romance']
        }
        
        if personality in personality_genre_mapping and personality_genre_mapping[personality]:
            preferred_genres = personality_genre_mapping[personality]
            genre_mask = movies_df['genres'].apply(
                lambda x: any(genre in (eval(x) if isinstance(x, str) else x) for genre in preferred_genres)
            )
            return movies_df[genre_mask]
        
        return movies_df
    
    def _calculate_movie_score(self, movie: pd.Series, profile: Dict[str, Any], 
                             user_history: Dict[str, List]) -> float:
        """Calculate a score for a movie based on multiple factors"""
        score = 0.0
        movie_id = movie['movieId']
        
        # Genre preference score (40% weight)
        preferred_genres = profile.get('preferred_genres', [])
        if preferred_genres:
            movie_genres = eval(movie['genres']) if isinstance(movie['genres'], str) else movie['genres']
            genre_matches = sum(1 for genre in movie_genres if genre in preferred_genres)
            if genre_matches > 0:
                score += 0.4 * (genre_matches / len(preferred_genres))
        
        # Popularity score (20% weight)
        if movie_id in self.movie_popularity.index:
            popularity = self.movie_popularity.loc[movie_id]
            # Normalize rating (0-5 scale) and rating count
            rating_score = popularity['avg_rating'] / 5.0
            count_score = min(popularity['rating_count'] / 100.0, 1.0)  # Cap at 100 ratings
            score += 0.2 * (rating_score * 0.7 + count_score * 0.3)
        
        # Liked movies bonus (20% weight)
        liked_movies = user_history.get('liked_movies', [])
        if movie_id in liked_movies:
            score += 0.2
        
        # Year preference (10% weight) - prefer movies from 1990-2020
        year = movie.get('year', 2000)
        if 1990 <= year <= 2020:
            score += 0.1
        
        # Random factor (10% weight) for diversity
        score += 0.1 * random.random()
        
        return score
    
    def get_movie_metadata(self, movie_id: int) -> Dict[str, Any]:
        """Get enhanced metadata for a movie including cast and streaming links"""
        movie = self.movies_df[self.movies_df['movieId'] == movie_id]
        if movie.empty:
            return None
        
        movie = movie.iloc[0]
        
        # Generate consistent mock data based on movie ID
        cast = self._generate_mock_cast(movie['title'], movie_id)
        streaming_links = self._generate_streaming_links(movie['title'], movie_id)
        
        return {
            'title': movie['title'],
            'year': movie['year'],
            'genres': eval(movie['genres']) if isinstance(movie['genres'], str) else movie['genres'],
            'imdb_rating': round(random.uniform(2.0, 5.0), 1),
            'rating_count': random.randint(1, 1000),
            'cast': cast,
            'streaming_links': streaming_links
        }
    
    def _generate_mock_cast(self, title: str, movie_id: int) -> List[str]:
        """Generate consistent mock cast based on movie ID"""
        # Use movie ID as seed for consistency
        random.seed(movie_id)
        
        actors = [
            "Tom Hanks", "Meryl Streep", "Leonardo DiCaprio", "Scarlett Johansson",
            "Brad Pitt", "Jennifer Lawrence", "Ryan Gosling", "Emma Stone",
            "Chris Evans", "Robert Downey Jr.", "Chris Hemsworth", "Mark Ruffalo",
            "Scarlett Johansson", "Jeremy Renner", "Don Cheadle", "Paul Rudd",
            "Benedict Cumberbatch", "Chadwick Boseman", "Brie Larson", "Tom Holland"
        ]
        
        # Select 3 random actors
        cast = random.sample(actors, 3)
        
        # Reset random seed
        random.seed()
        
        return cast
    
    def _generate_streaming_links(self, title: str, movie_id: int) -> List[Dict[str, str]]:
        """Generate consistent mock streaming links based on movie ID"""
        # Use movie ID as seed for consistency
        random.seed(movie_id)
        
        platforms = [
            {"name": "Netflix", "url": "https://netflix.com"},
            {"name": "Amazon Prime", "url": "https://primevideo.com"},
            {"name": "Disney+", "url": "https://disneyplus.com"},
            {"name": "Hulu", "url": "https://hulu.com"},
            {"name": "HBO Max", "url": "https://hbomax.com"},
            {"name": "Apple TV+", "url": "https://tv.apple.com"}
        ]
        
        # Select 1-3 random platforms
        num_platforms = random.randint(1, 3)
        selected_platforms = random.sample(platforms, num_platforms)
        
        # Reset random seed
        random.seed()
        
        return selected_platforms