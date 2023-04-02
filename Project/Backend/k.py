from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
import json
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import joblib
app = Flask(__name__)
api = Api(app)
cors = CORS(app)

# Initialize the NLTK sentiment analyzer
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

# This endpoint retrieves and analyzes data about a user's posts on Twitter
class AnalyzeUserData(Resource):
    def get(self):
        # Get access token from authorization header
        access_token = "AAAAAAAAAAAAAAAAAAAAAK%2B3NgEAAAAA%2BanA%2FoqLWn%2FdtDuIzX48%2FH%2FMHZg%3Dn5MGElfAsd0ySRhd5ukJrxxLWR4yADb9QILvc3KXHrqU6r4a5C"
        if access_token is None:
            return {'error': 'Access token missing from header'}, 400

        # Set up headers for API requests
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'v2UserLookupPython'
        }

        # Set up endpoint URLs
        tweet_url = 'https://api.twitter.com/2/users/{user_id}/tweets'
        user_url = 'https://api.twitter.com/2/users/by/username/{username}'

        # Get the user's ID from their username
        # username = request.json.get('username')
        # if username is None:
        #     return {'error': 'Username missing from request body'}, 400
        # user_response = requests.get(user_url.format(username=username), headers=headers)
        # if user_response.status_code != 200:
        #     return {'error': 'Error getting user ID'}, 400
        user_id = "1521385989167493120"

        # Get the user's tweets
        tweet_params = {
            'max_results': 100,
            'tweet.fields': 'public_metrics'
        }
        tweet_response = requests.get(tweet_url.format(user_id=user_id), headers=headers, params=tweet_params)
        if tweet_response.status_code != 200:
            print(tweet_response)
            return {'error': 'Error getting user tweets'}, 400
        tweets = tweet_response.json()['data']

        # Parse the tweets and extract relevant data
        tweet_data = []
        for tweet in tweets:
            # Analyze the tweet's sentiment using NLTK
            tweet_sentiment = sid.polarity_scores(tweet['text'])

            # Get the tweet's likes and retweets
            likes = tweet['public_metrics']['like_count']
            retweets = tweet['public_metrics']['retweet_count']
            
            # Use a linear regression model to predict how much the tweet's engagement will increase in the future based on sentiment score
            sentiment_score = tweet_sentiment['compound']
            
            predicted_likes = 0
            predicted_retweets = 0
            if tweet_sentiment['compound'] > 0:
                predicted_likes = int(likes * 1.1)
                predicted_retweets = int(retweets * 1.2)
            else:
                predicted_likes = likes
                predicted_retweets = retweets

            # Add relevant data to the response
            tweet_data.append({
                'text': tweet['text'],
                'sentiment': tweet_sentiment,
                'likes': likes,
                'retweets': retweets,
                'predicted_likes': predicted_likes,
                'predicted_retweets': predicted_retweets
            })

        # Add the predicted engagement counts to the response
        response_data = {
           'tweets': tweet_data,
        }

        return make_response(jsonify(response_data), 200)
    
class AnalyseUser(Resource):
    def get(self):
        username = 'henit_chobisa'
        bearer_token = "AAAAAAAAAAAAAAAAAAAAAK%2B3NgEAAAAA%2BanA%2FoqLWn%2FdtDuIzX48%2FH%2FMHZg%3Dn5MGElfAsd0ySRhd5ukJrxxLWR4yADb9QILvc3KXHrqU6r4a5C"
        
        headers = {"Authorization": f"Bearer {bearer_token}"}
        tweet_params = {
            'user.fields': 'profile_image_url,public_metrics'
        }
        response = requests.get("https://api.twitter.com/2/users/1521385989167493120", headers=headers, params=tweet_params)
        if response.status_code != 200:
            raise Exception(f"Failed to get user's follower count: {response.status_code}")
        user_data = json.loads(response.content)
        
        followers_count = user_data["data"]["public_metrics"]["followers_count"]
        following_count = user_data["data"]["public_metrics"]["following_count"]

        # Get the current date and time and calculate the end of the month
        now = datetime.now()
        days_in_month = 30 - now.day
        end_of_month = now + timedelta(days=days_in_month)

        # Predict the expected number of followers by the end of the month using the machine learning model
        predicted_followers = int(model.predict([[followers_count]])[0])

        # Return a JSON response with the current followers and following and the predicted number of followers by  the end of the month
        response_data = {
            'profileImage' : user_data["data"]["profile_image_url"],
            'username': username,
            'followers': followers_count,
            'following': following_count,
            'ipredictedf': predicted_followers
        }
        return make_response(jsonify(response_data), 200)
    
api.add_resource(AnalyzeUserData, '/analyze')
api.add_resource(AnalyseUser, '/user')

if __name__ == '__main__':
    # Load the linear regression model
    model = joblib.load('linear_regression_model.pkl')
    app.run(port=9000,debug=True)
