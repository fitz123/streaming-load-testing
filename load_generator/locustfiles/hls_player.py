##################################################
# Simple emulator of an HLS media player
##################################################
# MIT License
##################################################
# Author: Mark Ogle
# License: MIT
# Email: mark@unified-streaming.com
# Maintainer: roberto@unified-streaming.com
##################################################

import os
from locust import HttpUser, TaskSet, task, between
import m3u8
import logging
import resource
import sys
import random

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

logger = logging.getLogger(__name__)
print(resource.getrlimit(resource.RLIMIT_NOFILE))
# set the highest limit of open files in the server
resource.setrlimit(resource.RLIMIT_NOFILE, resource.getrlimit(
    resource.RLIMIT_NOFILE)
)

MANIFEST_FILE = os.getenv('MANIFEST_FILE')
HOST_PORT = os.getenv('HOST_PORT')

class PlayerTaskSet(TaskSet):
    """
    Play complete stream.
    Steps:
    * get manifest
    * select highest bitrate
    * get each segment in order
    * wait for segment duration in between downloads, to act somewhat like
    a player kinda dumb hack to make results gathering easier is to merge
    everything into a single name
    """
    def on_start(self):
        # Get the base URL from the MANIFEST_FILE
        base_url = (f"{MyLocust.host}:{HOST_PORT}/{MANIFEST_FILE.rsplit('/', 1)[0]}")

        # get master manifest
        master_url = f"{base_url}/{MANIFEST_FILE.rsplit('/', 1)[1]}"
        master_m3u8 = self.client.get(master_url, name="playlist", verify=False)
        self.parsed_master_m3u8 = m3u8.M3U8(content=master_m3u8.text, base_uri=base_url)

    @task(1)
    def play_stream(self):
        # Get the base URL from the MANIFEST_FILE
        base_url = (f"{MyLocust.host}:{HOST_PORT}/{MANIFEST_FILE.rsplit('/', 1)[0]}")

        # get the chunks URI from the master manifest
        variant_uri = self.parsed_master_m3u8.playlists[0].uri
        variant_url = f"{base_url}/{variant_uri}"
        variant_m3u8 = self.client.get(variant_url, name="chunks", verify=False)
        parsed_variant_m3u8 = m3u8.M3U8(content=variant_m3u8.text, base_uri=base_url)

        ## get all the segments
        #for segment in parsed_variant_m3u8.segments:
        #    logger.debug("Getting segment {0}".format(segment.absolute_uri))
        #    seg_get = self.client.get(segment.absolute_uri, name="ts files" ,verify=False)
        #    sleep = segment.duration - seg_get.elapsed.total_seconds()
        #    logger.debug("Request took {elapsed} and segment duration is {duration}. Sleeping for {sleep}".format(
        #        elapsed=seg_get.elapsed.total_seconds(), duration=segment.duration, sleep=sleep))
        #    self._sleep(sleep)

class MyLocust(HttpUser):
    host = os.getenv('HOST_URL', "http://localhost")
    tasks = [PlayerTaskSet]
    wait_time = between(0, 0)
