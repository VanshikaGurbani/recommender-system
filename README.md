# 🎬 Personalized Movie Recommender System

A sophisticated, single-user movie recommendation application that learns from your personality, mood, and viewing history to provide personalized movie suggestions.

## ✨ Features

### 🧠 **Intelligent Personalization**
- **6-Question Personality Assessment**: Determines your personality type and preferences
- **Mood-Based Filtering**: Recommendations adapt to your current mood
- **Learning from History**: System improves recommendations based on your interactions

### 🎯 **Smart Recommendations**
- **Multi-Factor Scoring**: Combines genre preferences, mood, personality, and history
- **Diverse Results**: Adds randomness to prevent repetitive recommendations
- **Real-time Updates**: Recommendations change as you interact with movies
- **🤖 LLM-Powered Search**: Natural language queries using Cohere AI
- **AI Explanations**: Get personalized explanations for why movies were recommended

### 🎨 **Modern Interface**
- **Dark Theme**: Sleek, modern design with matte finish
- **Interactive Movie Cards**: Rich movie information with action buttons
- **Responsive Layout**: Works perfectly on desktop and mobile

### 📊 **Rich Movie Information**
- **Complete Details**: Title, year, IMDB rating, genres, cast
- **Streaming Links**: Direct links to where movies are available
- **Consistent Data**: Same movie always shows same information

## 🏗️ Architecture

### **Core Components**

#### **1. Data Layer**
```
📁 data/
├── ml-latest-small/          # MovieLens 100K dataset
│   ├── movies.csv           # Movie metadata
│   ├── ratings.csv          # User ratings
│   └── links.csv            # External links
├── processed_movies.csv     # Processed movie data
├── processed_ratings.csv    # Processed ratings data
└── user_movie_matrix.csv    # User-movie interaction matrix
```

#### **2. User Persistence**
```
📄 user_profile.json         # User personality profile
📄 user_history.json         # Interaction history
```

#### **3. Recommendation Engine**
- **PersonalizedRecommendationEngine**: Core recommendation logic
- **Multi-factor Scoring Algorithm**: 
  ```
  Score = Genre_Match + Mood_Filter + Personality_Filter + History_Bonus + Randomness
  ```

#### **4. User Interface**
- **Streamlit Application**: Modern web interface
- **Questionnaire System**: 6 questions for personality assessment
- **Interactive Components**: Movie cards with action buttons

### **Recommendation Algorithm**

1. **Profile Analysis**: Analyzes user personality and mood
2. **Genre Matching**: Matches preferred genres from questionnaire
3. **Mood Filtering**: Applies mood-based genre preferences
4. **Personality Filtering**: Adjusts recommendations based on personality type
5. **History Integration**: Excludes watched/disliked movies, includes liked preferences
6. **Scoring & Ranking**: Calculates composite scores and ranks movies
7. **Randomization**: Adds variety by shuffling top candidates

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- pip package manager

### **Installation**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd recommender-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download and process data**
   ```bash
   python data/download_data.py
   ```

4. **Setup Cohere API key (for LLM features)**
   ```bash
   python setup_cohere.py
   ```
   Get your free API key at: https://dashboard.cohere.ai/

5. **Run the application**
   ```bash
   streamlit run app_personalized.py
   ```

6. **Open your browser**
   - Navigate to `http://localhost:8501`
   - Complete the personality questionnaire
   - Start getting personalized recommendations!

## 📋 Requirements

```
streamlit==1.28.1
pandas==2.1.3
numpy==1.24.3
scikit-learn==1.3.2
requests==2.31.0
pillow==10.1.0
matplotlib==3.8.2
seaborn==0.13.0
```

## 🎮 How to Use

### **1. First Time Setup**
- Complete the 6-question personality questionnaire
- Your profile will be saved automatically

### **2. Getting Recommendations**
- Click "Get Recommendations" to see your personalized movie suggestions
- Each movie card shows: title, year, IMDB rating, cast, and streaming links

### **3. Interacting with Movies**
- **✅ Watched**: Mark as watched (replaces with new recommendation)
- **❤️ Liked**: Add to liked list (no replacement)
- **👎 Disliked**: Mark as disliked (replaces with new recommendation)
- **🔄 Replace**: Manually replace with a new recommendation

### **4. Managing Recommendations**
- **Generate 10 More**: Add 10 new recommendations below existing ones
- **Refresh All**: Generate completely new set of recommendations
- **Clear All**: Clear all current recommendations

### **5. 🤖 LLM-Powered Search**
- **Natural Language Queries**: Ask for movies in plain English
- **AI Explanations**: Get personalized explanations for recommendations
- **Smart Understanding**: AI understands complex requests and preferences
- **Example Queries**:
  - "movies like inception"
  - "I want a romantic comedy from the 90s"
  - "thriller movies with strong female leads"
  - "feel-good movies for a rainy day"

### **6. Viewing History**
- Click "View Full History" to see your complete movie history
- Edit history by removing individual movies or clearing categories

## 🔧 Technical Details

### **Data Processing**
- **MovieLens 100K Dataset**: ~1000 movies, ~1000 users, ~100K ratings
- **CSV-based Storage**: No database required, uses processed CSV files
- **Offline Operation**: No external API calls, fully self-contained

### **Recommendation Features**
- **Genre Preferences**: Learned from questionnaire responses
- **Mood States**: Happy, Sad, Excited, Relaxed, Adventurous, Romantic, Mysterious, Neutral
- **Personality Types**: Balanced, Creative, Analytical, Social, Introverted
- **Smart Filtering**: Excludes watched, disliked, and current recommendations

### **User Experience**
- **Persistent State**: All interactions saved immediately
- **Consistent Data**: Same movie ID always generates same metadata
- **Unique Widget Keys**: Prevents Streamlit conflicts
- **Responsive Design**: Works on all screen sizes

## 📁 Project Structure

```
recommender-system/
├── app_personalized.py      # Main Streamlit application
├── data/                    # Data files and processing
│   ├── download_data.py    # Data download and processing script
│   ├── ml-latest-small/    # MovieLens dataset
│   ├── processed_movies.csv
│   ├── processed_ratings.csv
│   └── user_movie_matrix.csv
├── user_profile.json       # User personality profile
├── user_history.json       # User interaction history
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎯 Key Features Explained

### **Personality Assessment**
The system uses 6 carefully crafted questions to determine:
- **Preferred Genres**: Comedy, Drama, Action, Romance, etc.
- **Personality Type**: Balanced, Creative, Analytical, Social, Introverted
- **Mood Preferences**: How mood affects movie choices

### **Smart Recommendation Engine**
- **Multi-factor Scoring**: Combines multiple signals for better recommendations
- **Learning from Feedback**: Improves over time based on user interactions
- **Diversity Injection**: Adds randomness to prevent repetitive results

### **Rich Movie Information**
- **Mock Data Generation**: Creates realistic cast and streaming information
- **Consistent Results**: Same movie always shows same information
- **External Links**: Direct links to streaming platforms

## 🔮 Future Enhancements

- **Real Movie Data**: Integration with TMDB or similar APIs
- **Advanced ML**: Deep learning models for better recommendations
- **Social Features**: Share recommendations with friends
- **Mobile App**: Native mobile application
- **Multi-user Support**: Support for multiple user profiles

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **MovieLens Dataset**: For providing the movie and rating data
- **Streamlit**: For the excellent web framework
- **Python Community**: For the amazing libraries and tools

---

Sample:
https://drive.google.com/file/d/18ScMtqONaVsFogcZ7t-fz0g1746Bg-yY/view?usp=sharing

**Built with ❤️ for movie lovers everywhere!**
