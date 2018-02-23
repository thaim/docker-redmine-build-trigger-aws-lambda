#!/usr/bin/env python3

"""
trigger automated docker build for trunk redmine
"""

import json
import logging
import os
import sys
import time

import svn.remote
import urllib.request


def hit_on_update(token):
    """
    trigger docker build when redmine trunk is updated
    """
    one_day = 24 * 60 * 60
    rev, last_update = redmine_trunk()
    now = time.time()
    # if last_update >= now - one_day:
    # always trigger docker build
    hit_trigger(token, rev)

    return last_update, rev

def redmine_trunk():
    """
    check redmine trunk and return latest revision and last update
    """
    client = svn.remote.RemoteClient("http://svn.redmine.org/redmine/trunk")
    info   = client.info()
    return info['entry_revision'], info['commit_date']

def hit_trigger(token, rev):
    url     = "https://registry.hub.docker.com/u/thaim/redmine/trigger/" + token + "/"
    method  = "POST"
    headers = {"Content-Type" : "application/json"}
    params  = {"docker_tag": "latest"}
    postdata = urllib.parse.urlencode(params).encode('utf-8')

    request = urllib.request.Request(url=url, data=postdata, method=method, headers=headers)
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode("utf-8")
    print(response_body)

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    token = os.environ['TRIGGER_TOKEN']

    date, rev = hit_on_update(token)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        token = sys.argv[1]
    hit_on_update(token)
