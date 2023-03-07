import sys
import os
sys.path.append("/home/ocanal/Desktop/annotations/modules/")
from   modules.annotations_yaml import Yaml_dict, Yaml_file
from modules.vep_realease import Vep_class
import requests
import docker
import pytest
import subprocess

test_yaml_file = "/home/ocanal/Desktop/annotations/annotation_resources.yaml"
yaml_file_class = Yaml_file(test_yaml_file)
yaml_dict = yaml_file_class.parse_yaml()
vep_class_instance = Vep_class()

def test_extract_vep_version_pipeline():
    assert isinstance(yaml_dict, dict), "yaml_dict is not a dictionary"
    assert "vep" in yaml_dict, "vep does not exists in the yaml file"
    assert "version" in yaml_dict["vep"], "version of vep is not in the yaml file"
    print (f"yaml dict : {yaml_dict} ")
    version = vep_class_instance.extract_vep_version_pipeline(yaml_dict)

    assert isinstance(version, float), "pipeline version of vep is not a number"

def test_extract_vep_version_release_github():
    vep_github_url = "https://github.com/Ensembl/ensembl-vep"
    response = requests.get(vep_github_url)

    assert response.status_code == 200, f"{vep_github_url} does not exist or is not accessibel" 

    release_version = vep_class_instance.extract_vep_version_realease_github()

    assert isinstance(release_version, float), f"release version of vep is not a float number, check if the github branch of the url {vep_github_url} indicates the realease version"

# install docker vep versions to test the function:
image_name = "ensemblorg/ensembl-vep"
image_tags = ["release_109.3", "release_109.2", "release_106.1"]
image_full_names = ["ensemblorg/ensembl-vep:release_109.3", "ensemblorg/ensembl-vep:release_109.2", "ensemblorg/ensembl-vep:release_106.1"]

def test_install_docker_ver_version():
        
    # download 3 versions of docker to test that they are installed as docker images
    for image_tag in image_tags:
        vep_class_instance.install_docker_vep_version(image_tag)
    
    client = docker.from_env()
    for image_full_name in image_full_names:
        assert client.images.get(image_full_name), f"Image {image_full_name} have not been properly installed"

def test_docker_env_images():
    vep_images_installed = vep_class_instance.docker_env_images()
    assert len(vep_images_installed) >= 3, "You should have more than 3 versions of vep already installed by the testing script."
    for vep_image in vep_images_installed:
        assert vep_image.tags[0] in image_full_names, f"Vep image tag {vep_image.tags} should have been previously installed by the test and it's not detected."

def test_get_env_versions():
    vep_env_versions = vep_class_instance.get_env_versions()
    for image_tag in image_tags:
        assert image_tag in vep_env_versions


def test_extract_vep_version_dockerhub():
    latest_vep_tag, latest_vep_version = vep_class_instance.extract_vep_version_dockerhub()
    
    assert "release" in latest_vep_tag, f"latest_vep_tag is: {latest_vep_tag}: the word release is not in the tag. The format of the docker hub is expected to be release_version. Check if a latest version have been detected or if it has detected the release named latest as the output of the function."
    
    # To be sure that the latest version detected is not latest
    assert isinstance(latest_vep_version, float), f"latest version is: {latest_vep_version} and it is detected as not a digit"


def test_compare_versions():
    newer_version = vep_class_instance.compare_versions(vep_class_instance.extract_vep_version_dockerhub()[1], 
                                        vep_class_instance.extract_vep_version_pipeline(yaml_dict))
    
    assert isinstance(newer_version, bool)


def test_uninstall_previous_docker_image():
    for image_tag in image_tags:
        function_output = vep_class_instance.uninstall_previous_docker_image(image_tag)
        assert function_output == 0, f"the image tag {image_tag} have not been uninstalled correctly"
    for image_full_name in image_full_names:
        result = subprocess.run(["docker", "images", image_full_name], capture_output=True, text=True)
        print (f"result= {result}")
        assert result.stdout.strip(), f"the image {image_full_name}, has been found in docker images so it's not properly uninstalled"


