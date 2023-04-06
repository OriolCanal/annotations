from ..modules import clinvar
from ..modules import global_var
import os
import requests
import urllib.request
from datetime import date
import vcf
import re

clinvar_class = clinvar.Clinvar()


def test_get_latest_weekly_date():
    last_release_date = clinvar_class.get_latest_weekly_date()
    today = date.today()
    print(today)
    date_str = int(today.strftime("%Y%m%d"))

    assert isinstance(last_release_date, int)

    # Checking that it has been less than 1 months since the last uploaded file
    # as a new file is released weekly 
    assert (last_release_date + 100) >= date_str, f"It has been more than 14 days since the last release of clinvar."


def test_latest_weekly_files():
    latest_clinvar_file, latest_tabix_file = clinvar_class.get_latest_weekly_files()
    response = requests.get(clinvar_class.weekly_release_url)
    html = response.content.decode("utf-8")
    assert latest_clinvar_file in html, f"The last release clinvar file: {latest_clinvar_file} has not been found in {clinvar_class.weekly_release_url}"
    assert latest_tabix_file in html, f"The last release tabix clinvar file: {latest_tabix_file} has not been found in {clinvar_class.weekly_release_url}"


clinvar_fields = [
    "AF_ESP",
    "AF_EXAC",
    "AF_TGP",
    "ALLELEID",
    "CLNDN",
    "CLNDNINCL",
    "CLNDISDB",
    "CLNDISDBINCL",
    "CLNHGVS",
    "CLNREVSTAT",
    "CLNSIG",
    "CLNSIGCONF",
    "CLNSIGINCL",
    "CLNVC",
    "CLNVCSO",
    "CLNVI",
    "DBVARID",
    "GENEINFO",
    "MC",
    "ORIGIN",
    "RS",
    "SSR"
] 

clinvar_full_path = ""
def test_download_latest_version():
    global clinvar_full_path
    clinvar_full_path, tabix_full_path = clinvar_class.download_latest_version()
    clinvar_file = os.path.basename(clinvar_full_path)
    tabix_file = os.path.basename(tabix_full_path)

    # Testing that the downloaded file is in the correct nomenclature
    pattern = r"clinvar_(\d+)\.vcf\.gz"
    match = re.search(pattern, clinvar_file)
    assert match is not None, f"pattern : {pattern} is not found in clinvar file {clinvar_file}. Check the clinvar file nomenclature!"
    date_str = str(match.group(1))
    assert len(date_str) == 8, f"Date of the file {clinvar_file} has not 8 digits and is not in date format"

    assert os.path.isfile(clinvar_full_path), f"The last clinvar file has not been downloaded: {clinvar_full_path}"
    assert os.path.isfile(tabix_full_path), f"the last clinvar tabix file has not been downloaded: {tabix_full_path}"

    clinvar_url = f"{clinvar_class.weekly_release_url}{clinvar_file}"
    tabix_url = f"{clinvar_class.weekly_release_url}{tabix_file}"

    # Retrieve expected file size
    response = urllib.request.urlopen(clinvar_url)
    tabix_response = urllib.request.urlopen(tabix_url)
    expected_clinvar_size = int(response.headers["Content-Length"])
    expected_tabix_size = int(tabix_response.headers["Content-Length"])

    assert os.path.getsize(clinvar_full_path) == expected_clinvar_size, f"The downloaded clinvar file has not the expected size:\nExpected size: {expected_clinvar_size}"
    assert os.path.getsize(tabix_full_path) == expected_tabix_size, f"The downloaded tabix file has not the expected size:\nExpected size: {expected_tabix_size}"

    vcf_reader = vcf.Reader(filename=clinvar_full_path.encode(), compressed=True)
    info_fields = vcf_reader.infos

    for field in info_fields:
        assert field in clinvar_fields, f"{field} not found in the clinvar fields predeterminated list. Be aware, it seems that clinvar has change its format!"


def test_get_hg19_latest_downloaded_file():
    # testing that all the files stored in the clinvar folder are vcf or tabix files
    ann_dir = global_var.annotations_dir
    clinvar_dir = os.path.join(ann_dir, "clinvar", "hg19")
    pattern = r"clinvar_(\d+)\.vcf\.gz"
    for clinvar_file in os.listdir(clinvar_dir):
        assert clinvar_file.endswith(".vcf.gz") or clinvar_file.endswith(".tbi"), f"Clinvar file must end either with .vcf.gz or tbi. Detected file {clinvar_file} "
        if clinvar_file.endswith(".vcf.gz"):
            match = re.search(pattern, clinvar_file)
            assert match is not None, f"pattern : {pattern} is not found in clinvar file {clinvar_file}. Check the clinvar file nomenclature!"
            date_str = str(match.group(1))
            assert len(date_str) == 8, f"Date of the file {clinvar_file} has not 8 digits and is not in date format"

    last_clinvar_path = clinvar_class.get_hg19_latest_downloaded_file()

    assert os.path.isfile(last_clinvar_path), f"Clinvar file {last_clinvar_path} not detected"
    tabix_file = f"{last_clinvar_path}.tbi"
    assert os.path.isfile(tabix_file), f"Clinvar file {last_clinvar_path} has not its tabix file on the clinvar folder." 


def test_trial_vep_clinvar():
    
    global clinvar_full_path
    clinvar_file = os.path.basename(clinvar_full_path)
    vep_output = clinvar_class.trial_vep_clinvar(clinvar_file)
    assert os.path.isfile(vep_output)

    vcf_reader = vcf.Reader(filename=vep_output)
    info_fields = vcf_reader.infos
    clinvar_info_fields = [clinvar_field for clinvar_field in info_fields if "ClinVar" in clinvar_field]
    print(clinvar_info_fields)
    # The info fields in the annotated file are in format Clinvar_ID
    new_clinvar_list = [f"ClinVar_{clinvar_field}" for clinvar_field in clinvar_fields]
    # and a new clinvar field is also included. This field describes the location of the clinvar file used.
    new_clinvar_list.append("ClinVar")
    print(f"new_clinvar_list = {new_clinvar_list}")

    for field in new_clinvar_list:
        assert field in clinvar_info_fields, f"{field} is not found in the predeterminated Clinvar fields list. Be aware, it seems that clinvar have been updated with a new field"







