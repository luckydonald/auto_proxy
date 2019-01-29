import os

from jinja2 import Template, Environment, FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)

class RelEnvironment(Environment):
    """
    Override join_path() to enable relative template paths.
    http://stackoverflow.com/a/8530761/3423324
    """
    def join_path(self, template, parent):
        return os.path.join(os.path.dirname(parent), template)
    # end def join_path
# end class RelEnvironment


def get_template(file_name) -> Template:
    env = RelEnvironment(loader=FileSystemLoader("templates"))
    try:
        return env.get_template(file_name)
    except TemplateSyntaxError as e:
        logger.warn("{file}:{line} {msg}".format(msg=e.message, file=e.filename if e.filename else file_name, line=e.lineno))
        raise e
    # end with
# end def get_template
