# -*- coding: utf-8 -*-
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)

from auto_proxy.main import main

if __name__ == '__main__':
    logging.add_colored_handler(level=logging.INFO)
    logger.info("Starting container...")
    main()
# end if

