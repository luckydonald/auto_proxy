# -*- coding: utf-8 -*-
import os
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)


SIGNALS = os.getenv('SIGNALS', None)
# can be none #assert(SIGNALS is not None)  # SIGNALS environment variable
