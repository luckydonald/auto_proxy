# -*- coding: utf-8 -*-
from datetime import datetime

from DictObject import DictObject
from luckydonaldUtils.logger import logging
__all__ = ['Watcher']
__author__ = 'luckydonald'
logger = logging.getLogger(__name__)


from docker import DockerClient


# like https://github.com/colebrumley/des/blob/41552576a2f5f3a8ea2f3667a2a12f6cb1e38399/des/watcher.py

class Watcher(object):
    """
    Docker daemon monitor object
    """
    def __init__(self,
                 endpoint='unix:///var/run/docker.sock',
                 timeout=None,
                 api_version='auto',
                 tls_config=None, filters=None):
        """

        :param endpoint:
        :param timeout:
        :param api_version:
        :param tls_config:
        :param filters:  Like `{"status":["exited"]}`. See https://stackoverflow.com/a/28054296/3423324 and https://docs.docker.com/engine/api/v1.31/#operation/SystemEvents
        """
        self.filters = filters
        self.endpoint = endpoint
        self.client = DockerClient(
            base_url=endpoint,
            version=api_version,
            timeout=timeout,
            tls=tls_config)
    # end def

    def run(self):
        logger.info("watching " + self.endpoint + " for container events")
        yield from (DictObject.objectify(e) for e in self.client.events(since=datetime.utcnow(), filters=self.filters, decode=True))
    # end def
# end class

