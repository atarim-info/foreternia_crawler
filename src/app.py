# Task: Build a web crawler that gets data from a secure forum
# You need to create a crawler that scans, downloads and saves into files.
# Fetch as many documents as possible from this URL: https://foreternia.com/community/announcement-forum
# Requirements:

# Python 3.9+
#     Use concurrency / threading (up to 2 connections at the same time)
#     Use Typer in order to create a simple CLI.
# Data structure:
#     The files will be saved in the ./data/ directory
#     Each unique thread will have a filename prefix (chosen by you).
#     Each post will be a JSON file with the page link, title, published time and content.

import requests
import yaml
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import logging

# import data_extractor.extractor as extractor
from data_extractor import extractor as extractor

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

"""
    Loads the configuration from config.yaml.

    Returns:
        dict: The configuration
"""
def load_config():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        return config

"""
    Authenticates a user with the given cookie by setting it in a session object.

    Args:
        url (str): The base URL of the forum.
        cookie (str): The cookie to use for authentication.
        
    Returns:
        requests.Session: A session object with the authenticated user's session.
"""
def authenticate_with_cookie(url, cookie):
    session = requests.Session()
    session.headers.update(headers)
    session.cookies.set('cookie_name', cookie)
    return session


"""
    Authenticates a user with the given credentials by sending a POST request to the login endpoint.

    Args:
        url (str): The base URL of the forum.
        username (str): The username for authentication.
        password (str): The password for authentication.
        
    Returns:
        requests.Session: A session object with the authenticated user's session.
        
    Raises:
        ValueError: If the login details are incorrect or if the account has been banned.
"""
def authenticate_with_credentials(url, username, password):
    session = requests.Session()
    session.headers.update(extractor.headers)
    response = session.post(url + '/wp_login.php?do=login', data={'vb_login_username': username, 'vb_login_password': password})
    if 'Your login details are incorrect' in response.text:
        raise ValueError('Incorrect login details')
    if 'You have been banned from this forum' in response.text:
        raise ValueError('The account has been banned')
    return session
 
def authenticate(config):
    session = None
    url = config['url']
    username = config['authentication']['username']
    password = config['authentication']['password']
    
    try:
        logger.debug('Trying to authenticate with credentials')
        session = authenticate_with_credentials(url, username, password)
    except ValueError:
        logger.error('Authentication failed, trying with cookie')
        cookie = config['authentication']['cookie']
        session = authenticate_with_cookie(url, cookie)
    
    if session is None:
        logger.error('Authentication failed, trying with cookie')
        cookie = config['authentication']['cookie']
        session = authenticate_with_cookie(url, cookie)
    return session

def process_topic(session, topic):
    """
    Process a single topic URL using the provided session
    """
    logger.debug(f"Processing topic {topic['title']}")
    try:
        return extractor.get_data_from_topic_page(session, topic)
    except Exception as e:
        logger.error(f"Error processing topic {topic}: {str(e)}")
        return None
    
def main():
    config = load_config()
    session = authenticate(config)
    if session is None:
        logger.error('Authentication failed')
        return 
    
    url = config['url']

    # extractor.get_data_from_homepage(session, url)
    
    topics = extractor.get_data_from_anouncements_page(session, url)
    # for topic in topics["topics"]:
    #     extractor.get_data_from_topic_page(session, topic["url"])

    # Get the thread count from config, default to 2 if not specified
    max_threads = config.get('max_threads', 2)
    
    topics = extractor.get_data_from_anouncements_page(session, url)
    
    # Create a ThreadPoolExecutor with the specified number of threads
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Create a list to store the futures
        futures = []
        
        # Submit tasks to the thread pool
        for topic in topics["topics"]:
            future = executor.submit(process_topic, session, topic)
            futures.append(future)
            
        # Wait for all tasks to complete and handle results
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    logger.info(f"Successfully processed topic")
            except Exception as e:
                logger.error(f"Thread execution failed: {str(e)}")

    session.close()
    

if __name__ == '__main__':
    main()