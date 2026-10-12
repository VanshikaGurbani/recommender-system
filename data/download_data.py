#!/usr/bin/env python3
"""
Download and preprocess MovieLens 100K dataset
"""

import os
import pandas as pd
import requests
import zipfile
from pathlib import Path

def download_movielens_100k():
    """Download MovieLens 100K dataset"""
    url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    zip_path = data_dir / "ml-latest-small.zip"
    
    if not zip_path.exists():
        print("Downloading MovieLens 100K dataset...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download completed!")
    else:
        print("Dataset already exists!")
    
    # Extract the zip file
    if not (data_dir / "ml-latest-small").exists():
        print("Extracting dataset...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        print("Extraction completed!")
    
    return data_dir / "ml-latest-small"

def load_and_preprocess_data(data_path):
    """Load and preprocess the data"""
    movies_path = data_path / "movies.csv"
    ratings_path = data_path / "ratings.csv"
    
    # Load data
    movies_df = pd.read_csv(movies_path)
    ratings_df = pd.read_csv(ratings_path)
    
    # Clean and preprocess movies data
    movies_df['genres'] = movies_df['genres'].str.split('|')
    movies_df['year'] = movies_df['title'].str.extract(r'\((\d{4})\)')
    movies_df['clean_title'] = movies_df['title'].str.replace(r'\(\d{4}\)', '').str.strip()
    
    # Create a combined text representation for embeddings
    movies_df['text_for_embedding'] = movies_df.apply(
        lambda x: f"{x['clean_title']} {' '.join(x['genres'])} {x['year'] if pd.notna(x['year']) else ''}", 
        axis=1
    )
    
    # Filter ratings to keep only movies that exist
    ratings_df = ratings_df[ratings_df['movieId'].isin(movies_df['movieId'])]
    
    # Create user-movie matrix
    user_movie_matrix = ratings_df.pivot(
        index='userId', 
        columns='movieId', 
        values='rating'
    ).fillna(0)
    
    return movies_df, ratings_df, user_movie_matrix

def save_processed_data(movies_df, ratings_df, user_movie_matrix):
    """Save processed data to CSV files"""
    data_dir = Path("data")
    
    movies_df.to_csv(data_dir / "processed_movies.csv", index=False)
    ratings_df.to_csv(data_dir / "processed_ratings.csv", index=False)
    user_movie_matrix.to_csv(data_dir / "user_movie_matrix.csv")
    
    print(f"Processed data saved to {data_dir}/")
    print(f"Movies: {len(movies_df)}")
    print(f"Users: {len(ratings_df['userId'].unique())}")
    print(f"Ratings: {len(ratings_df)}")

if __name__ == "__main__":
    # Download dataset
    data_path = download_movielens_100k()
    
    # Load and preprocess
    movies_df, ratings_df, user_movie_matrix = load_and_preprocess_data(data_path)
    
    # Save processed data
    save_processed_data(movies_df, ratings_df, user_movie_matrix)
