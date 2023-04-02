import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import pytz
import requests
import json

# Set up the Twitter API credentials and endpoint
bearer_token = "AAAAAAAAAAAAAAAAAAAAAK%2B3NgEAAAAA%2BanA%2FoqLWn%2FdtDuIzX48%2FH%2FMHZg%3Dn5MGElfAsd0ySRhd5ukJrxxLWR4yADb9QILvc3KXHrqU6r4a5C"
endpoint = "https://api.twitter.com/2/"

# Define the function to get the user's follower count
def get_follower_count(user_id):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    tweet_params = {
        'user.fields': 'public_metrics'
    }
    response = requests.get(endpoint + f"users/{user_id}", headers=headers, params=tweet_params)
    if response.status_code != 200:
        raise Exception(f"Failed to get user's follower count: {response.status_code}")
    user_data = json.loads(response.content)
    print(user_data)
    return user_data["data"]["public_metrics"]["followers_count"]

# Set up the start and end dates for data collection
end_date = datetime.now(pytz.utc)
start_date = end_date - timedelta(days=30)

# Get the user's follower count at the start and end dates
follower_count_start = get_follower_count("1521385989167493120")
follower_count_end = get_follower_count("1521385989167493120")

# Get the user's follower counts for the last 30 days
follower_counts = []
for i in range(30):
    date = start_date + timedelta(days=i)
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {
        "query": f"from:{'henit_chobisa'}",
        # "since_id" : date.strftime('%Y-%m-%d'),
        # "until_id" : date+timedelta(days=1),
        "max_results": 100,
        "user.fields": "public_metrics",
        "tweet.fields": "public_metrics"
    }
    response = requests.get(endpoint + "tweets/search/recent", headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to get follower counts: {response.status_code}")
    tweets_data = json.loads(response.content)
    followers = sum([tweet["public_metrics"]["retweet_count"]+tweet["public_metrics"]["reply_count"]+tweet["public_metrics"]["like_count"] for tweet in tweets_data["data"]])
    follower_counts.append(followers)

# Create a pandas dataframe with the data
data = {"follower_counts": follower_counts}
df = pd.DataFrame(data)

# Fit a linear regression model to the data
X = df.index.values.reshape(-1, 1)
y = df["follower_counts"].values.reshape(-1, 1)
model = LinearRegression().fit(X, y)

# Save the trained model to a file
joblib.dump(model, "linear_regression_model.pkl")
