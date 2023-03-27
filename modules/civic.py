import requests
import os
from global_var import logging, annotations_dir
import re
import datetime
import hashlib


class Civic():
    download_urls = ["https://civicdb.org/downloads/nightly/nightly-VariantGroupSummaries.tsv",
                     "https://civicdb.org/downloads/nightly/nightly-AssertionSummaries.tsv",
                     "https://civicdb.org/downloads/nightly/nightly-GeneSummaries.tsv",
                     "https://civicdb.org/downloads/nightly/nightly-VariantSummaries.tsv",
                     "https://civicdb.org/downloads/nightly/nightly-ClinicalEvidenceSummaries.tsv"
                     ] 
    civic_url = "https://civicdb.org/releases/main"
    assertions_file_url = "https://civicdb.org/downloads/nightly/nightly-AssertionSummaries.tsv"
    civic_path = f"{annotations_dir}/CIViC"

    def get_date(self):
        date = datetime.datetime.now()
        return (date.strftime("%d_%m_%Y"))

    def download_nightly_file(self):
        print(self.download_urls)
        date = self.get_date()
        for download_url in self.download_urls:
            print(download_url)
            response = requests.get(download_url)
            civic_dir_path =f"{self.civic_path}/{date}"
            civic_filename = f"{os.path.basename(download_url)}"
            civic_file_path = os.path.join(civic_dir_path, civic_filename)
            if response.status_code == 200:
                if not os.path.exists(civic_dir_path):
                    os.mkdir(civic_dir_path)
                with open(civic_file_path, "w") as f:
                    f.write(str(response.content))
                logging.info("Civic nightly file downloaded successfully")

            else:
                logging.critical(f"Failed to download the civic nightly file. Status code {response.status_code}")
        return (civic_dir_path)

    def convert_date_to_int(self, date):
        """
        Convert a date in format 24_05_2022 to 20220504.
        In this way it's easier to compare dates and versions

        Params:
            date: Date in version dd_mm_yyyy

        return:
            date in format yyyymmdd
        """

        day, month, year = date.split("_")
        return (int(f"{year}{month}{day}"))

    def get_last_downloaded_dir(self):
        """
        get the last downloaded civic directory in format dd_mm_yyyy
        """
        pattern = r"\d{2}_\d{2}_\d{2}"
        last_date = 0
        for dir in os.listdir(self.civic_path):
            if re.search(pattern, dir):
                date = self.convert_date_to_int(dir)
                if date > last_date:
                    last_date = date
                    last_dir = dir
        return (last_dir)

    def get_md5(self, file):
        hash_md5 = hashlib.md5()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return (hash_md5.hexdigest())

    def compare_md5(self, dir1, dir2):
        """Compare if files from 2 directories are equal. Both directories should contain the same filesnames.
        Params:
            dir1: Civic directory 1
            dir2: Civic directory 2

        Return:
            True: All the files are equal
            False: A minimum of 1 file is different
        """
        md5_dir1_dict = {}
        md5_dir2_dict = {}
        dir1 = f"{self.civic_path}/{dir1}"
        dir2 = f"{self.civic_path}/{dir2}"
        for root, dirs, files in os.walk(dir1):
            for file in files:
                filepath = os.path.join(root, file)
                md5_dir1_dict[file] = self.get_md5(filepath)

        for root, dirs, files in os.walk(dir2):
            for file in files:
                filepath = os.path.join(root, file)
                md5_dir2_dict[file] = self.get_md5(filepath)
                if md5_dir1_dict[file] == md5_dir2_dict[file]:
                    pass
                else:
                    return (False)
        return (True)


if "__main__" == __name__:
    civic_class = civic()
    civic_class.get_last_downloaded_dir()
    #civic_class.download_nightly_file()
    result = civic_class.compare_md5("28_09_2022", "28_09_2022")
    print (result)