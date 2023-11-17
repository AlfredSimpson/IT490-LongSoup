import pika
import time
import logging
import os, sys, json
import pymongo
from dotenv import load_dotenv

load_dotenv()

"""
This worker will handle requests to and from dev. It will be called indirectly by workers on dev, which will send a message to the queue.
Once the message is received, this worker will run the necessary scripts to move the code from dev to qa.
"""
