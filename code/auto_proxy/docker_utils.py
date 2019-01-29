import re
CONTAINER_CGROUP_REGEX = re.compile('^\d+:\w+:/docker[/-](?P<hash>[a-z0-9]{64})(\\.scope)?$')
# 10:blkio:/docker/852314f36fe2bf5f57d68dfd9e5a6370ba3974ef708b43bf8cec1d1393d548b1
# 9:cpuset:/docker/852314f36fe2bf5f57d68dfd9e5a6370ba3974ef708b43bf8cec1d1393d548b1


def get_current_container_id():
    with open("/proc/self/cgroup") as f:
        for line in f:
            m = CONTAINER_CGROUP_REGEX.match(line)
            if m:
                return m.group("hash")
        # end for
    # end with
    return None
# end def
