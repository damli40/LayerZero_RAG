"""
Mocks fetching trending tweets from X (Twitter).
"""
# TODO: Replace with real API calls to X

def fetch_trending_tweets(topic):
    """
    Returns a list of mocked trending tweets for a given topic.
    Args:
        topic (str): The topic to search for.
    Returns:
        list: List of tweet strings.
    """
    return [f"Trending tweet 1 about {topic}", f"Trending tweet 2 about {topic}"] 