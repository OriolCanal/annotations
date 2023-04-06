import sys              
from packaging import version
sys.path.append("/home/ocanal/Desktop/pipeline/GC_NGS_PIPELINE/annotations/modules")
from modules.annotations_yaml import Yaml_file, Yaml_dict
from modules.vep_realease import Vep_class
from modules.global_var import logging, yaml_pipeline
from modules.cadd import CADD
from modules.clinvar import Clinvar
from modules.splice_ai import SpliceAI
from modules.civic import Civic
from modules.dbNSFP import DbNSFP
from modules.gnomad import Gnomad
import os




# Yaml dict class
Yaml_class = Yaml_file(yaml_pipeline)
initial_yaml_dict = Yaml_class.parse_yaml()
Yaml_dict_class = Yaml_dict(initial_yaml_dict)
print(f"type initial yaml dict : {type(initial_yaml_dict)}")


clinvar_class = Clinvar()
current_clinvar_version = int(Yaml_dict_class.get_database_version("clinvar"))
last_release_version = int(clinvar_class.get_latest_weekly_date())
if last_release_version > current_clinvar_version:
    clinvar_class.download_latest_version()
    clinvar_latest_file, clinvar_tabix_file = clinvar_class.get_latest_weekly_files()
    logging.info(f"Downloading the latest version of Clinvar: {last_release_version}")
    Yaml_dict_class.substitute_yaml_value("clinvar", "version", last_release_version)
    Yaml_dict_class.substitute_yaml_value("clinvar", "hg19", f"hg19/{clinvar_latest_file}")
else:
    logging.info(f"You already have the latest version of clinvar downloaded, actual version: {current_clinvar_version}\n \
                last released version : {last_release_version}")

end_yaml_dict = Yaml_dict_class.get_yaml_dict()
# print(f"yaml dict class.initial_dict: {Yaml_dict_class.initial_dict}")
# print(f"end_yaml_dict: {end_yaml_dict}")
if Yaml_dict_class.compare_dict_changes():
    Yaml_dict_class.dict_to_yaml()
    logging.info(f"The yaml file has been modified and a new version: {Yaml_dict_class.new_version} will be created")
