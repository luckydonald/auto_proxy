class DockerInfo(object):
    def __init__(
        self, name, container_count, image_count, version, api_version, go_version,
        operating_system, architecture, current_container_id
    ):
        """

        :type name: string
        :type container_count: int
        :type image_count: int
        :type version: string
        :type api_version: string
        :type go_version: string
        :type operating_system: string
        :type architecture: string
        :type current_container_id: string
        """
        self.name = str(name)
        self.container_count = int(container_count)
        self.image_count = int(image_count)
        self.version = str(version)
        self.api_version = str(api_version)
        self.go_version = str(go_version)
        self.operating_system = str(operating_system)
        self.architecture = str(architecture)
        self.current_container_id = str(current_container_id)
