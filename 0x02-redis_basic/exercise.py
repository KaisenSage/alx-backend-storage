#!/usr/bin/env python3
"""
This module provides a Cache class for interacting with Redis.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps

def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of calls to a method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper

def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a particular function.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        inputs = str(args)
        outputs = method(self, *args, **kwargs)
        self._redis.rpush(f"{method.__qualname__}:inputs", inputs)
        self._redis.rpush(f"{method.__qualname__}:outputs", str(outputs))
        return outputs
    return wrapper

class Cache:
    """
    Cache class for basic Redis operations.
    """

    def __init__(self):
        """
        Initialize the Cache class.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a random key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """
        Get data from Redis and optionally convert it using fn.
        """
        data = self._redis.get(key)
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """
        Get data from Redis as a string.
        """
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """
        Get data from Redis as an integer.
        """
        return self.get(key, int)

def replay(method: Callable):
    """
    Display the history of calls of a particular function.
    """
    r = redis.Redis()
    method_name = method.__qualname__
    inputs = r.lrange(f"{method_name}:inputs", 0, -1)
    outputs = r.lrange(f"{method_name}:outputs", 0, -1)
    print(f"{method_name} was called {len(inputs)} times:")
    for input_, output in zip(inputs, outputs):
        print(f"{method_name}(*{input_.decode('utf-8')}) -> {output.decode('utf-8')}")

