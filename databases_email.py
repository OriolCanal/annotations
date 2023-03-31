import sys              
from packaging import version
sys.path.append("/home/ocanal/Desktop/annotations/modules")
from modules.annotations_yaml import Yaml_file, Yaml_dict
from modules.vep_realease import Vep_class
from modules.global_var import logging, yaml_file, args, annotations_dir, get_y_n_from_user
from modules.cadd import CADD
from modules.clinvar import Clinvar
from modules.splice_ai import SpliceAI
from modules.civic import Civic
from modules.dbNSFP import DbNSFP
from modules.gnomad import Gnomad
from modules.emailing import send_email
import os


databases_release = {}

# Yaml dict class

Yaml_class = Yaml_file(yaml_file)
initial_yaml_dict = Yaml_class.parse_yaml()
Yaml_dict_class = Yaml_dict(initial_yaml_dict)
print(f"type initial yaml dict: {type(initial_yaml_dict)}")




# VARIANT EFFECT PRDICTOR (VEP)

vep_class = Vep_class()

# extracting pipeline version from yaml file
pipeline_version = vep_class.extract_vep_version_pipeline(initial_yaml_dict)
# extracting release version of vep from github branch name
github_realease_version = vep_class.extract_vep_version_release_github()
dockerhub_release_tag, dockerhub_release_version = vep_class.extract_vep_version_dockerhub()
docker_env_versions = vep_class.get_env_versions()
# comparing versions. If vep version > pipeline version, new version = True. Otherwise, new_version = False
new_version = vep_class.compare_versions(dockerhub_release_version, pipeline_version)
if new_version:
    databases_release["vep"] = f"There is a new version of vep:\n\
        actual pipeline version: {pipeline_version}\n\
        last release version: {dockerhub_release_version}"
else:
    databases_release["vep"] = f"The pipeline is using the last release of vep:\n\
        actual vep pipeline version: {pipeline_version}\n\
        last vep release version: {dockerhub_release_version}"


# gnomAD

gnomad_class = Gnomad()
gnomad_pipeline_version = Yaml_dict_class.get_database_version("gnomad")
gnomad_last_v = gnomad_class.get_last_release()
if version.parse(str(gnomad_last_v)) > version.parse(str(gnomad_pipeline_version)):
    gnomad_msg = f" A new version of gnomAD is available:\n\
        gnomAD pipelinve version = {gnomad_pipeline_version}\n\
        gnomAD last release version = {gnomad_last_v}\n\
        If you want to install the latest version of gnomad go to the following URL: https://gnomad.broadinstitute.org/downloads/"
    logging.info(gnomad_msg)
    databases_release["gnomAD"] = gnomad_msg
else:
    gnomad_msg = f"The pipeline is using the last release of gnomAD:\n\
        actual gnomAD pipeline version = {gnomad_pipeline_version}\n\
        gnomAD las release version = {gnomad_last_v}"
    logging.info(gnomad_msg)
    databases_release["gnomAD"] = gnomad_msg


# CADD

cadd_class = CADD()
CADD_pipeline_version = cadd_class.get_pipeline_version(initial_yaml_dict)
last_CADD_released_version = cadd_class.get_last_version()
if last_CADD_released_version > CADD_pipeline_version:
    databases_release["CADD"] =f"There is a new version of the CADD database:\n\
        pipeline CADD version = {CADD_pipeline_version}\n\
        last release CADD version = {last_CADD_released_version}\n\
        If you want to download the latest version of CADD go to this URL: https://cadd.gs.washington.edu/download"
else:
    msg = f"You already have the latest version of CADD database, \n\
        actual pipeline version: {CADD_pipeline_version}\n \
        last realeased version: {last_CADD_released_version}"
    logging.info(msg)
    databases_release["CADD"] = msg


# dbNSFP

dbnsfp_class = DbNSFP()
last_dbnsfp_version = dbnsfp_class.get_dbnsfp_last_release()
dbnsfp_pipeline_version = Yaml_dict_class.get_database_version("dbnsfp")
if version.parse(str(last_dbnsfp_version)) > version.parse(str(dbnsfp_pipeline_version)):
    dbnsfp_msg = f"A new version of dbNSFP is available:\n\
        dbNSFP pipeline version = {dbnsfp_pipeline_version}\n\
        dbNSFP last release = {last_dbnsfp_version}\n\
        If you want to download the latest version of dbNSFP go to this url: https://sites.google.com/site/jpopgen/dbNSFP?pli=1"
    logging.info(dbnsfp_msg)
    databases_release["dbNSFP"] = dbnsfp_msg
else:
    dbnsfp_msg = f"The pipeline is using the last dbNSFP release:\n\
        pipeline dbNSFP version = {dbnsfp_pipeline_version}\n\
        last dbNSFP version = {last_dbnsfp_version}"


# SpliceAI

spliceai_class = SpliceAI()
current_spliceai_v = spliceai_class.get_last_version()
pipeline_snv_v = Yaml_dict_class.get_database_version("spliceai_snv")
pipeline_indel_v = Yaml_dict_class.get_database_version("spliceai_indel")
if (version.parse(str(current_spliceai_v)) > version.parse(str(pipeline_snv_v))) or version.parse(str(current_spliceai_v)) > version.parse(str(pipeline_indel_v)):
    spliceai_msg = f"A new version of Splice AI has been released:\n\
        actual spliceAI pipeline version: {pipeline_snv_v}\n\
        last spliceAI release version: {current_spliceai_v}\n\
        If you want to download the latest version of SpliceAI go to this url: https://basespace.illumina.com/projects/66029966"
    logging.info(spliceai_msg)
    databases_release["spliceAI"] = spliceai_msg
else:
    databases_release["spliceAI"] = f"The pipeline is using the last version of SpliceAI:\n\
                                    pipeline SpliceAI version: {pipeline_snv_v}\n\
                                    last SpliceAI version: {current_spliceai_v}"

databases_release["IMPORTANT_INFORMATION"] = "If you download a new version of any database, please REMEMBER TO UPDATE THE annotations_resources.yaml FILE"

# EMAIL MESSAGE
whole_email_msg = ""
for key, item in databases_release.items():
    if key == "IMPORTANT_INFORMATION":
        whole_email_msg += f"\n {key} \n{item}\n\n\n"
    else:
        whole_email_msg += f"\n DATABASE: {key} \n{item}\n\n\n"

print(f"whole email msg {whole_email_msg}")

send_email("oriolcanal1998@gmail.com", "DATABASE RELEASES", whole_email_msg)
