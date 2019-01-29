# -*- coding: utf-8 -*-
import re

from docker import errors as docker_errors
from html import escape
from DictObject import DictObject
from luckydonaldUtils.logger import logging
from luckydonaldUtils.encoding import to_native as n

from .jinja2_utils import get_template
from .docker_utils import get_current_container_id
from .docker_utils.env import extract_container_envs
from .classes import DockerInfo
from .watcher import Watcher

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)


DEFAULT_HOST="example.com"
INPUT_FILENAME = "nginx.conf.template"
OUTPUT_FILENAME = "/output/nginx.conf"


class Status(object):
    def __init__(self, key, text, emoji):
        self.key = key
        self.text = text
        self.emoji = emoji
    # end def
# end class


VAR_REPLACEMENT_REGEX = re.compile('§{(?P<var>[A-Z_][A-Z0-9_]*)}')
""" basically `§{VARNAME}` """

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
    logger.info("listening to the events: {!r}".format(TRIGGER_EVENTS))

    # get previous config file, to see if we need to trigger a nginx reload.
    old_file = None
    try:
        with open(OUTPUT_FILENAME, 'r') as f:
            old_file = n(f.read())
        # end with
    except OSError:
        logger.info("Not yet existent (or not readable): /data/nginx.conf")
    # end if

    # prepare template
    template = get_template(INPUT_FILENAME)

    # prepare docker
    filters = {"event": TRIGGER_EVENTS}
    w = Watcher(filters=filters)
    client = w.client

    docker_version = client.version()

    inspect_and_template(client, docker_version, old_file, template)

    # listen to incomming events
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

        more_data = DictObject.objectify(client.api.inspect_container(container_id))

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
        message = "{emoji} Container {container}: {image} {text}".format(
            image=" ({})".format(image) if image else "",
            emoji=status.emoji, container=container,
            text=status.text,
        )
        logger.success(message)

        # now
        # containers

        did_change, old_file = inspect_and_template(client, docker_version, old_file, template, )
    # end for
# end def


def inspect_and_template(client, docker_version, old_file, template):
    containers = []
    # retry listing until it succeeds
    list_exception = False
    while list_exception is not None:
        try:
            containers = client.containers.list(all=True, sparse=False)
            list_exception = None
        except docker_errors.NotFound as e:  # probably a container which died just the right moment.
            list_exception = e
            logger.warn("Exception occured when listing, retrying...", exc_info=True)
        # end try
    # end while
    instances_by_name = {}
    for container in containers:
        if all(label in container.labels for label in (
            'com.docker.compose.project',
            'com.docker.compose.service',
            'com.docker.compose.container-number'
        )):
            service_name = container.labels['com.docker.compose.project'] + "_" \
                           + container.labels['com.docker.compose.service']  # + "_" \
            # + ['com.docker.compose.container-number']
            service_name_short = container.labels['com.docker.compose.service']
        else:
            service_name = container.name
            service_name_short = service_name
        # end if

        container_environment_vars = extract_container_envs(container)

        def env_replace_func(match):
            """
            Used in :py:`get_label` as function to resolve the `§{VARNAME}` replacements.
            See the regex :py:`VAR_REPLACEMENT_REGEX` above.
            :param match:
            :return:
            """
            var = match.group('var')
            return container_environment_vars[var]
        # end def

        def get_label(
            name, default,
            valid_values=None,
            replace_variables_label=True, replace_variables_default=False, replace_variables=None,
        ):
            """
            Gets a label from the container label section.
            Optionally allows to pull in environment variables of the form `§{VARNAME}`.

            :param name: name of the label
            :type  name: str

            :param default: The default value, if label was not found
            :type  default: str

            :param valid_values: A list of valid values
            :type  valid_values: List[str]

            :param replace_variables_label: If we should replace `§{VARNAME}` environment variables in the loaded label value.
            :type  replace_variables_label: bool

            :param replace_variables_default: If we should replace `§{VARNAME}` environment variables in the fallback default value.
            :type  replace_variables_default: bool

            :param replace_variables: If we should replace `§{VARNAME}` environment variables
                                      in the loaded label value and fallback default value.
                                      This overwrites the settings of `replace_variables_label` and `replace_variables_default`.
                                      Default: No action (`None`)
            :type  replace_variables_label: None|bool

            :return:
            """
            if isinstance(replace_variables, bool):
                replace_variables_label = replace_variables
                replace_variables_default = replace_variables
            # end if
            label = container.labels.get(name, None)
            # TODO: https://stackoverflow.com/a/11819111/3423324#match-character-which-is-not-escaped
            if label is None:
                # use default
                label = default
                if replace_variables_default:
                    label = VAR_REPLACEMENT_REGEX.sub(env_replace_func, label)
                # end if
            elif replace_variables_label:
                label = VAR_REPLACEMENT_REGEX.sub(env_replace_func, label)
            # end if
            if valid_values is not None and label not in valid_values:
                raise AssertionError(f'Invalid value for label {name}: Got {label!r}, allowed are {valid_values!r}')
            # end if
            return label
        # end def

        if get_label('auto_proxy.enable', '0', replace_variables=False) != '1':
            logger.debug(f'skipping wrong container: {container.id} {service_name}')
            continue
        # end if

        hosts = container.labels.get('auto-proxy.host', DEFAULT_HOST).split(",")

        service_data = {
            "name": service_name,
            "short_name": service_name_short,
            "mount_point": get_label('auto_proxy.mount_point', f"/{service_name_short}"),
            "hosts": hosts,
            "access": get_label('auto_proxy.access', "net", valid_values=['net', 'socket']),
            "protocol": get_label('auto_proxy.protocol', "http", valid_values=['http', 'uwsgi']),
            "port": int(get_label('auto_proxy.port', "80")),
            "environment": container_environment_vars,
        }
        instance_data = {
            "id": container.id,
            "name": container.name,
        }
        if service_name not in instances_by_name:
            instance = {
                "scaled_instances": [instance_data]
            }
            instance.update(service_data)
            instances_by_name[service_name] = instance
        else:
            instance = instances_by_name[service_name]
            for k, v in service_data.items():
                if instance[k] != v:
                    raise AssertionError("instance[k] != v", k, service_data, instance)
                # end if
            # end for
            instance['scaled_instances'].append(instance_data)
        # end if
    # end for
    services_by_host = {}
    logger.success(f"instances_by_name: {instances_by_name}")
    for instance in instances_by_name.values():
        logger.success(f"instance: {instance}")
        for host in instance['hosts']:
            if host not in services_by_host:
                services_by_host[host] = []
            # end if
            services_by_host[host].append(instance)
        # end for
    # end for
    did_change, old_file = run_templating(
        client, docker_version, old_file, template,
        services_by_host=services_by_host,
        services_by_name=instances_by_name,
        services=instances_by_name.values(),
    )
    return did_change, old_file
# end def


def run_templating(
    client, docker_version, old_file, template,
    services, services_by_host, services_by_name,
):
    d = client.info()
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

    new_file = template.render(
        docker=docker,
        services=services,
        services_by_host=services_by_host,
        services_by_name=services_by_name
    )
    if new_file != old_file:
        with open(OUTPUT_FILENAME, 'w') as f:
            f.write(new_file)
        # end with
        print('I AM SO TRIGGERED!!!!11111ELEVEN11')

        # old_file = new_file
        return True, new_file
    # end if
    return False, old_file
# end main



if __name__ == '__main__':
    logging.add_colored_handler("root", level=logging.DEBUG)
    main()
# end if
