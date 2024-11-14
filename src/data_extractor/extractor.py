
import json
import os

from bs4 import BeautifulSoup

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

def get_data_from_anouncements_page(session, url):
    forum_url = url +  '/community/announcement-forum/'
    response = session.get(forum_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all the topics on the forum
        topics = soup.find_all("div", class_="wpforo-topic-info")

        # Iterate over the posts and add each one to a JSON forum topics file
        forum_topics = {
            "topics": []
        }
        for i, topic in enumerate(topics):
            # Extract the post title and content
            topic_title = topic.find("a")
            title_text = topic_title.text.strip()
            title_url = topic_title["href"]
            author = topic.find("div", class_="wpforo-topic-start-info").text.strip()


            # Create a dictionary with the post data
            topic_data = {
                "title": title_text,
                "url": title_url.strip(),
                "author": author
            }
            forum_topics['topics'].append(topic_data)

        # Save the post data to a JSON file
        topics_file = "forum_topics.json"
        with open(os.path.join(output_dir, topics_file), "w") as f:
            json.dump(forum_topics, f, indent=2)

        logger.info(f"Saved {len(forum_topics['topics'])} forum topics to the '{output_dir}/{topics_file}' file.")

        return forum_topics


def get_data_from_topic_page(session, topic):
    topic_url = topic["url"]
    response = session.get(topic_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all the posts on the forum
        posts = soup.find_all("div", class_="post-wrap")

        # Iterate over the posts and save each one to a JSON file
        for i, post in enumerate(posts):
            # Extract the post title and content
            get_single_post_data(post)

        logger.info(f"Processed topic \"{topic['title']}\". Saved {len(posts)} posts to the '{output_dir}' directory.")

def get_single_post_data(post):
    id = post.get("id")
    author = post.find("div", class_="author-name").text.strip()
    content = post.find("div", class_="wpforo-post-content").get_text(strip=True)
    content_bottom = post.find("div", class_="wpforo-post-content-bottom").get_text(strip=True)

            # Create a dictionary with the post data
    post_data = {
                "id": id,
                "author": author,
                "content": content,
                "content_bottom": content_bottom
            }

            # Save the post data to a JSON file
    with open(os.path.join(output_dir, f"{id}.json"), "w") as f:
        json.dump(post_data, f, indent=2)


def get_data_from_homepage(session, url):
    # forum_url = url + '/forums/'
    forum_url = url +  '/page/1'
    response = session.get(forum_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        threads = soup.select('article', class_='buddyx-article')
        for thread in threads:
            post_id = thread.get('id')
            category = thread.select_one('div', class_='post-meta-category__item').text.strip()
            title = thread.select_one('h2').text.strip()
            post = thread.select_one('div', class_='entry-content').text.strip()

            data = {
                'post_id': post_id,
                'category': category,
                'title': title,
                'post': post
            }

            with open(f'data/{post_id}.json', 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)