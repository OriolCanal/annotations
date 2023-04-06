import sys              
from packaging import version
import os
sys.path.append(os.path.abspath(__file__))
from modules.annotations_yaml import Yaml_file, Yaml_dict
from modules.vep_realease import Vep_class
from modules.global_var import logging, yaml_pipeline, args, annotations_dir, get_y_n_from_user
from modules.emailing import send_email
from modules.cadd import CADD
from modules.clinvar import Clinvar
from modules.splice_ai import SpliceAI
from modules.civic import Civic
from modules.dbNSFP import DbNSFP
from modules.gnomad import Gnomad



databases_release = {}

# Yaml dict class

Yaml_class = Yaml_file(yaml_pipeline)
initial_yaml_dict = Yaml_class.parse_yaml()
Yaml_dict_class = Yaml_dict(initial_yaml_dict)

# VARIANT EFFECT PRDICTOR (VEP)

if args.vep:
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
        vep_msg = f"There is a new version of vep:\n\
            actual pipeline version: {pipeline_version}\n\
            last release version: {dockerhub_release_version}"
        databases_release["vep"] = vep_msg
        logging.info(vep_msg)
        # asking to the user if new version should be downloaded 
        answer = get_y_n_from_user(f"Do you want to update the vep version from the current pipeline version: {pipeline_version} to the last version: {dockerhub_release_version}? (y/n)")
        if answer:
            logging.info(f"Downloading the Vep release tag: {dockerhub_release_tag}")
            # TO DO: CREATE A COMMAND LINE ARGUMENT THAT IF IT'S SPECIFIED, THE NEW VERSION IS INSTALLED AND SUBSTITUTED IN THE YAML FILE 
            vep_class.install_docker_vep_version(dockerhub_release_tag)
            logging.info(f"Changing the vep version in the yaml file")
            Yaml_dict_class.substitute_yaml_value("vep", "version", dockerhub_release_tag)
            # UNCOMMENT TO UNINSTALL VEP OLDER IMAGES
            # for env_version in docker_env_versions:
            #     if env_version != dockerhub_release_tag:
            #         logging.info(f"uninstalling the old vep image: {env_version}")
            #         vep_class.uninstall_previous_docker_image(env_version)
            #         logging.warning(f"The docker image of vep with tag {env_version} will be uninstalled")
    else:
        databases_release["vep"] = f"The pipeline is using the last release of vep:\n\
            actual vep pipeline version: {pipeline_version}\n\
            last vep release version: {dockerhub_release_version}"

# CADD

if args.CADD:
    cadd_class = CADD()
    CADD_pipeline_version = cadd_class.get_pipeline_version(initial_yaml_dict)
    last_CADD_released_version = cadd_class.get_last_version()
    if last_CADD_released_version > CADD_pipeline_version:
        databases_release["CADD"] =f"There is a new version of the CADD database:\n\
            pipeline CADD version = {CADD_pipeline_version}\n\
            last release CADD version = {last_CADD_released_version}"
        answer = get_y_n_from_user(f"Do you want to update the clinvar version from your current version: {CADD_pipeline_version} to the last version: {last_CADD_released_version}? (y/n)")
        if answer:
            cadd_class.download_version(last_CADD_released_version)
            # Editing the yaml dict with the new info
            Yaml_dict_class.substitute_yaml_value("cadd", "version", last_CADD_released_version)
            Yaml_dict_class.substitute_yaml_value("cadd", "hg19", f"hg19/{last_CADD_released_version}/{cadd_class.file_name}")
    else:
        msg = f"You already have the latest version of CADD database, \n\
                actual pipeline version: {CADD_pipeline_version}\n \
                last realeased version: {last_CADD_released_version}"
        logging.info(msg)
        databases_release["CADD"] = msg

# Clinvar

if args.clinvar:
    clinvar_class = Clinvar()
    current_clinvar_version = int(Yaml_dict_class.get_database_version("clinvar"))
    last_release_version = int(clinvar_class.get_latest_weekly_date())
    if last_release_version > current_clinvar_version:
        clinvar_msg = f"A new version of ClinVar is available:\n\
            ClinVar pipeline version : {current_clinvar_version}\n\
            ClinVar last released version: {last_release_version}\n"
        answer = get_y_n_from_user(f"Do you want to update the clinvar version from your current version: {current_clinvar_version} to the last version: {last_release_version}? (y/n)")
        if answer:
            logging.info(f"Downloading the latest version of Clinvar: {last_release_version}")
            clinvar_class.download_latest_version()
            clinvar_latest_file, clinvar_tabix_file = clinvar_class.get_latest_weekly_files()
            Yaml_dict_class.substitute_yaml_value("clinvar", "version", last_release_version)
            Yaml_dict_class.substitute_yaml_value("clinvar", "hg19", f"hg19/{clinvar_latest_file}")

        else:
            clinvar_msg += "\nYou can run this script with the following flags: --clinvar --force to update to the new version"
            logging.info(f"The clinvar files won't be actualized to the last released version {last_release_version}\
                You can run this script with the following flags: --clinvar --force to update to the new version")
    else:
        clinvar_msg = f"Pipeline ClinVar version is already the last released version:\n\
            Last ClinVar released version {last_release_version}\n\
            Pipeline ClinVar version: {current_clinvar_version}"
        logging.info(clinvar_msg)
    databases_release["ClinVar"] = clinvar_msg 


    
    # Trying if vep runs with the pipeline version
    # clinvar_file = Yaml_dict_class.get_database_file("clinvar")
    # clinvar_full_path_file = f"{annotations_dir}/{clinvar_file}"
    # clinvar_class.trial_vep_clinvar(clinvar_full_path_file)


# gnomAD

if args.gnomad:
    gnomad_class = Gnomad()
    gnomad_pipeline_version = Yaml_dict_class.get_database_version("gnomad")
    gnomad_last_v = gnomad_class.get_last_release()
    if version.parse(str(gnomad_last_v)) > version.parse(str(gnomad_pipeline_version)):
        gnomad_msg = f" A new version of gnomAD is available:\n\
            gnomAD pipelinve version = {gnomad_pipeline_version}\n\
            gnomAD last release version = {gnomad_last_v}\n\
            If you want to install the latest version of gnomad go to the following URL: https://gnomad.broadinstitute.org/downloads/"
        databases_release["gnomAD"] = gnomad_msg
    else:
        gnomad_msg = f"The pipeline is using the last release of gnomAD:\n\
            actual gnomAD pipeline version = {gnomad_pipeline_version}\n\
            gnomAD las release version = {gnomad_last_v}"
    logging.info(gnomad_msg)
    databases_release["gnomAD"] = gnomad_msg

# dbNSFP

if args.dbnsfp:
    dbnsfp_class = DbNSFP()
    last_dbnsfp_version = dbnsfp_class.get_dbnsfp_last_release()
    dbnsfp_pipeline_version = Yaml_dict_class.get_database_version("dbnsfp")
    if version.parse(str(last_dbnsfp_version)) > version.parse(str(dbnsfp_pipeline_version)):
        dbnsfp_msg = f"A new version of dbNSFP is available:\n\
                    dbNSFP pipeline version = {dbnsfp_pipeline_version}\n\
                    dbNSFP last release = {last_dbnsfp_version}"
        logging.info(dbnsfp_msg)
        databases_release["dbNSFP"] = dbnsfp_msg
    else:
        dbnsfp_msg = f"The pipeline is using the last dbNSFP release:\n\
                    pipeline dbNSFP version = {dbnsfp_pipeline_version}\n\
                    last dbNSFP version = {last_dbnsfp_version}"

# SpliceAI

if args.spliceai:
    spliceai_class = SpliceAI()
    current_spliceai_v = spliceai_class.get_last_version()
    pipeline_snv_v = Yaml_dict_class.get_database_version("spliceai_snv")
    pipeline_indel_v = Yaml_dict_class.get_database_version("spliceai_indel")
    if (version.parse(str(current_spliceai_v)) > version.parse(str(pipeline_snv_v)) or (version.parse(str(current_spliceai_v)) > version.parse(str(pipeline_indel_v)))):
        logging.info(f"A new release of SpliceAI snv version is available: v:{current_spliceai_v} \n\
                     If you want to download the new version go to this url: \n\
                     https://basespace.illumina.com/projects/66029966")
        databases_release["spliceAI"] = f"A new version of Splice AI has been released:\n\
            actual spliceAI pipeline version: {pipeline_snv_v}\n\
            last spliceAI release version: {current_spliceai_v}"
    else:
        databases_release["spliceAI"] = f"The pipeline is using the last version of SpliceAI:\n\
            pipeline SpliceAI version: {pipeline_snv_v}\n\
            last SpliceAI version: {current_spliceai_v}"
        
# CIVIC

if args.civic:
    civic_v = str(Yaml_dict_class.get_database_version("civic"))
    civic_dirname = Yaml_dict_class.get_database_dir("civic")
    civic_class = Civic()
    civic_yaml_path = f"{annotations_dir}/{civic_dirname}/{civic_v}"
    answer = get_y_n_from_user(f"Do you want to update the Civic version from your current version to the last version: nighlty file? (y/n)")
    if answer:
        civic_nightly_path = civic_class.download_nightly_file()
        nightly_v = os.path.basename(civic_nightly_path)
    # civic_is_different (bol) = True if nightly civic files and yaml civic files are different
    # civic_is_different (bol) = False if nightly civic files and yaml civic files are equal 
        civic_is_different = civic_class.compare_md5(civic_yaml_path, civic_nightly_path)
        if civic_is_different:
            Yaml_dict_class.substitute_yaml_value("civic", "version", nightly_v)
            logging.info(f"The nightly Civic file is different from the pipeline civic file. The new downloaded file will be set as the one to use by the pipeline.")
        else:
            logging.info(f"The nightly Civic file is the same as the one used by the pipeline. The downloaded file will be remove to avoid duplicates.")
            os.rmdir(civic_nightly_path)
    else:
        logging.info(f"We can't compare if there are differences between the nightly civic file and the pipeline Civic file if you don't accept to download the files.\
            If you want to check if they are different please run the script with the flags --civic --force")


# CREATING NEW YAML FILE

end_yaml_dict = Yaml_dict_class.get_yaml_dict()

if Yaml_dict_class.compare_dict_changes():
    Yaml_dict_class.dict_to_yaml()
    logging.info(f"The yaml file has been modified and a new version: {Yaml_dict_class.new_version} will be created")


# EMAIL MESSAGE
databases_release["IMPORTANT_INFORMATION"] = "If you download a new version of any database, please REMEMBER TO UPDATE THE annotations_resources.yaml FILE"
whole_email_msg = ""
for key, item in databases_release.items():
    if key == "IMPORTANT_INFORMATION":
        whole_email_msg += f"\n {key} \n{item}\n\n\n"
    else:
        whole_email_msg += f"\n DATABASE: {key} \n{item}\n\n\n"

logging.info(whole_email_msg)


if whole_email_msg != None:
    email_recievers = ["oriolcanal1998@gmail.com", "bioinformaticaudmmp@gmail.com"]
    if args.add_email:
        email_recievers.extend(args.add_email)
    for email in email_recievers:
        send_email(email, "ANNOTATIONS DATABASE NEW RELEASES", whole_email_msg)