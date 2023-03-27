import requests
import re
import urllib.request
from global_var import logging, annotations_dir
import os
from errors import FileAlreadyExists


class CADD:
    downloads_url = "https://cadd.gs.washington.edu/download"
    github_realeases_url = "https://github.com/kircherlab/CADD-scripts/releases"
    file_name = "whole_genome_SNVs.tsv.gz"
    cadd_annotations_dir = f"{annotations_dir}/CADD"

    def __init__(self):
        if not os.path.exists(self.cadd_annotations_dir):
            os.mkdir(self.cadd_annotations_dir)

    def get_pipeline_version(self, yaml_dict) -> float:
        return (float(yaml_dict["cadd"]["version"]))


    def get_CADD_released_versions(self) -> list:

        # URL for the CADD release page
        url = "https://cadd.gs.washington.edu/download"

        # Get the release page content
        response = requests.get(self.downloads_url)
        html = response.content.decode("utf-8")

        # Finding the pattern they are using to indicate the versions
        pattern = r"Developmental release: v(\d+\.\d+)"
        matches = re.findall(pattern, html)

        if matches:
            version_numbers = [float(match) for match in matches]
            print(f"There are the following CADD versions: {version_numbers}")
        else:
            logging.critical("No versions have been found in the CADD downloads webpage: https://cadd.gs.washington.edu/download \n \
                            The script searches for Developmental release: vx.x in the html")

        return(version_numbers)


    def get_last_version(self) -> float:
        released_versions = self.get_CADD_released_versions()
        return (max(released_versions))
    

    def download_version(self, version):
        """
        Download the CADD file of specific version given as input
        
        Parameters:
            version: version of the CADD file that wants to be downloaded
            
        Return: 
            file_name: File of the CADD file downloaded
            tabix_file_name: Name of the tabix CADD file downloaded
            """
        
        url_file = f"https://krishna.gs.washington.edu/download/CADD/v{version}/GRCh37/whole_genome_SNVs.tsv.gz"
        tabix_url_file = f"{url_file}.tbi"
        file_name = "whole_genome_SNVs.tsv.gz"
        tabix_file_name = f"{file_name}.tbi"

        # Retrieve expected file size
        response = urllib.request.urlopen(url_file)
        expected_file_size = int(response.headers["Content-Length"])

        output_folder_path = f"{self.cadd_annotations_dir}/hg19/{version}"
        output_file_path = f"{output_folder_path}/{file_name}"
        output_tabix_file_path = f"{output_folder_path}/{tabix_file_name}"
        
        # Check if the folder already exists
        if not os.path.exists(output_folder_path):
            os.mkdir(output_folder_path)
        
        # Check if the files already exist
        if os.path.isfile(output_folder_path):
            logging.critical(f"The file {output_file_path} already exists, the file won't be downloaded to avoid replacement problems")
            raise(FileAlreadyExists(output_folder_path, f"You already have the file: {output_file_path}, the file won't be downloaded to avoid replacement problems"))

        if os.path.isfile(output_tabix_file_path):
            logging.critical(f"The file {output_tabix_file_path} already exists, the file won't be downloaded to avoid replacement problems")
            raise(FileAlreadyExists(output_tabix_file_path, f"You already have the file: {output_tabix_file_path}, the file won't be downloaded to avoid replacement problems"))

        # Download the whole_genome_SNVs.tsv.gz file
        urllib.request.urlretrieve(url_file, output_file_path)
        if os.path.exists(output_file_path) and os.path.getsize(output_file_path) == expected_file_size:
            logging.info(f"The CADD version {version} have been downloaded correctly")
        else:
            logging.critical(f"Failed to download the CADD file of version {version}, the expected size of the file is {expected_file_size} bytes \
                            and the size of the downloaded file is {os.path.getsize(output_file_path)}")
        
        # tabix file
        response = urllib.request.urlopen(tabix_url_file)
        tabix_expected_file_size = int(response.headers["Content-Length"])

        tabix_path = f"{self.cadd_annotations_dir}/{tabix_file_name}"
        urllib.request.urlretrieve(tabix_url_file, tabix_path)
        if os.path.exists(tabix_path) and os.path.getsize(tabix_path) == tabix_expected_file_size:
            logging.info(f"The CADD tabix file of version {version} have been downloaded correctly")
            return(file_name, tabix_path)
        else:
            logging.critical(f"Failed to download the CADD tabix file of version {version}, the expected size of the file is {tabix_expected_file_size} bytes \
                            and the size of the downloaded file is {os.path.getsize(tabix_path)}")
            return(1)
        
        
if "__main__" == __name__:
    cadd_class = CADD()

    released_versions = cadd_class.get_CADD_released_versions()
    latest_version = cadd_class.get_last_version()
    print(f"{latest_version = }")
    cadd_class.download_version(latest_version)