class DockerInfo(object):
    def __init__(
        self, name, container_count, image_count, version, api_version, go_version,
        operating_system, architecture, current_container_id, datetime, git_info,
    ):
        """

        :type name: str
        :type container_count: int
        :type image_count: int
        :type version: str
        :type api_version: str
        :type go_version: str
        :type operating_system: str
        :type architecture: str
        :type current_container_id: str
        :type datetime: datetime.datetime
        :type git_info: GitInfo
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
        self.datetime = datetime
        self.git_info = git_info
    # end def
# end class


class GitInfo(object):
    def __init__(
        self,
        commit_short, commit,
        dirty_project, dirty_global,
        message, author, date,
        head, branches, tags,
        modified_files, modified_files_str,
        version_str
    ):
        """

        :type commit_short: str
        :type commit: str
        :type dirty_project: bool
        :type dirty_global: bool
        :type message: str
        :type author: str
        :type date: str
        :type head: str|None
        :type branches: List[str]
        :type tags: List[str]
        :type modified_files: Dict[str, Union[List[str], Dict[str, str]]]
        :type modified_files_str: str
        :type version_str: str
        """
        self.commit_short = commit_short
        self.commit = commit
        self.dirty_project = dirty_project
        self.dirty_global = dirty_global
        self.message = message
        self.author = author
        self.date = date
        self.head = head
        self.branches = branches
        self.tags = tags
        self.modified_files = modified_files
        self.modified_files_str = modified_files_str
        self.version_str = version_str
    # end def

    @classmethod
    def from_gitinfo_values(cls):
        from luckydonaldUtils.tg_bots.gitinfo import GIT_COMMIT, GIT_COMMIT_SHORT, GIT_DIRTY_PROJECT, GIT_DIRTY_GLOBAL
        from luckydonaldUtils.tg_bots.gitinfo import GIT_MESSAGE, GIT_AUTHOR, GIT_DATE, GIT_HEAD, GIT_BRANCHES, GIT_TAGS
        from luckydonaldUtils.tg_bots.gitinfo import GIT_MODIFIED_FILES, GIT_MODIFIED_FILES_STR, VERSION_STR
        return cls(
            commit_short=GIT_COMMIT_SHORT,
            commit=GIT_COMMIT,
            dirty_project=GIT_DIRTY_PROJECT,
            dirty_global=GIT_DIRTY_GLOBAL,
            message=GIT_MESSAGE,
            author=GIT_AUTHOR,
            date=GIT_DATE,
            head=GIT_HEAD,
            branches=GIT_BRANCHES,
            tags=GIT_TAGS,
            modified_files=GIT_MODIFIED_FILES,
            modified_files_str=GIT_MODIFIED_FILES_STR,
            version_str=VERSION_STR
        )
