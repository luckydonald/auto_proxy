# -*- coding: utf-8 -*-
import json
import iso8601

from html import escape
from DictObject import DictObject
from pytgbot.bot import Bot
from pytgbot.exceptions import TgApiServerException
from luckydonaldUtils.logger import logging
from docker.models.containers import Container

from .classes import DockerInfo
from .docker_utils import get_current_container_id
from .secrets import API_KEYS, TG_REPORT_CHAT
from .watcher import Watcher

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)


DEFAULT_HOST="example.com"


class Status(object):
    def __init__(self, key, text, emoji):
        self.key = key
        self.text = text
        self.emoji = emoji
    # end def
# end class


TRIGGER_EVENTS = ['die', 'stop', 'start']


HEALTH_STATUS = {"health_status: healthy": True, "health_status: unhealthy": False}
statussses = {
    Status("attach", "attached", "🔊"),
    Status("commit", "committed", "📦"),
    Status("copy", "copied", "📁"),
    Status("create", "created", "❇️"),
    Status("destroy", "destroyed", "💥"),
    Status("detach", "detached", "🔇"),
    Status("die", "died", "💀"),
    Status("exec_create", "exec created", "💟🆕"),
    Status("exec_detach", "exec detached", "💟💀"),
    Status("exec_start", "exec started", "💟▶️"),
    Status("export", "was exported", "📤"),
    Status("exit", "exited", "🅾️"),  # this is a variant of 'die', with exitCode == 0.
    Status("health_status: healthy", "is now healthy", "💚"),
    Status("health_status: unhealthy", "is unhealthy", "💔"),
    Status("import", "was imported", "📥"),
    Status("kill", "got killed", "🔫"),
    Status("oom", "got oom killed", "💣"),
    Status("rename", "renamed", "📝"),
    Status("resize", "resized", "↕️"),
    Status("restart", "restarted", "🔁"),
    Status("start", "started", "▶️"),
    Status("stop", "was stopped", "📴"),
    Status("top", "top", "🔝"),
    Status("pause", "paused", "⏸️"),
    Status("unpause", "top", "▶️"),
    Status("update", "top", "📨"),
    Status(None, " — we don't really know what it did?", "⚠️"),
}
NUMBERS = {
    "0": "0️⃣",
    "1": "1️⃣",
    "2": "2️⃣",
    "3": "3️⃣",
    "4": "4️⃣",
    "5": "5️⃣",
    "6": "6️⃣",
    "7": "7️⃣",
    "8": "8️⃣",
    "9": "9️⃣",
    True:  "💚",
    False: "💔",

}
STATUS = {s.key: s for s in statussses}


def main():
    logger.success("Will watch for status changes.")
    events_wanted = ["health_status", "created", "exited", "die", "start"]
    events_wanted += list(STATUS.keys())
    events_wanted = list(set(events_wanted))  # only one of each.
    events_wanted.remove("exec_create")
    events_wanted.remove("exec_start")
    logger.info("listening to the events: {!r}".format(events_wanted))

    old_file = None
    try:
        with open("/data/nginx.conf") as f:
            old_file = f.read()
        # end with
    except OSError:
        logger.info("Not yet existent (or not readable): /data/nginx.conf")
    # end if

    filters = {"event": TRIGGER_EVENTS}
    w = Watcher(filters=filters)

    docker_version = w.client.version()
    for event in w.run():
        logger.debug("New event:\n{!r}".format(event))
        if not hasattr(event, "status"):
            continue
        # end if

        # docker compose projects: only use service name, don't use image name.
        if 'com.docker.compose.service' in event.Actor.Attributes:
            container = event.Actor.Attributes['com.docker.compose.service']
            image = None
        else:
            container = event.Actor.Attributes['name']
            image = event.Actor.Attributes['image']
        # end if
        container_id = event.id

        more_data = DictObject.objectify(w.client.api.inspect_container(container_id))

        # getting the right STATUS
        if ":" in event.status:
            event_type, event_meta = tuple(event.status.split(":", maxsplit=1))
            event_type, event_meta = event_type.strip(), event_meta.strip()
        else:
            event_type = event.status.strip()
            event_meta = None
        # end if

        if (  # special case 'die' with exitCode == 0  --> 'exit'
            event.status == "die" and
            'exitCode' in event.Actor.Attributes and
            str(event.Actor.Attributes['exitCode']) == "0"
        ):
            status = STATUS["exit"]
        elif event.status in STATUS:
            status = STATUS[event.status]
        elif event_type in STATUS:
            status = STATUS[event_type]
        else:
            status = STATUS[None]
        # end def

        # make sure we don't get updates we don't want.
        if event.status not in TRIGGER_EVENTS:
            logger.debug("Skipping event {e!r} of container {c!r}.".format(e=event.status, c=container))
            continue
        # end if

        assert isinstance(status, Status)
        message = "{emoji} Container <code>{container}</code>{image} {text}".format(
            image=" (<code>{}</code>)".format(escape(image)) if image else "",
            emoji=escape(status.emoji), container=escape(container),
            text=escape(status.text),
        )

        d = w.client.info()
        docker = DockerInfo(
            name=d.get("Name"),
            container_count=d.get("Containers"),
            image_count=d.get("Images"),
            version=docker_version.get("Version"),
            api_version=docker_version.get("ApiVersion"),
            go_version=docker_version.get("GoVersion"),
            operating_system=docker_version.get("Os"),
            architecture=docker_version.get("Arch"),
            current_container_id=get_current_container_id(),
        )

        containers = w.client.containers.list(all=True)

        by_host = {}
        for container in containers:
            host = container.labels.get('auto-proxy.host', DEFAULT_HOST)
            if host not in by_host:
                by_host[host] = []
            # end if
            by_host[host].append(host)
        # end for

    # end for
# end main



if __name__ == '__main__':
    logging.add_colored_handler("root", level=logging.DEBUG)
    main()
# end if
