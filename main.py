import sys
sys.path.append("/home/ocanal/Desktop/annotations/modules")
from modules.annotations_yaml import Yaml_file, Yaml_dict
from modules.vep_realease import Vep_class
from modules.global_var import logger, yaml_file, args
from modules.cadd import CADD


################### Yaml dict ####################################


Yaml_class = Yaml_file(yaml_file)
yaml_dict = Yaml_class.parse_yaml()
Yaml_dict_class = Yaml_dict(yaml_dict)
vep_class = Vep_class()


#################### VARIANT EFFECT PRDICTOR (VEP) ##################
if args.vep:
    # extracting pipeline version from yaml file
    pipeline_version = vep_class.extract_vep_version_pipeline(yaml_dict)
    # extracting release version of vep from github branch name
    github_realease_version = vep_class.extract_vep_version_realease_github()
    dockerhub_release_tag, dockerhub_release_version = vep_class.extract_vep_version_dockerhub()
    docker_env_versions = vep_class.get_env_versions()
    # comparing versions. If vep version > pipeline version, new version = True. Otherwise, new_version = False
    new_version = vep_class.compare_versions(dockerhub_release_version, pipeline_version)
    if new_version == True:
        print(f"dockerhug release tag: {dockerhub_release_tag}")
        # TO DO: CREATE A COMMAND LINE ARGUMENT THAT IF IT'S SPECIFIED, THE NEW VERSION IS INSTALLED AND SUBSTITUTED IN THE YAML FILE 
        vep_class.install_docker_vep_version(dockerhub_release_tag)
        Yaml_dict_class.substitute_yaml_value("vep", "version", dockerhub_release_tag)
        # Add if command line argument is given, remove the version of the vep that are not used:
        for env_version in docker_env_versions:
                print(f"env version: {env_version} \n dockerhub release tag: {dockerhub_release_tag}")
                if env_version != dockerhub_release_tag:
                    print ("are not equal")
                    vep_class.uninstall_previous_docker_image(env_version)
                    logger.warning(f"The docker image of vep with tag {env_version} will be desinstalled")
        vep_class.install_docker_vep_version(dockerhub_release_version)


########################################### CADD #################################################################

if args.CADD:
    cadd_class = CADD()
    pipeline_version = cadd_class.get_pipeline_version(yaml_dict)
    last_CADD_released_version = cadd_class.get_last_version()
    if last_CADD_released_version > pipeline_version:
        cadd_class.download_version(last_CADD_released_version)
        # Editing the yaml dict with the new info
        Yaml_dict_class.substitute_yaml_value("cadd", "version", last_CADD_released_version)
        Yaml_dict_class.substitute_yaml_value("cadd", "hg19", f"hg19/{last_CADD_released_version}/{cadd_class.file_name}")


####################################### Clinvar ##################################################################

if args.clinvar:
     pass