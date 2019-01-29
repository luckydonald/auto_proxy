import os

from jinja2 import Template, Environment, FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError, TemplateNotFound
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)


class RelEnvironment(Environment):
    """
    Override join_path() to enable relative template paths.
    http://stackoverflow.com/a/8530761/3423324
    """
    def join_path(self, template, parent):
        path = os.path.join(os.path.dirname(parent), template)
        logger.info(f"template file path: {path}")
        return path
    # end def join_path
# end class RelEnvironment


class RelFileSystemLoader(FileSystemLoader):
    def __init__(self, searchpath, encoding='utf-8', followlinks=False):
        from jinja2._compat import string_types
        if isinstance(searchpath, string_types):
            searchpath = [searchpath]
        # end if
        searchpath = [os.path.abspath(path) for path in searchpath]
        super().__init__(searchpath, encoding=encoding, followlinks=followlinks)
    # end def

    def get_source(self, environment, template):
        from jinja2.loaders import split_template_path
        from jinja2.utils import open_if_exists
        from os import path
        pieces = split_template_path(template)
        for searchpath in self.searchpath:
            filename = path.join(searchpath, *pieces)
            logger.warn(f"File to open: {filename}")
            f = open_if_exists(filename)
            if f is None:
                continue
            try:
                contents = f.read().decode(self.encoding)
            finally:
                f.close()

            mtime = path.getmtime(filename)

            def uptodate():
                try:
                    return path.getmtime(filename) == mtime
                except OSError:
                    return False
            return contents, filename, uptodate
        raise TemplateNotFound(template)
    # end def
# end class


def get_template(file_name) -> Template:
    logger.warn("pwd: " + os.getcwd())
    loader = RelFileSystemLoader("templates")
    # loader.get_source(None, template=file_name)
    env = RelEnvironment(loader=loader)
    try:
        return env.get_template(file_name)
    except TemplateSyntaxError as e:
        logger.warn("{file}:{line} {msg}".format(msg=e.message, file=e.filename if e.filename else file_name, line=e.lineno))
        raise e
    except TemplateNotFound as e:
        logger.warn("{file}: {msg}".format(msg=e.message, file=e.filename if e.filename else file_name))
        raise e
    # end with
# end def get_template
