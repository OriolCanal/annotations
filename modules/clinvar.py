import requests
import urllib.request
from global_var import logging, annotations_dir
import os
import re
from errors import FileAlreadyExists
import subprocess

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
        return (latest_clinvar_file, latest_tabix_clinvar)

    def download_latest_version(self):
        clinvar_file, tabix_clinvar_file = self.get_latest_weekly_files()
        clinvar_url = f"https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/weekly/{clinvar_file}"
        tabix_url = f"https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/weekly/{tabix_clinvar_file}"

        # Retrieve expected file size
        response = urllib.request.urlopen(clinvar_url)
        tabix_response = urllib.request.urlopen(tabix_url)
        expected_clinvar_size = int(response.headers["Content-Length"])
        expected_tabix_size = int(tabix_response.headers["Content-Length"])
        
        clinvar_path = f"{self.clinvar_annotations_dir}/hg19/{clinvar_file}" 
        tabix_path = f"{self.clinvar_annotations_dir}/hg19/{tabix_clinvar_file}" 
        
        # Check if files already exists
        if os.path.isfile(clinvar_path):
            logging.critical(f"The file {clinvar_path} already exists, the file won't be downloaded to avoid replacement problems")
        else:
            # Download the clinvar file and checking it has been dowloaded correctly
            logging.info(f"Downloading the clinvar file: {clinvar_file}")
            urllib.request.urlretrieve(clinvar_url, clinvar_path)
            if os.path.exists(clinvar_path) and os.path.getsize(clinvar_path) == expected_clinvar_size:
                logging.info(f"The clinvar file {clinvar_path} have been downloaded correctly")
            else:
                logging.critical(f"Failed to download the clinvar file {clinvar_path}, the expected size of the file is {expected_clinvar_size} bytes \
                                and the size of the downloaded file is {os.path.getsize(clinvar_path)}")
        
        if os.path.isfile(tabix_path):
            logging.critical(f"The file {tabix_path} already exists, the file won't be downloaded to avoid replacement problems")
        else:
            # Download the tabix clinvar file and checking it has been downloaded correctly
            logging.info(f"Downloading tabix clinvar file: {tabix_clinvar_file}")
            urllib.request.urlretrieve(tabix_url, tabix_path)
            if os.path.exists(tabix_path) and os.path.getsize(tabix_path) == expected_tabix_size:
                logging.info(f"The clinvar file {tabix_path} have been downloaded correctly")
            else:
                logging.critical(f"Failed to download the clinvar file {tabix_path}, the expected size of the file is {expected_tabix_size} bytes \
                                and the size of the downloaded file is {os.path.getsize(tabix_path)}")

    def trial_vep_clinvar(self, clinvar_file):
        reference_genome_path = "/home/ocanal/vep_data/fasta_file/grch37/"
        reference_genome_file = "GRCh37.p13.genome.fa"
        clinvar_atributes = "ALLELEID,CLNDN,CLNDISDB,CLNHGVS,CLNREVSTAT,CLNSIG,CLNSIGCONF,CLNSIGINCL,CLNVC,CLNVCSO,CLNVI,DBVARID,GENEINFO,MC,ORIGIN,RS,SSR"
        vep = "ensemblorg/ensembl-vep"
        vcf_file_dir = "/home/ocanal/Desktop/annotations/vcf_trial/"
        output_vcf = "output_vcf.vcf"
        vcf_file = "RB21942_9999999.vcf"
        vep_cmd = f"docker run \
                -v {vcf_file_dir}:/work_data \
                -v {reference_genome_path}:/reference \
                -v $HOME/vep_data:/opt/vep/.vep:Z \
                -it {vep} vep \
                --cache --offline \
                --fasta /reference/{reference_genome_file} \
                --format vcf \
                --assembly GRCh37 \
                --hgvsg --everything --force_overwrite \
                --custom  {self.clinvar_annotations_dir}/{clinvar_file},vcf,exact,0,{clinvar_atributes}\
                -i /work_data/{vcf_file} \
                -o /work_data/{output_vcf}"
        print(f"{output_vcf = }")
        run = subprocess.run(vep_cmd, shell=True)
        print(f"{run = }")

if "__main__" == __name__:
    clinvar_class = Clinvar()
    latest_date = clinvar_class.get_latest_weekly_date()
    clinvar_class.download_latest_version()