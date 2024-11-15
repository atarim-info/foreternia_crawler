
import json
import os
import re

from bs4 import BeautifulSoup

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

date_pattern = r"\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [ap]m"

def get_data_from_anouncements_page(session, url, output_dir):
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
        with open(os.path.join(output_dir, topics_file), "w", encoding='utf-8') as f:
            json.dump(forum_topics, f, indent=2)

        logger.info(f"Saved {len(forum_topics['topics'])} forum topics to the '{output_dir}/{topics_file}' file.")

        return forum_topics


def get_data_from_topic_page(session, topic, output_dir):
    topic_url = topic["url"]
    response = session.get(topic_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all the posts on the forum
        posts = soup.find_all("div", class_="post-wrap")
        
        topic_data = {
            "title": topic["title"],
            "author": topic["author"],
            "url": topic_url,
            "posts": []
        }

        # Iterate over the posts and save each one to a JSON file
        for i, post in enumerate(posts):
            # Extract the post title and content
            try :
                post_data = get_single_post_data(post, output_dir=output_dir)
                topic_data['posts'].append(post_data)
            except KeyError as e:
                logger.warning(f"Post \"{post}\" has no id. Skipping.")
                continue

        # Save the post data to a JSON file
        topic_file_prefix = topic_url.split("/")[-1]
        topic_file = f"{topic_file_prefix}.json"
        with open(os.path.join(output_dir, topic_file), "w", encoding='utf-8') as f:
            json.dump(topic_data, f, indent=2)

        logger.info(f"Processed topic \"{topic['title']}\". Saved {len(posts)} posts to the '{output_dir}/{topic_file}' file.")

"""
    Extracts the post data from a BeautifulSoup post element and saves it to a JSON file.

    Args:
        post (bs4.element.Tag): A BeautifulSoup post element.
        output_dir (str): The directory to save the JSON file to.

    Returns:
        dict: A dictionary with the post data.
"""
def get_single_post_data(post, output_dir):
    id = post.get("id")
    if id is None:
        raise KeyError(f"Post \"{post}\" has no id. Skipping.")
    
    author = post.find("div", class_="author-name").text.strip()
    content = post.find("div", class_="wpforo-post-content").get_text(strip=True)
    content_bottom = post.find("div", class_="wpforo-post-content-bottom").get_text(strip=True)
    match = re.search(date_pattern, content_bottom)

    if match:
        post_date = match.group(0)
    else:    
        post_date = None

    # Create a dictionary with the post data
    post_data = {
                "id": id,
                "author": author,
                "content": content,
                "date": post_date
            }

    # # Save the post data to a JSON file
    # with open(os.path.join(output_dir, f"{id}.json"), "w", encoding='utf-8') as f:
    #     json.dump(post_data, f, indent=2)

    return post_data

def get_data_from_homepage(session, url, output_dir):
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
            
            # Save the post data to a JSON file            
            with open(os.path.join(output_dir, f"{post_id}.json"), "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2)