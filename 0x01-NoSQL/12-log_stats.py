#!/usr/bin/env python3
"""12-log_stats.py"""
from pymongo import MongoClient

if __name__ == "__main__":
    client = MongoClient('mongodb://127.0.0.1:27017')
    collection = client.logs.nginx
    num_logs = collection.count_documents({})
    print(f"{num_logs} logs")
    print("Methods:")
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    for method in methods:
        count = collection.count_documents({"method": method})
        print(f"\tmethod {method}: {count}")
    status_check = collection.count_documents({"method": "GET", "path": "/status"})
    print(f"{status_check} status check")

