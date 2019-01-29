__author__ = 'luckydonald'


def extract_container_envs(container):
    """
    Extracts a dict of environment variables from a docker container

    Example:

    >>> # Mock class for the container
    ... class _(object):
    ...   def __init__(self, envs):
    ...     self.attrs = {'Config': {'Env': envs}}
    ...

    >>> # Mock variable for the container
    ... container = _(['URL_HOSTNAME=more-bots.bonbotics.io', 'URL_PATH=derpi_derpbooru', 'PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'LANG=C.UTF-8', 'GPG_KEY=0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D', 'PYTHON_VERSION=3.6.3', 'PYTHON_PIP_VERSION=9.0.1', 'GROUP_UID=1020', 'USER_UID=1020', 'GIT_COMMIT=75f1a941c796494f7830744135e123ba3a7e0545', 'GIT_MESSAGE=Documented travis file a bit more.', 'PIP_NO_CACHE_DIR=off', 'PIP_DISABLE_PIP_VERSION_CHECK=on'])

    >>> result = extract_container_envs(container)

    >>> result == {
    ...     'URL_HOSTNAME': 'more-bots.bonbotics.io',
    ...     'URL_PATH': 'derpi_derpbooru',
    ...     'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
    ...     'LANG': 'C.UTF-8',
    ...     'GPG_KEY': '0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D',
    ...     'PYTHON_VERSION': '3.6.3',
    ...     'PYTHON_PIP_VERSION': '9.0.1',
    ...     'GROUP_UID': '1020',
    ...     'USER_UID': '1020',
    ...     'GIT_COMMIT': '75f1a941c796494f7830744135e123ba3a7e0545',
    ...     'GIT_MESSAGE': 'Documented travis file a bit more.',
    ...     'PIP_NO_CACHE_DIR': 'off',
    ...     'PIP_DISABLE_PIP_VERSION_CHECK': 'on'
    ... }
    True

    :param container: The docker container object

    :return: Dictionary with the environment vars
    :rtype: Dict[str, str]
    """
    env_list = container.attrs.get('Config', {}).get('Env', [])
    return envs_to_dict(env_list)
# end def


def envs_to_dict(env_list):
    """
    Extracts a dict of environment variables from a list of environment variables

    Example:

    >>> envs = [
    ...     'URL_HOSTNAME=more-bots.bonbotics.io',
    ...     'URL_PATH=derpi_derpbooru',
    ...     'PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
    ...     'LANG=C.UTF-8',
    ...     'GPG_KEY=0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D',
    ...     'PYTHON_VERSION=3.6.3',
    ...     'PYTHON_PIP_VERSION=9.0.1',
    ...     'GROUP_UID=1020',
    ...     'USER_UID=1020',
    ...     'GIT_COMMIT=75f1a941c796494f7830744135e123ba3a7e0545',
    ...     'GIT_MESSAGE=Documented travis file a bit more.',
    ...     'PIP_NO_CACHE_DIR=off',
    ...     'PIP_DISABLE_PIP_VERSION_CHECK=on'
    ... ]

    >>> result = envs_to_dict(container)

    >>> result == {
    ...     'URL_HOSTNAME': 'more-bots.bonbotics.io',
    ...     'URL_PATH': 'derpi_derpbooru',
    ...     'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
    ...     'LANG': 'C.UTF-8',
    ...     'GPG_KEY': '0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D',
    ...     'PYTHON_VERSION': '3.6.3',
    ...     'PYTHON_PIP_VERSION': '9.0.1',
    ...     'GROUP_UID': '1020',
    ...     'USER_UID': '1020',
    ...     'GIT_COMMIT': '75f1a941c796494f7830744135e123ba3a7e0545',
    ...     'GIT_MESSAGE': 'Documented travis file a bit more.',
    ...     'PIP_NO_CACHE_DIR': 'off',
    ...     'PIP_DISABLE_PIP_VERSION_CHECK': 'on'
    ... }
    True

    :param env_list: The environement variables
    :type  env_list: List[str]

    :return: Dictionary with the environment vars
    :rtype: Dict[str, str]
    """
    return {k: v for k, v in [split_env(env) for env in env_list]}
# end def


def split_env(var):
    """
    Split a vir
    >>> split_env('URL_HOSTNAME=more-bots.bonbotics.io')
    ('URL_HOSTNAME', 'more-bots.bonbotics.io')

    >>> split_env('URL_PATH=derpi_derpbooru')
    ('URL_PATH', 'derpi_derpbooru')

    >>> split_env('PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')
    ('PATH', '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')

    >>> split_env('LANG=C.UTF-8')
    ('LANG', 'C.UTF-8')

    >>> split_env('GPG_KEY=0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D')
    ('GPG_KEY', '0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D')

    >>> split_env('PYTHON_VERSION=3.6.3')
    ('PYTHON_VERSION', '3.6.3')

    >>> split_env('PYTHON_PIP_VERSION=9.0.1')
    ('PYTHON_PIP_VERSION', '9.0.1')

    >>> split_env('GROUP_UID=1020')
    ('GROUP_UID', '1020')

    >>> split_env('USER_UID=1020')
    ('USER_UID', '1020')

    >>> split_env('GIT_COMMIT=75f1a941c796494f7830744135e123ba3a7e0545')
    ('GIT_COMMIT', '75f1a941c796494f7830744135e123ba3a7e0545')

    >>> split_env('GIT_MESSAGE=Documented travis file a bit more.')
    ('GIT_MESSAGE', 'Documented travis file a bit more.')

    >>> split_env('PIP_NO_CACHE_DIR=off')
    ('PIP_NO_CACHE_DIR', 'off')

    >>> split_env('PIP_DISABLE_PIP_VERSION_CHECK=on')
    ('PIP_DISABLE_PIP_VERSION_CHECK', 'on')

    >>> split_env('TEST_WITH_EQUAL_IN_IT=foo=bar')
    ('TEST_WITH_EQUAL_IN_IT', 'foo=bar')

    :param var: A env definition in the format of `VARIABLE=value`
    :type  var: str

    :return: tuple ``(variable, value)``
    :rtype: Tuple[str]
    """
    return var.split("=", maxsplit=1)
# end def
