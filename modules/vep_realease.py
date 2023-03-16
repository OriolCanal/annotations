import requests
from annotations_yaml import Yaml_file, Yaml_dict
import subprocess
import docker 
import json
from global_var import logger
from datetime import datetime
import re


class Vep_class:
    """
    Working with vep releases version to be updated in the pipeline

    Methods:
    --------
        extract_vep_version_pipeline(yaml_dict): 
            extract the vep version of the pipeline from the yaml file.
        extract_vep_version_realease_github():
            extract the release version of the main branch of vep github
        docker_env_images():
            returns a list of the images of all vep versions installed in the machine
        get_env_versions():
            returns a list of vep images tags installed.
        extract_vep_version_dockerhub():
            returns the latest tag of vep in DockerHub
        compare_versions(release_version, pipeline_version):
            compare the version of the pipeline vs the latest docker vep release tag, if the latest vep docker release is bigger than the pipeline version it returns True.
        check_vep_requirements():
            Check that the requirements for installing vep are already installed. Raises value error if some requirement is not already installed.
        install_docker_vep_version(release_tag):
            Pulls the vep docker image given as a release tag
        uninstall_previous_docker_image(image_tag):
            Uninstall the vep docker image given its tag as input
    """

    def __init__(self):
        self.vep_repo = "ensemblorg/ensembl-vep"

    def extract_vep_version_pipeline(self, yaml_dict: dict) -> float:
        """
        extract the vep version of the pipeline from the yaml file.

        Parameter:
            yaml_dict = dictionary of the yaml resources file
            
        return:
            version(float): Version of vep used by the pipeline
        """
        version = float(yaml_dict["vep"]["version"])
        return (version)

    def extract_vep_version_release_github(self) -> float: 
        """
        extracte the latest version of vep in github. It extractes it by reading the name of the main branch 
        of the github page of vep: https://github.com/Ensembl/ensembl-vep
        
        Returns:
            release_version(float): the main branch release version of vep in github
        """
        # Github repository of vep
        REPO_URL = "https://github.com/Ensembl/ensembl-vep"
        
        # Extract owner and repository
        owner, repo_name = REPO_URL.split("/")[-2:]

        # Construct the API endpoint URL for getting the default branch
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}"

        try:
            # Make a GET request to the API endpoint
            response = requests.get(api_url)
        
        except:
            raise ValueError(f"{api_url} was not accessible")

        # Get the default branch of the repository from the response
        default_branch = response.json()["default_branch"]

        # The branch name is in format: Release/109 for example
        release_version = float(default_branch.split("/")[1])
        
        return (release_version)
    

    def docker_env_images(self) -> list:
        """
        returns the different vep images docker tags that you have installed
        
        Returns:
            tags(list): List of docker images tags that you have installed
        """
        
        client = docker.from_env()

        # list all the tags from the vep docker repository
        image_list = client.images.list(name=self.vep_repo)

        # order the tags (newest first)
        logger.info(f"You have the following version of vep docker with the following images objects {image_list}")
        return(image_list)
        
    
    def get_env_versions(self) -> list:
        """
        get the versions of vep docker images installed
        
        Retrun:
            images_versions: list strings indicating the image version. It also can contain latest"""
        
        images_versions = []
        docker_env_images = self.docker_env_images()
        for image_obj in docker_env_images:
            # accessing the tag of the image object
            image_obj = image_obj.tags[0]
            match = re.search(r"release_\d+\.\d+",image_obj)
            if match:
                image_version = match.group()
            elif match is None:
                index = image_obj.rfind("latest")
                if index != -1:
                    image_version = "latest"
            else:
                logger.critical(f"It has not been possible to obtain a float or latest from docker image: {image_obj}")
                raise ValueError(f"It has not been possible to obtain a float or latest from docker image: {image_obj}")
            images_versions.append(image_version)
        
        return(images_versions)


    def extract_vep_version_dockerhub(self):
        """
        extract the latest version and tag of vep DockerHub
        Returns: 
            latest_tag(str): latest tag of vep docker image
            version(float): version of the latest tag
        """
        response = requests.get(f"https://hub.docker.com/v2/repositories/{self.vep_repo}/tags/?page_size=100")
        response.raise_for_status()

                
        # Parse the response JSON
        response_json = json.loads(response.text)

        # Extract the latest tag name and version number
        latest_tag = response_json['results'][1]['name']
        print (latest_tag)
        version = float(latest_tag.split('_')[1])

        logger.info(f"The latest version of vep in dockerhub is {version}")

        # Print the results
        return (latest_tag, version)
    

    def compare_versions(self, release_version, pipeline_version):
        """
        compare the version of the pipeline vs the latest docker vep release tag,
        if the latest vep docker release is bigger than the pipeline version it returns True.
        
        Parameters: 
            release_version(float): Version of the latest docker vep image
            pipeline_version(float): Pipeline version extracte from yaml.

        Returns:
            True(bol) if the realease version > pipeline version
            False(bol) if the release version !> pipeline version
        """

        #transform the versions to floats:
        if float(release_version) > float(pipeline_version):
            logger.critical(f"We are not using the latest version of vep: \
            \nenvironment image v.: {pipeline_version} \nDockerHub image v.: {release_version}")
            return(True)
        else:
            logger.info(f"You are using the latest version of vep that can be found in DockerHub")
            return(False)

    

    def check_vep_requirements(self):
        """
        Check that the requirements for installing vep are already installed. 
        Raises value error if some requirement is not already installed.
        
        Returns:
            0 if all the requirements are already installed
        """

        vep_requirements = ["wget", "perl", "gcc", "g++", "make"]
        perl_libraries = "-MArchive::Zip", "-MDBI" 

        for vep_requirement in vep_requirements:
            if subprocess.run(["which", vep_requirement]).returncode != 0:
                raise ValueError(f"Install {vep_requirement} before trying to install a new version of vep!")
            
        for perl_library in perl_libraries:
            if subprocess.run(["perl", perl_library, "-e", "1"]).returncode != 0:
                raise ValueError(f"Install the perl library {perl_library} before trying to install a new version of vep!")

        return(0)
    

    def install_docker_vep_version(self, release_tag):
        """
        Pulls the vep docker image given as a release tag
        
        Parameters:
            realease_tag: Tag of the version that wanted to be installed. e.g. release_109.3  

        Returns:
            0 : If the docker image has been pulled successfully
            ValueError: Failed to download the docker image
        """

        client = docker.from_env()

        image_name = "ensemblorg/ensembl-vep"
        
        # Pull the image from the Docker hub
        client.images.pull(image_name, release_tag)

        # verify that the image has been downloaded 
        if client.images.get(f"{image_name}:{release_tag}"):
            logger.info(f"a new image of docker will be pulled: {release_tag}")
            return(0)
        else:
            logger.critical(f"Error: Failed to download {image_name}:{release_tag}")
            raise(ValueError(f"Error: Failed to download {image_name}:{release_tag}"))

    
    def uninstall_previous_docker_image(self, image_tag):
        """
        Uninstall the vep docker image given its tag as input
        
        Parameters: image_tag(str): image tag of the vep image that wants to be uninstalled
        
        Returns:
            0: unisntallation have been performed correctly
            1: Failed to uninstall vep image
        """

        image_name = "ensemblorg/ensembl-vep"

        # Stop and remove running containers that are using the Vep image
        cmd = f"docker ps -a | grep {image_name}:{image_tag} | awk '{{print $1}}' | xargs docker stop | xargs docker rm"
        subprocess.run(cmd, shell=True)

        cmd2 = f"docker image rm {image_name}:{image_tag}"
        result = subprocess.run(cmd2, shell=True)
        print(result)
        if not result.returncode == 0:
            # Verify that the VEP image with the specified tag no longer exists
            result = subprocess.run(["docker images", "-q", f"{image_name}:{image_tag}"])
            print (f"resutl: {result}")
            if not result.stdout:
                logger.info(f"VEP image with tag {image_tag} have been unistalled successfully.")
                return (0)
            else:
                logger.critical(f"VEP image with tag {image_tag} still exists.")
                return(1)
        else:
            return(0)
        

test_yaml_file = "/home/ocanal/Desktop/annotations/annotation_resources.yaml"
yaml_file_class = Yaml_file(test_yaml_file)
yaml_dict = yaml_file_class.parse_yaml()
vep_class = Vep_class()
pipeline_version = vep_class.extract_vep_version_pipeline(yaml_dict)
version_realease= vep_class.extract_vep_version_release_github()
docker_release, docker_version  = vep_class.extract_vep_version_dockerhub()
print (f"{docker_version = }")
print (f"{version_realease = }")
print (f"{type(pipeline_version) = }")

vep_class.install_docker_vep_version(docker_release)