# 485 Project (Web Development Coursework)

## Project Overview

"This was actually two related projects from my web development coursework.

The first was building a full-stack web application—like a simplified Instagram or blog platform. I built a server-side static site generator in Python that converted templates to HTML, with user authentication, posts, comments, and likes all stored in a SQL database. On the frontend, I added JavaScript features like infinite scroll and real-time interactions using AJAX calls to a REST API I built.

The second was building a search engine. I used MapReduce in Python to process and index a large collection of web pages, then built a REST API that the frontend could query to get search results. It was a simplified version of how Google works—crawling, indexing, and ranking."

## Q&A

### Q4: "How did you structure your database? What tables did you have?"

**Conversational Answer:**

"We had tables for the core entities:

- **users:** user_id, username, email, password_hash, created_at
- **posts:** post_id, user_id (foreign key), image_path, caption, created_at
- **comments:** comment_id, post_id, user_id, text, created_at
- **likes:** post_id, user_id (composite primary key)
- **followers:** follower_id, following_id (who follows whom)

Foreign keys maintained referential integrity—you can't have a comment on a post that doesn't exist. The likes table used a composite primary key so a user can only like a post once.

For the feed, we'd join posts with users and aggregate likes and comments. Something like: get all posts from users I follow, ordered by date, with like counts and recent comments."
