import requests
import urllib.request
from global_var import logger, annotations_dir
import os
import re
from errors import FileAlreadyExists



class Clinvar:
    ncbi_url =  "https://ftp.ncbi.nlm.nih.gov/"
    weekly_release_url = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/weekly/"
    clinvar_annotations_dir = f"{annotations_dir}/clinvar"
    
    
    def __init__(self):
        if not os.path.exists(self.clinvar_annotations_dir):
            os.mkdir(self.clinvar_annotations_dir)


    def get_latest_weekly_date(self) -> int:
        """
        list of files from clinvar weekly directory for genome GRCh37
        
        Return:
            max(matches) : latest date that clinvar have made an update in https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/weekly/
        """ 
        response = requests.get(self.weekly_release_url)
        html = response.content.decode("utf-8")

        pattern = r"clinvar_(\d+).vcf.gz"
        matches = set(re.findall(pattern, html))

        if matches:
            matches = [int(match) for match in matches]
            latest_version_date = max(matches)
            return (latest_version_date)
        else:
            return (1)
        
    def get_latest_weekly_files(self) -> list:
        latest_date = self.get_latest_weekly_date()
        latest_clinvar_file = f"clinvar_{latest_date}.vcf.gz"
        latest_tabix_clinvar = f"{latest_clinvar_file}.tbi"
        return(latest_clinvar_file, latest_tabix_clinvar)


    def download_latest_version(self):
        clinvar_file, tabix_clinvar_file = self.get_latest_weekly_files()
        clinvar_url = f"https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/weekly/{clinvar_file}"
        tabix_url = f"https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/weekly/{tabix_clinvar_file}"

        # Retrieve expected file size
        response = urllib.request.urlopen(clinvar_url)
        tabix_response = urllib.request.urlopen(tabix_url)
        expected_clinvar_size = int(response.headers["Content-Length"])
        expected_tabix_size = int(tabix_response.headers["Content-Length"])
        
        clinvar_path = f"{self.clinvar_annotations_dir}/{clinvar_file}" 
        tabix_path = f"{self.clinvar_annotations_dir}/{tabix_clinvar_file}" 
        
        # Check if files already exists
        if os.path.isfile(clinvar_path):
            logger.critical(f"The file {clinvar_path} already exists, the file won't be downloaded to avoid replacement problems")
            raise(FileAlreadyExists(clinvar_path, f"You already have the file: {clinvar_path}, the file won't be downloaded to avoid replacement problems"))

        if os.path.isfile(tabix_path):
            logger.critical(f"The file {tabix_path} already exists, the file won't be downloaded to avoid replacement problems")
            raise(FileAlreadyExists(tabix_path, f"You already have the file: {tabix_path}, the file won't be downloaded to avoid replacement problems"))

        # Download the clinvar file and checking it has been dowloaded correctly
        urllib.request.urlretrieve(clinvar_file, clinvar_path)
        if os.path.exists(clinvar_path) and os.path.getsize(clinvar_path) == expected_clinvar_size:
            logger.info(f"The clinvar file {clinvar_path} have been downloaded correctly")
        else:
            logger.critical(f"Failed to download the clinvar file {clinvar_path}, the expected size of the file is {expected_clinvar_size} bytes \
                            and the size of the downloaded file is {os.path.getsize(clinvar_path)}")
        
        # Download the tabix clinvar file and checking it has been downloaded correctly
        urllib.request.urlretrieve(tabix_url, tabix_path)
        if os.path.exists(tabix_path) and os.path.getsize(tabix_path) == expected_clinvar_size:
            logger.info(f"The clinvar file {tabix_path} have been downloaded correctly")
        else:
            logger.critical(f"Failed to download the clinvar file {tabix_path}, the expected size of the file is {expected_clinvar_size} bytes \
                            and the size of the downloaded file is {os.path.getsize(tabix_path)}")
        
clinvar_class = Clinvar()
latest_date = clinvar_class.get_latest_weekly_date()
clinvar_class.download_latest_version()