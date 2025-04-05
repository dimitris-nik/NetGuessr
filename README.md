# NetGuessr

**NetGuessr** is a web-based game where players test their knowledge of internet history by guessing the age of a randomly selected website. Think of it as *GeoGuessr*, but for the evolution of the internet.

---

## 🕸️ What is NetGuessr?

NetGuessr presents you with a version of a popular website from the past 20 years, pulled from the [Internet Archive's Wayback Machine](https://archive.org/web/). Your task is to analyze its design, content, layout, and context clues to guess **what year it's from**.

To keep things challenging, the proxy filters out any explicit mentions of years from the page, so no easy giveaways!

---

## 🛠️ Current Status

NetGuessr is in **early alpha**. As of now, only the **proxy** feature is working. This means the game currently fetches and filters archived versions of websites, but gameplay logic (like input, scoring, or rounds) hasn't been implemented yet.

---

## 🔧 Tech Stack

- **Frontend:** [React](https://reactjs.org/) — Renders the UI and handles player interaction.
- **Backend:** [Flask](https://flask.palletsprojects.com/) — Powers the proxy server and REST API.
- **Data Source:** [Internet Archive](https://archive.org/) — Used to fetch archived web pages.

---

## 🎮 How to Play (Future Vision)

1. A random website is selected from a curated list of historically significant or popular sites.
2. A random snapshot of that site is fetched via the Internet Archive.
3. The site is proxied and sanitized to remove any year-based hints.
4. You examine the design, features, and context to guess the year it was captured.

