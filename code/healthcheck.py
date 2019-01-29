# -*- coding: utf-8 -*-
from luckydonaldUtils.logger import logging
from pytgbot.bot import Bot
from docker import DockerClient

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)


try:
    client = DockerClient(base_url='unix:///var/run/docker.sock', version='auto')
    client.ping()

    # all successful
    exit(0)
except Exception:
    logger.exception("Healthcheck failed.")
    exit(1)
# end try
