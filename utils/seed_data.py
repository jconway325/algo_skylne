#!/usr/bin/env python
import redis
import msgpack
import os
import sys
import json
import socket
import time
import pickle
from struct import Struct, pack
from os.path import dirname, abspath, join, realpath
from multiprocessing import Process, Manager, log_to_stderr

# add the shared settings file to namespace
sys.path.insert(0, ''.join((dirname(dirname(abspath(__file__))), "/src" )))
import settings

# Get the current working directory of this file.
# http://stackoverflow.com/a/4060259/120999
__location__ = realpath(join(os.getcwd(), dirname(__file__)))

if __name__ == "__main__":
    print "Connecting to Redis..."
    r = redis.StrictRedis(unix_socket_path=settings.REDIS_SOCKET_PATH)
    time.sleep(5)

    print 'Loading data over UDP via Horizon...'
    metric = 'horizon.test.udp'
    initial = int(time.time()) - settings.MAX_RESOLUTION

    with open(join(__location__, 'data.json'), 'r') as f:
      data = json.loads(f.read())
      series = data['results']
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

      for datapoint in series:
        datapoint[0] = initial
        initial += 1
        packet = msgpack.packb((metric, datapoint))
        sock.sendto(packet, (socket.gethostname(), settings.UDP_PORT))

    time.sleep(5)
    try:
        x = r.smembers('metrics.unique_metrics')
        if x == None:
        	raise Exception
        x = r.smembers('mini.unique_metrics')
        if x == None:
        	raise Exception
        x = r.get('metrics.horizon.test.udp')
        if x == None:
        	raise Exception
        x = r.get('mini.horizon.test.udp')
        if x == None:
        	raise Exception

        print "Congratulations! The data made it in. The Horizon pipeline seems to be working."
    except:
        print "Woops, looks like the metrics didn't make it into Horizon. Try again?"
