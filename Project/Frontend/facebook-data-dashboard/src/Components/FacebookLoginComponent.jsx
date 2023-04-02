import React, { useState } from "react";
import FacebookLogin from "react-facebook-login";
// import { useNavigate } from "react-router-dom";

const FacebookLoginComponent = (props) => {
  const [error, setError] = useState("");
//   const history = useNavigate();

  const handleResponse = (response) => {
    if (response.accessToken) {
      // set the access token as a cookie
      document.cookie = `fb_accessToken=${response.accessToken}; path=/`;
      console.log(response.accessToken);

      // redirect to the dashboard page
    //   history.push("/");
    } else {
      setError("Failed to fetch the access token.");
      // redirect to the error page
    //   history.push("/error");
    }
  };

  return (
    <>
      {error && <p>{error}</p>}
      <FacebookLogin
        appId={"768209161168408"}
        autoLoad={false}
        fields="name,email,picture"
        callback={handleResponse}
      />
    </>
  );
};

export default FacebookLoginComponent;
