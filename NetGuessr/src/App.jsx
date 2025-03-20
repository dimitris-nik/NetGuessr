import React, { useState, useEffect } from "react";
import Website from "./Website"

const URL = "http://localhost:5000/getRandomWebsite";
export default function App() {
  const [website_url, setWebsiteUrl] = useState('');
  useEffect(() => {
      console.log("Fetching website URL");
      fetch(URL)
        .then((res) => {
          return res.json();
        })
        .then((data) => {
          setWebsiteUrl(data.url);
          console.log("Fetched website URL");
        });
    }, []);
  return (
    <main>
      <h1>NetGuessr</h1>
      <p>Guess the websites age. Explore the internet through time!</p>
      <Website url={website_url}/>
      <div className="hidden">
      </div>
    </main>
  )
}
 
