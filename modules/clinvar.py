import requests
import urllib.request
from global_var import logging, annotations_dir, main_dir
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
        list of files from clinvar weekly directory for genome GRCh37 that can be found in https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/weekly/
        
        Return:
            max(matches) : latest date that clinvar have updated its vcf file 
        """
        response = requests.get(self.weekly_release_url)
        html = response.content.decode("utf-8")

        pattern = r"clinvar_(\d+).vcf.gz"
        matches = set(re.findall(pattern, html))

        if matches:
            latest_version_date = max([int(match) for match in matches])
            return (latest_version_date)
        else:
            return (1)
        
    def get_latest_weekly_files(self) -> list:
        """
        Get the filename of the latest vcf and tbi files uploaded in https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/weekly/
        
        Return:
            latest_clinvar_file: latest vcf clinvar file
            latest_tabix_file: Its corresponding tabix file
        """
        latest_date = self.get_latest_weekly_date()
        latest_clinvar_file = f"clinvar_{latest_date}.vcf.gz"
        latest_tabix_clinvar = f"{latest_clinvar_file}.tbi"
        return (latest_clinvar_file, latest_tabix_clinvar)

    def download_latest_version(self):
        """
        Download the latest version of the clinvar file uploaded in https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/weekly/
        The downloaded files are stored in: ANN_DIR/clinvar/hg19/
        
        Return:
            clinvar_path: Path of the downloaded clinvar file
            tabix_path: Path of the downloaded tbi file
        """
        clinvar_file, tabix_clinvar_file = self.get_latest_weekly_files()
        clinvar_url = f"{self.weekly_release_url}{clinvar_file}"
        tabix_url = f"{self.weekly_release_url}{tabix_clinvar_file}"

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
                logging.info(f"The clinvar file {clinvar_path} has been downloaded correctly")
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

        return clinvar_path, tabix_path
    

    def get_hg19_latest_downloaded_file(self):
        """
        From the hg19 clinvar directory it gets the latest file based on its dates.
        
        Return:
            last_file_path: Absolute path of the latest clinvar file downloaded
        """
        hg19_clinvar_path = os.path.join(self.clinvar_annotations_dir, "hg19")
        
        pattern = r"clinvar_(\d+)\.vcf\.gz"
        last_date = 0
        last_file = None
        for clinvar_file in os.listdir(hg19_clinvar_path):
            if clinvar_file.endswith(".vcf.gz"):
                match = re.search(pattern, clinvar_file)
                if match:
                    date = int(match.group(1))
                    if date > last_date:
                        last_date = date
                        last_file = clinvar_file
                else:
                    logging.critical(
                        f"Be aware, you have a file in clinvar folder that don't follow the nomenclature of clinvar vcf files: nomenclature: clinvar_(\d+)\.vcf\.gz\n\file:{clinvar_file}"
                    )
        last_file_path = os.path.join(self.clinvar_annotations_dir, "hg19", last_file)
        return last_file_path

    def trial_vep_clinvar(self, clinvar_file):
        """
        Testing that vep runs correctly with the latest downloaded clinvar_file
        
        Return:
            output_full_path: output of the annotated vcf
        """
        input_filename = "AP0239.mutect2.lancet.vcf"
        output_filename = "AP0239.mutect2.lancet.clinvar.vep.vcf"
        output_full_path = os.path.join(main_dir, "annotations/test_input_output", output_filename)
        input_dir = os.path.join(main_dir, "annotations/test_input_output")

        clinvar_atributes = "AF_ESP,AF_EXAC,AF_TGP,ALLELEID,CLNDN,CLNDNINCL,CLNDISDB,CLNDISDBINCL,CLNHGVS,CLNREVSTAT,CLNSIG,CLNSIGCONF,CLNSIGINCL,CLNVC,CLNVCSO,CLNVI,DBVARID,GENEINFO,MC,ORIGIN,RS,SSR"
        vep_cmd = f"/usr/bin/docker run -u $(id -u):$(id -g) -v /home/ocanal/REF_DIR/hg19/:/genomedir/:Z -v {input_dir}:/input_dir/ -v /home/ocanal/ANN_DIR:/anndir/ -v /home/ocanal/ANN_DIR/VEP:/opt/vep/.vep ensemblorg/ensembl-vep:release_105.0\
        perl vep --cache --offline --dir_cache /opt/vep/.vep/\
        --dir_plugins /opt/vep/.vep/Plugins/\
        --input_file /input_dir/{input_filename}\
        --output_file /input_dir/{output_filename}\
        --af_1kg --af_gnomad --cache_version 105 --canonical\
        --format vcf --vcf --hgvs --xref_refseq --hgvsg \
        --max_af --pubmed --gene_phenotype \
        --ccds --sift b --polyphen b --symbol --force_overwrite\
        --custom  /anndir/clinvar/hg19/{clinvar_file},ClinVar,vcf,exact,0,{clinvar_atributes}"
        
        logging.info(f"Running vep: \n{vep_cmd}")
        subprocess.run(vep_cmd, shell=True)

        return output_full_path


if "__main__" == __name__:
    clinvar_class = Clinvar()
    #latest_date = clinvar_class.get_latest_weekly_date()
    #clinvar_class.download_latest_version()
    latest_donwloaded_clinvar_path = clinvar_class.get_hg19_latest_downloaded_file()
    clinvar_filename = os.path.basename(latest_donwloaded_clinvar_path)

    clinvar_class.trial_vep_clinvar(clinvar_filename)