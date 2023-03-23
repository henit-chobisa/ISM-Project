from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# Initialize the NLTK sentiment analyzer
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

# This endpoint retrieves and analyzes data about a user's posts on Twitter
class AnalyzeUserData(Resource):
    def post(self):
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

            # Add relevant data to the response
            tweet_data.append({
                'text': tweet['text'],
                'sentiment': tweet_sentiment,
                'likes': likes,
                'retweets': retweets
            })

        # Use a linear regression model to predict how much the user's engagement will increase in the future
        df = pd.DataFrame(tweet_data)
        df['timestamp'] = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'))
        df['month'] = df['timestamp'].dt.to_period('M')
        engagement_counts = df.groupby('month')[['likes', 'retweets']].sum().reset_index()
        engagement_counts['month_start'] = engagement_counts['month'].apply(lambda x: x.start_time)
        engagement_counts['timestamp'] = engagement_counts['month_start'].astype(int) // 10**9
        X = engagement_counts[['timestamp']]
        y = engagement_counts[['likes', 'retweets']]
        model = LinearRegression().fit(X, y)
        current_timestamp = pd.Timestamp.now().floor('D').timestamp()
        next_month_timestamp = (pd.Timestamp.now().floor('D') + pd.DateOffset(months=1)).timestamp()
        next_month = pd.DataFrame({'timestamp': [next_month_timestamp]})
        predicted_engagement_counts = model.predict(next_month)[0]
        predicted_likes = int(predicted_engagement_counts[0])
        predicted_retweets = int(predicted_engagement_counts[1])

        # Add the predicted engagement counts to the response
        response_data = {
           'tweets': tweet_data,
           'predicted_likes': predicted_likes,
           'predicted_retweets': predicted_retweets
        }

        return jsonify(response_data), 200
    
api.add_resource(AnalyzeUserData, '/analyze')

if __name__ == '__main__':
    app.run(port=9000,debug=True)