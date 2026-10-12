"""
LLM-Powered Recommendation Engine using Cohere

This module provides natural language query processing and LLM-powered recommendations
using Cohere's Command and Embed models.
"""

import cohere
import pandas as pd
import numpy as np
import json
import os
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity


class CohereLLMEngine:
    """LLM-powered recommendation engine using Cohere models"""
    
    def __init__(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame):
        """
        Initialize the Cohere LLM engine
        
        Args:
            movies_df: DataFrame containing movie information
            ratings_df: DataFrame containing user ratings
        """
        self.movies_df = movies_df
        self.ratings_df = ratings_df
        
        # Initialize Cohere client
        api_key = os.getenv('COHERE_API_KEY')
        if not api_key:
            # For demo purposes, you can set a default key here
            api_key = "your_cohere_api_key_here"
        
        self.co = cohere.Client(api_key)
        
        # Create movie embeddings cache
        self.movie_embeddings = None
        self.movie_embeddings_df = None
        
    def process_natural_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process natural language query and extract structured preferences
        
        Args:
            user_query: Natural language query like "movies like inception"
            
        Returns:
            Dictionary with extracted preferences
        """
        prompt = f"""
        Analyze this movie recommendation query and extract structured information:
        
        Query: "{user_query}"
        
        Extract the following information and return as JSON:
        {{
            "query_type": "similar_to" | "actor_based" | "genre_preference" | "mood_based" | "time_period" | "general",
            "reference_movie": "movie title if mentioned",
            "actor_name": "actor name if mentioned (e.g., Brad Pitt, Tom Hanks)",
            "preferred_genres": ["genre1", "genre2"],
            "mood": "happy" | "sad" | "excited" | "relaxed" | "adventurous" | "romantic" | "mysterious" | "neutral",
            "time_period": "1990s" | "2000s" | "2010s" | "recent" | "classic" | "any",
            "additional_requirements": ["requirement1", "requirement2"],
            "explanation": "brief explanation of what the user wants"
        }}
        
        Special cases:
        - If query mentions an actor (e.g., "Brad Pitt movies"), set query_type to "actor_based" and actor_name to the actor
        - If query is "movies like X", set query_type to "similar_to" and reference_movie to X
        - Only include fields that are relevant to the query. Use "any" or empty arrays for unspecified preferences.
        """
        
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            # Parse JSON response
            result_text = response.generations[0].text.strip()
            # Clean up the response to extract JSON
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            return json.loads(result_text)
            
        except Exception as e:
            print(f"Error processing query: {e}")
            # Fallback to basic parsing
            return self._fallback_query_parsing(user_query)
    
    def _fallback_query_parsing(self, user_query: str) -> Dict[str, Any]:
        """Fallback query parsing if LLM fails"""
        query_lower = user_query.lower()
        
        result = {
            "query_type": "general",
            "reference_movie": None,
            "actor_name": None,
            "preferred_genres": [],
            "mood": "neutral",
            "time_period": "any",
            "additional_requirements": [],
            "explanation": "Basic query processing"
        }
        
        # Simple keyword matching
        if "like" in query_lower:
            result["query_type"] = "similar_to"
        
        # Actor detection
        actors = ["brad pitt", "tom hanks", "leonardo dicaprio", "scarlett johansson", 
                 "jennifer lawrence", "ryan gosling", "emma stone", "chris evans",
                 "robert downey jr", "chris hemsworth", "mark ruffalo", "meryl streep"]
        for actor in actors:
            if actor in query_lower:
                result["query_type"] = "actor_based"
                result["actor_name"] = actor.title()
                break
        
        # Genre detection
        genres = ["comedy", "drama", "action", "romance", "horror", "thriller", "sci-fi", "fantasy"]
        for genre in genres:
            if genre in query_lower:
                result["preferred_genres"].append(genre.title())
        
        # Time period detection
        if "90" in query_lower or "nineties" in query_lower:
            result["time_period"] = "1990s"
        elif "2000" in query_lower:
            result["time_period"] = "2000s"
        elif "2010" in query_lower:
            result["time_period"] = "2010s"
        
        return result
    
    def get_movie_embeddings(self) -> pd.DataFrame:
        """Generate embeddings for all movies using Cohere Embed model"""
        if self.movie_embeddings is not None:
            return self.movie_embeddings_df
        
        print("Generating movie embeddings...")
        
        # Create movie descriptions for embedding
        movie_descriptions = []
        for _, movie in self.movies_df.iterrows():
            # Create a rich description for each movie including cast
            genres = eval(movie['genres']) if isinstance(movie['genres'], str) else movie['genres']
            
            # Generate cast for this movie (consistent with existing system)
            cast = self._generate_mock_cast(movie['title'], movie['movieId'])
            
            # Create comprehensive description including cast
            description = f"{movie['title']} ({movie['year']}) - {', '.join(genres)} - Starring: {', '.join(cast)}"
            movie_descriptions.append(description)
        
        # Generate embeddings in batches
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(movie_descriptions), batch_size):
            batch = movie_descriptions[i:i+batch_size]
            try:
                response = self.co.embed(
                    texts=batch,
                    model='embed-english-v3.0',
                    input_type='search_document'
                )
                all_embeddings.extend(response.embeddings)
            except Exception as e:
                print(f"Error generating embeddings for batch {i}: {e}")
                # Use random embeddings as fallback
                all_embeddings.extend([np.random.rand(1024).tolist() for _ in batch])
        
        # Create embeddings DataFrame
        self.movie_embeddings_df = self.movies_df.copy()
        self.movie_embeddings_df['embedding'] = all_embeddings
        self.movie_embeddings = np.array(all_embeddings)
        
        return self.movie_embeddings_df
    
    def find_similar_movies(self, query: str, top_k: int = 20) -> List[Tuple[int, float]]:
        """
        Find movies similar to the query using embeddings
        
        Args:
            query: Natural language query
            top_k: Number of similar movies to return
            
        Returns:
            List of (movie_id, similarity_score) tuples
        """
        try:
            # Get query embedding
            query_response = self.co.embed(
                texts=[query],
                model='embed-english-v3.0',
                input_type='search_query'
            )
            query_embedding = np.array(query_response.embeddings[0]).reshape(1, -1)
            
            # Get movie embeddings
            movie_embeddings_df = self.get_movie_embeddings()
            movie_embeddings = np.array(movie_embeddings_df['embedding'].tolist())
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, movie_embeddings)[0]
            
            # Get top similar movies
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                movie_id = movie_embeddings_df.iloc[idx]['movieId']
                score = similarities[idx]
                results.append((movie_id, score))
            
            return results
            
        except Exception as e:
            print(f"Error finding similar movies: {e}")
            # Fallback to random selection
            random_movies = self.movies_df.sample(n=min(top_k, len(self.movies_df)))
            return [(row['movieId'], 0.5) for _, row in random_movies.iterrows()]
    
    def get_llm_recommendations(self, user_query: str, user_history: Dict[str, List], 
                              n_recommendations: int = 10) -> List[Dict[str, Any]]:
        """
        Get LLM-powered recommendations based on natural language query
        
        Args:
            user_query: Natural language query
            user_history: User's movie interaction history
            n_recommendations: Number of recommendations to return
            
        Returns:
            List of recommendation dictionaries with explanations
        """
        # Process the query
        query_info = self.process_natural_query(user_query)
        
        # Find similar movies using embeddings
        similar_movies = self.find_similar_movies(user_query, top_k=30)
        
        # Filter out watched and disliked movies
        watched_movies = set(user_history.get('watched_movies', []))
        disliked_movies = set(user_history.get('disliked_movies', []))
        
        filtered_movies = [
            (movie_id, score) for movie_id, score in similar_movies
            if movie_id not in watched_movies and movie_id not in disliked_movies
        ]
        
        # Get top recommendations
        top_movies = filtered_movies[:n_recommendations]
        
        # Generate explanations using LLM
        recommendations = []
        for movie_id, score in top_movies:
            movie_info = self.movies_df[self.movies_df['movieId'] == movie_id].iloc[0]
            
            # Generate explanation
            explanation = self._generate_recommendation_explanation(
                movie_info, query_info, user_query, score
            )
            
            recommendations.append({
                'movie_id': movie_id,
                'score': score,
                'explanation': explanation,
                'movie_info': movie_info
            })
        
        return recommendations
    
    def _generate_recommendation_explanation(self, movie_info: pd.Series, 
                                           query_info: Dict[str, Any], 
                                           original_query: str, 
                                           similarity_score: float) -> str:
        """Generate explanation for why a movie was recommended"""
        
        movie_title = movie_info['title']
        movie_year = movie_info['year']
        genres = eval(movie_info['genres']) if isinstance(movie_info['genres'], str) else movie_info['genres']
        
        prompt = f"""
        Explain why "{movie_title} ({movie_year})" was recommended based on this query:
        
        User Query: "{original_query}"
        Query Analysis: {json.dumps(query_info, indent=2)}
        Movie Genres: {', '.join(genres)}
        Similarity Score: {similarity_score:.2f}
        
        Provide a brief, engaging explanation (1-2 sentences) of why this movie matches the user's request.
        Be specific about the connection between the query and the movie.
        """
        
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=100,
                temperature=0.7
            )
            
            return response.generations[0].text.strip()
            
        except Exception as e:
            print(f"Error generating explanation: {e}")
            # Fallback explanation
            return f"Recommended because it matches your request for {query_info.get('explanation', 'movies')}."
    
    def explain_recommendation(self, movie_id: int, user_profile: Dict[str, Any], 
                             reason: str) -> str:
        """Generate detailed explanation for a recommendation"""
        
        movie_info = self.movies_df[self.movies_df['movieId'] == movie_id].iloc[0]
        
        prompt = f"""
        Explain why "{movie_info['title']}" was recommended to this user:
        
        User Profile: {json.dumps(user_profile, indent=2)}
        Reason: {reason}
        Movie: {movie_info['title']} ({movie_info['year']})
        Genres: {movie_info['genres']}
        
        Provide a personalized, engaging explanation (2-3 sentences) of why this movie 
        is a good match for this user's preferences and personality.
        """
        
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.generations[0].text.strip()
            
        except Exception as e:
            print(f"Error generating detailed explanation: {e}")
            return f"Recommended based on your preferences and the movie's characteristics."
    
    def _generate_mock_cast(self, title: str, movie_id: int) -> List[str]:
        """Generate consistent mock cast based on movie ID (same as recommendation engine)"""
        import random
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
