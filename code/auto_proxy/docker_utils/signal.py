import docker
from docker.errors import APIError
from docker.models.containers import Container
from luckydonaldUtils.logger import logging
from typing import List, Tuple, Union, cast
from signal import Signals

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)


def parse_signals(container_id: str, string: str) -> List[Tuple[str, Signals]]:
    """
    Sends a signal to a docker client,
    e.g. `SIGHUP` to and `nginx` container for triggering a configuration reload.
    :return:
    """
    parts = string.split(",")
    return [(container_id, parse_signal(part)) for part in parts]
# end def


def parse_trigger_config(string: str) -> List[Tuple[str, Signals]]:
    parts = string.split(",")
    triggers = []
    for part in parts:
        container, signal = (p.strip() for p in part.split("="))  # if this fails you don't have "key=value"...
        signal = parse_signal(signal)
        entry = container, signal
        triggers.append(entry)
    # end for
    return triggers


def parse_signal(signal: str) -> Signals:
    """
    string to signal
    """
    try:
        signal = Signals[signal.upper()]  # lookup by name
    except KeyError:
        signal = int(signal)  # try lookup as int
        signal = Signals(signal)  # lookup given int
    # end if
    return signal


# end def


def trigger_containers(
    client: docker.DockerClient,
    containers: List[Tuple[str, Signals]] = (('nginx', Signals.SIGHUP),)
):
    """
    Sends a specified signal to a specified container.
    Or more of those.
    :type client: docker.DockerClient
    :type containers: List[Tuple[str, Union[int, str]]]
    :return:
    """
    logger.info('I FEEL SO TRIGGERED!!!!11111ELEVEN11')
    # https://github.com/jwilder/docker-gen/blob/d25795eae43782e31dc532937634ed78dc0ea382/generator.go#L332-L341
    for container, signal in containers:
        logger.info(f"Sending container {container!r} signal {signal!r}...")
        c: Container = client.containers.get(container)
        try:
            c.kill(signal=signal)
        except APIError as e:
            if (
                e.status_code == 409  # conflict
                and "not running" in str(e)
            ):
                logger.info(f'Couldn\'t send signal to container, not running: {c.id}')
            else:
                logger.warn(f'Couldn\'t send signal to container {c.id}: {e}')
            # end if
    # end for
# end def
