import inspect
import os
import sys

import redis

redis = redis.Redis(decode_responses=True)

parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
sys.path.insert(0, parentdir)
