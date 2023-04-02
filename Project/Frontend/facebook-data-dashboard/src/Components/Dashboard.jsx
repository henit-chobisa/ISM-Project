import React, { useEffect, useState } from "react";
import "./tile.css";
import image from "./IMG_4435.png"

function getSentiment(sentimentObj) {
    if (sentimentObj.compound > 0.05) {
      return "Positive";
    } else if (sentimentObj.compound < -0.05) {
      return "Negative";
    } else {
      return "Neutral";
    }
}

const TwitterPostTile = ({
    data
}) => {
    console.log(data)
  return (
    <div class="twitter-post-tile-container">
      <div class="twitter-post-tile-scroll">
        { data.tweets.map((element) => {
            return (<div class="twitter-post-tile">
            <div class="twitter-post-tile-header">
              <span class="twitter-post-tile-sentiment">Sentiment {getSentiment(element.sentiment)}</span>
              <span class="twitter-post-tile-likes">Likes {element.likes}</span>
              <span class="twitter-post-tile-retweets">Retweets {element.retweets}</span>
            </div>
            <div class="twitter-post-tile-body">
              <p class="twitter-post-tile-text">
                {element.text}
              </p>
            </div>
            <div class="twitter-post-tile-footer">
              <span class="twitter-post-tile-predicted-likes">
                Predicted Likes {element.predicted_likes}
              </span>
              <span class="twitter-post-tile-predicted-retweets">
                Predicted Retweets {element.predicted_retweets}
              </span>
            </div>
          </div> )
        })}
      </div>
    </div>
  );
};

const Dashboard = () => {

  const [data, setData] = useState({tweets: []})
  const [user, setUser] = useState({ profileImage : "", username: "", followers : 0, following : 0, ipredictedf : 0 })

  useEffect(() => {
    getData();
    getUser();
  }, []);

  const getData = () => {
    fetch("http://localhost:9000/analyze", {
        method: 'GET',
    }).then((response) => {
        return response.json()
    }).then((data) => {
        setData(data)
    })  
  }

  const getUser = () => {
    fetch('http://localhost:9000/user', {
        method: 'GET',
    }).then((response) => {
        return response.json()
    }).then((data) => {
        console.log(data)
        setUser(data)
    })
  }

  return (
    <div class="main">
      <TwitterPostTile
        data={data}
      />
      <div class="user">
        <p class="username">@{user.username}</p>
        <img class="profImg" src={image} alt="" />
        <div className="ff">
            <p class="followers">Followers {user.followers}</p>
            <p class="following">Following {user.following}</p>
        </div>
        <p class="predicted">Predicted Follower Increment : {user.ipredictedf}</p>
      </div>
    </div>
  );
};

export default Dashboard;
