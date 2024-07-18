#!/usr/bin/env python3
"""
This module provides a function to fetch and cache web pages using Redis.
"""

import redis
import requests
from typing import Callable
from functools import wraps

# Initialize Redis connection
r = redis.Redis()

def cache_with_expiration(method: Callable) -> Callable:
    """
    Decorator to cache the result of a function call for 10 seconds.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        # Check if the URL is already cached
        cached_data = r.get(f"cache:{url}")
        if cached_data:
            return cached_data.decode('utf-8')

        # Call the original method
        result = method(url)

        # Cache the result with an expiration time of 10 seconds
        r.setex(f"cache:{url}", 10, result)
        return result
    return wrapper

@cache_with_expiration
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a URL and cache the result with an expiration time of 10 seconds.
    """
    # Increment the access count for the URL
    r.incr(f"count:{url}")

    # Fetch the content of the URL
    response = requests.get(url)
    return response.text

if __name__ == "__main__":
    # Example usage
    url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.example.com"
    print(get_page(url))
    print(f"URL accessed {r.get(f'count:{url}').decode('utf-8')} times.")

