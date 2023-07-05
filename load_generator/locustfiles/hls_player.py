import os
import random
import logging
import hashlib
import base64
import uuid
import m3u8
import resource
import sys
import urllib3
from locust import HttpUser, TaskSet, task, between

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure Python 3 is being used
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

# Set the highest limit of open files in the server
resource.setrlimit(resource.RLIMIT_NOFILE, resource.getrlimit(resource.RLIMIT_NOFILE))

logger = logging.getLogger(__name__)

# Retrieve channel URI and host port from environment variables
CHANNEL_URI = os.getenv('CHANNEL_URI')
HOST_PORT = os.getenv('HOST_PORT')

class PlayerTaskSet(TaskSet):
    # This task set plays complete stream.

    def on_start(self):
        # Calculate ticket and user_id for each user starting to play stream
        secret = 'secret'  # replace with your actual secret
        self.user_id = str(uuid.uuid4()).lower()
        ticket_string = f"9999999999./{CHANNEL_URI}.{secret}.{self.user_id}"
        self.ticket = base64.urlsafe_b64encode(hashlib.md5(ticket_string.encode()).digest()).rstrip(b'=').decode('utf-8')
        logger.debug(f"Ticket string is: {ticket_string}")
        logger.debug(f"Ticket is: {self.ticket}")

        # Define base URL
        self.base_url = f"{MyLocust.host}:{HOST_PORT}/v4/{self.ticket}/9999999999/{self.user_id}/{self.ticket}/9999999999/{CHANNEL_URI}"

        # Get master manifest
        master_url = f"{self.base_url}/playlist.m3u8"
        logger.debug(f"Master Manifest File URL: {master_url}")
        master_m3u8 = self.client.get(master_url, name="playlist", verify=False)
        self.parsed_master_m3u8 = m3u8.M3U8(content=master_m3u8.text, base_uri=self.base_url)
        logger.debug(f"parsed_master_m3u8 playlists: {self.parsed_master_m3u8.playlists[0]}")

    @task(1)
    def play_stream(self):
        # Get variant URI from the master manifest
        variant_uri = self.parsed_master_m3u8.playlists[0].uri

        # Fetch variant m3u8 file
        variant_m3u8 = self.client.get(f"{self.base_url}/{variant_uri}", name="chunks", verify=False)
        parsed_variant_m3u8 = m3u8.M3U8(content=variant_m3u8.text, base_uri=self.base_url)

        # Get all the segments and sleep for the duration of each segment
        segments_to_iterate = 1 if random.random() > 0.1 else 2  # 0-10% chance of choosing 2 segments

        for segment in parsed_variant_m3u8.segments[:segments_to_iterate]:
            logger.debug("Getting segment {0}".format(segment.absolute_uri))
            seg_get = self.client.get(segment.absolute_uri, name="ts files", verify=False)
            sleep_time = segment.duration - seg_get.elapsed.total_seconds()
            logger.debug(f"Request took {seg_get.elapsed.total_seconds()} and segment duration is {segment.duration}. Sleeping for {sleep_time}")
            self._sleep(sleep_time)

class MyLocust(HttpUser):
    # Main locust class
    host = os.getenv('HOST_URL', "http://localhost")
    tasks = [PlayerTaskSet]
    wait_time = between(0, 0)

