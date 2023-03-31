# from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
from global_var import logging, annotations_dir, get_y_n_from_user
from packaging import version
from github import Github
import os

github_token = os.environ.get("pwd_github")
class SpliceAI:


    spliceai_basespace_project_id = 94103939
    spliceai_path = f"{annotations_dir}/spliceAI/hg19/"
    cmd_download_project = f"./bs download project --id 66029966  -o {annotations_dir}/spliceAI/hg19/"
    github_tags_url = "https://github.com/Illumina/SpliceAI/"
    
    def get_released_versions(self) -> list:
        # response = requests.get(self.github_tags_url)
        # html = response.content.decode("utf-8")
        # print(html)
        g = Github(github_token)
        repo = g.get_repo("illumina/SpliceAI")
        tags = repo.get_tags()
        version_list = []
        for tag in tags:
            version = tag.name
            if version.startswith("v"):
                version = version.strip("v")
                version_list.append(version)

        return (version_list)
    
    def get_last_version(self) -> str:
        releases = self.get_released_versions()
        last_version = 0
        for release in releases:
            if version.parse(str(release)) > version.parse(str(last_version)):
                last_version = release
        logging.info(f"The last release for spliceAI is {last_version}")
        return (last_version)
    
    def download_last_version(self):
        get_y_n_from_user(f"BEFORE DOWNLOADING THE FILE:, check that the new version of spliceAI database has benn released in BaseSpace: check the files of the following project: \n \
                          https://basespace.illumina.com/analyses/ \n\
                          ")

if "__main__" == __name__:
    spliceai_class = SpliceAI()
    spliceai_class.get_last_version()
