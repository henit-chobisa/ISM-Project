import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
import tweepy
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from sklearn.linear_model import LinearRegression

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

app = Flask(__name__)

# Initialize the NLTK sentiment analyzer
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

# This endpoint retrieves data about a user's posts and returns analyzed post data with predicted likes and shares
@app.route('/users/<user_id>/posts', methods=['POST'])
def get_user_posts(user_id):
    # Get the access token from the request header
    access_token = request.headers.get('Authorization')

    # Return a 400 Bad Request status if the access token is not provided
    if not access_token:
        return jsonify({'error': 'Access token not provided'}), 400

    # Make a request to the Graph API to retrieve the user's posts
    url = f"https://graph.facebook.com/{user_id}/posts"
    params = {'access_token': access_token}
    response = requests.get(url, params=params)

    # Parse the response and extract relevant data
    data = response.json()
    posts = data['data']
    post_data = []
    for post in posts:
        # Make a request to the Graph API to retrieve the post's likes and reshares
        post_id = post['id']
        likes_url = f"https://graph.facebook.com/{post_id}/likes"
        reshares_url = f"https://graph.facebook.com/{post_id}/sharedposts"
        likes_response = requests.get(likes_url, params=params)
        reshares_response = requests.get(reshares_url, params=params)

        # Analyze the post's sentiment using NLTK
        post_text = post['message'] if 'message' in post else ''
        post_sentiment = sid.polarity_scores(post_text)
        # Check if the post contains a photo or video, and if so, retrieve the URL
        media_url = ''
        media_type = ''
        if 'attachments' in post and 'data' in post['attachments'] and len(post['attachments']['data']) > 0:
            attachment = post['attachments']['data'][0]
            type = attachment['type']
            if attachment['type'] == 'photo':
                media_url = attachment['media']['image']['src']
            elif attachment['type'] == 'video':
                media_url = attachment['media']['source']
                    

        # Extract relevant data and add to the response
        likes_count = likes_response.json()['summary']['total_count'] if likes_response.ok else 0
        reshares_count = reshares_response.json()['summary']['total_count'] if reshares_response.ok else 0
        post_data.append({
            'id': post_id,
            'message': post_text,
            'created_time': post['created_time'],
            'sentiment': post_sentiment,
            'likes': likes_count,
            'reshares': reshares_count,
            'media_url': media_url,
            'media_type': type,
        })
    # Use a linear regression model to predict how much likes and reshares will increase in the future
    df = pd.DataFrame(post_data)
    X = df[['likes', 'reshares']]
    y_likes = df['likes'] + 1 # Add 1 to avoid divide-by-zero errors
    y_reshares = df['reshares'] + 1
    model_likes = LinearRegression().fit(X, y_likes)
    model_reshares = LinearRegression().fit(X, y_reshares)
    for post in post_data:
        post['predicted_likes'] = max(0, int(model_likes.predict([[post['likes'], post['reshares']]])[0]))
        post['predicted_reshares'] = max(0, int(model_reshares.predict([[post['likes'], post['reshares']]])[0]))

    # Return the data as JSON
    return jsonify(post_data)


@app.route('/me', methods=['GET'])
def getUserProfileData():
        # Get access token from authorization header
        access_token = request.headers.get('Authorization')
        # if access_token is None:
        #     return {'error': 'Access token missing from header'}, 400
        
        access_token = "EAAK6rqIqJhgBADEeJzmZBNkfrnAuB3goao4HaPZBbyOId7ZAFG9Peg0l4kV2oF5STjIhYFfvtTLRixctz3u3MoNoBZC2bq7sfidhMVu1XdR45ZAc3Rd7FIlUbZA18HeixxXbMHlnuu8nGHuRuMqgqyGNbysZCQfVJ1ES4zCzRInBRdnZB4gqGTWkXX4tVEaKLryo0Ud5hZAMrAVImdxJHQiHP"

        # Make a request to the Graph API to retrieve user data
        # url = "https://graph.facebook.com/me"
        # params = {'fields': 'name, email', 'access_token': access_token}
        # response = requests.get(url, params=params)
        # userData = response.json();
        
        # friendsURL = "https://graph.facebook.com/me/subscribers"
        # print(friendsURL)
        # params = {'uid': userData['id'],'access_token' : access_token}
        # response = requests.get(friendsURL, params=params);
        # print(response.json());

        # Parse the response and extract relevant data
        # data = response.json()
        # print(data)
        # followers = data['followers']['data']
        # follower_counts = []
        # for follower in followers:
        #     follower_counts.append(follower['created_time'])

        # # Use a linear regression model to predict how many followers the user will gain in the future
        # df = pd.DataFrame({'created_time': follower_counts})
        # df['created_time'] = pd.to_datetime(df['created_time'])
        # df['month'] = df['created_time'].dt.to_period('M')
        # counts = df.groupby('month')['created_time'].count().reset_index(name='count')
        # counts['month_start'] = counts['month'].apply(lambda x: x.start_time)
        # counts['timestamp'] = counts['month_start'].astype(int) // 10**9
        # X = counts[['timestamp']]
        # y = counts['count']
        # model = LinearRegression().fit(X, y)
        # current_timestamp = pd.Timestamp.now().floor('D').timestamp()
        # next_month_timestamp = (pd.Timestamp.now().floor('D') + pd.DateOffset(months=1)).timestamp()
        # current_count = model.predict([[current_timestamp]])[0]
        # next_month_count = model.predict([[next_month_timestamp]])[0]
        # predicted_count = int(next_month_count - current_count)

        # # Make a request to the Graph API to retrieve the user's posts
        url = "https://graph.facebook.com/me/posts"
        params = {'access_token': access_token, 'include_hidden' : True}
        response = requests.get(url, params=params)

        # Parse the response and extract relevant data
        data = response.json()
        print(data)
        posts = data['data']
        post_data = []
        photo_count = 0
        video_count = 0
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for post in posts:
            # Analyze the post's sentiment using NLTK
            post_text = post['message'] if 'message' in post else ''
            post_sentiment = sid.polarity_scores(post_text)
            if post_sentiment['compound'] > 0.5:
                sentiment_counts['positive'] += 1
            elif post_sentiment['compound'] < -0.5:
                sentiment_counts['negative'] += 1
            else:
                sentiment_counts['neutral'] += 1

            # Extract relevant data and add to the response
            post_type = 'text'
            if 'attachments' in post:
                attachments = post['attachments']['data']
                if attachments:
                    attachment_type = attachments[0]['type']
                if attachment_type == 'photo':
                    photo_count += 1
                    post_type = 'photo'
                elif attachment_type == 'video':
                    video_count += 1
                    post_type = 'video'
                    post_data.append({'created_time': post['created_time'], 'post_type': post_type})
                    
                    
        prime_time = ''
        if post_data:
            df = pd.DataFrame(post_data)
            df['created_time'] = pd.to_datetime(df['created_time'])
            df['hour'] = df['created_time'].dt.hour
            df['likes'] = df.apply(lambda x: get_likes_for_post(x['created_time'], access_token), axis=1)
            hour_likes = df.groupby('hour')['likes'].sum().reset_index(name='likes')
            prime_hour = hour_likes.loc[hour_likes['likes'].idxmax()]['hour']
            prime_time = f'{prime_hour}:00 - {prime_hour+1}:00'
            
            
        # Determine what type of post gets the most likes
        post_type_likes = {'text': 0, 'photo': 0, 'video': 0}
        for post in posts:
            post_type = 'text'
            if 'attachments' in post:
                attachments = post['attachments']['data']
            if attachments:
                attachment_type = attachments[0]['type']
                if attachment_type == 'photo':
                    post_type = 'photo'
                elif attachment_type == 'video':
                    post_type = 'video'
            post_type_likes[post_type] += get_likes_for_post(post['id'], access_token)

        max_likes_type = max(post_type_likes, key=post_type_likes.get)
        
        response_data = {
            # 'follower': follower,
            # 'predicted_followers_gain': predicted_count,
            'prime_posting_time': prime_time,
            'sentiment_likes': max(sentiment_counts, key=sentiment_counts.get),
            'photo_count': photo_count,
            'video_count': video_count,
            'most_liked_post_type': max_likes_type
        }

        return jsonify(response_data)
    
@app.route('/friends', methods=['GET'])
def getFriends():
        access_token = request.headers.get('Authorization')
        if access_token is None:
            return {'error': 'Access token missing from header'}, 400

        # Make a request to the Graph API to retrieve user data
        url = "https://graph.facebook.com/me"
        params = {'fields': 'name,id,friends,conversations{senders,updated_time,messages.limit(1000){from}}', 'access_token': access_token}
        response = requests.get(url, params=params)

        # Parse the response and extract relevant data
        data = response.json()
        friends = data['friends']['data']
        conversations = data['conversations']['data']
        messages = []
        for conversation in conversations:
            for message in conversation['messages']['data']:
                messages.append({'from': message['from']['id'], 'timestamp': pd.Timestamp(message['created_time']).timestamp()})
        messages_df = pd.DataFrame(messages)
        messages_df = messages_df.sort_values('timestamp')
        grouped_messages = messages_df.groupby('from').size().reset_index(name='count')
        sorted_messages = grouped_messages.sort_values(by=['count'], ascending=False)
        top_connections = sorted_messages.head(10)
        top_connection_ids = list(top_connections['from'])
        lost_connections = []
        for friend in friends:
            friend_id = friend['id']
            if friend_id not in top_connection_ids:
                if messages_df[messages_df['from'] == friend_id]['timestamp'].max() < pd.Timestamp.now().floor('D') - pd.DateOffset(months=6):
                    lost_connections.append(friend_id)

        # Make a request to the Graph API to retrieve the names and profiles of the top connections and lost connections
        url = "https://graph.facebook.com"
        params = {'ids': ','.join(top_connection_ids + lost_connections), 'fields': 'name,picture'}
        response = requests.get(url, params=params)
        data = response.json()

        # Extract the top connection and lost connection data from the response
        top_connections_data = []
        lost_connections_data = []
        for connection_id, connection_data in data.items():
            if connection_id in top_connection_ids:
                top_connections_data.append({'id': connection_id, 'name': connection_data['name'], 'picture': connection_data['picture']['data']['url']})
            elif connection_id in lost_connections:
                lost_connections_data.append({'id': connection_id, 'name': connection_data['name'], 'picture': connection_data['picture']['data']['url']})

        # Return the top connections and lost connections data in the response
        response_data = {'top_connections': top_connections_data, 'lost_connections': lost_connections_data}
        return response_data, 200
    
@app.route('/tweet', methods=['POST'])
def tweet():
    # Get access token from authorization header
    access_token = request.headers.get('Authorization')
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
    username = request.json.get('username')
    if username is None:
        return {'error': 'Username missing from request body'}, 400
    user_response = requests.get(user_url.format(username=username), headers=headers)
    if user_response.status_code != 200:
        return {'error': 'Error getting user ID'}, 400
    user_id = user_response.json()['data']['id']

    # Get the user's tweets
    tweet_params = {
        'max_results': 100,
        'tweet.fields': 'public_metrics'
    }
    tweet_response = requests.get(tweet_url.format(user_id=user_id), headers=headers, params=tweet_params)
    if tweet_response.status_code != 200:
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
        

if __name__ == '__main__':
    app.run(debug=True)
