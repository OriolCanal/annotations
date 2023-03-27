import subprocess
from global_var import logging, annotations_dir
from annotations_yaml import Yaml_dict
import os
from packaging import version
import re


class Gnomad():
    gsutil_path = "gs://gcp-public-data--gnomad/release/"
    gnoamad_ann_dir = f"{annotations_dir}/gnomAD/hg19/"

    def __init__(self):
        if not os.path.exists(self.gnoamad_ann_dir):
            os.mkdir(self.gnoamad_ann_dir)

    def get_releases(self):
        """
        Extract gnomad releases by using gsutil to extract the folders in the gsutil_data variable
        """

        ls_command = f"gsutil ls {self.gsutil_path}"
        result = subprocess.run(ls_command.split(), stdout=subprocess.PIPE)
        print(f"{result = }")
        output = result.stdout.decode("utf-8")
        paths = output.strip().split("\n")

        versions = []
        for path in paths:
            file = path.replace("gs://gcp-public-data--gnomad/release/","")
            version = file.replace("/","")
            if version != "":
                versions.append(version)

        print(versions)
        return (versions)
    
    def get_last_release(self):
        releases_v = self.get_releases()
        last_v = 0
        for release_v in releases_v:
            if version.parse(str(release_v)) > version.parse(str(last_v)):
                last_v = release_v
        logging.info(f"The last version of gnomad is {last_v}")
        return (last_v)

    def filter_gnomad(self):
        pass

    def download_release_files(self, version):
        gsutil_rel_file_path = f"{version}/vcf/gnomad.genomes.r{version}"

        gsutil_abs_path = f"{self.gsutil_path}{gsutil_rel_file_path}".strip()
        print(gsutil_abs_path)

        file_exists_cmd = f"gsutil -q stat {gsutil_abs_path}"

        result = subprocess.run(file_exists_cmd, shell=True, capture_output=True)
        print(f"{result.stdout = }")
        print(f"{result.stderr = }")

    def download_release_file2(self):
        bucket = "gnomad-public"
        prefix = "release"

        vcf_pattern = r"gnomad.(exomes|genomes).r(\d+).sites.vcf.bgz"

        output = subprocess.check_output(["gsutil", "ls", f"gs://gcp-public-data--gnomad/{prefix}"])
        print(output)
        # Loop over the lines of the output
        latest_version = 0
        latest_filename = ''
        for line in output.splitlines():
            # Extract the filename from the line
            filename = line.decode().split('/')[-1]
            
            # Check if the filename matches the GnomAD VCF pattern
            match = re.match(vcf_pattern, filename)
            if match:
                # Extract the version number from the filename
                version = int(match.group(2))
                print(version)
                
                # If this version is higher than the current latest version, update the latest version and filename
                if version > latest_version:
                    latest_version = version
                    latest_filename = filename

        print(latest_version, latest_filename)
        # Download the latest version of the GnomAD VCF file
        #subprocess.call(['gsutil', 'cp', f'gs://{bucket}/{prefix}/{latest_filename}', '.'])
                    


if "__main__" == __name__:
    print("hey")
    gnomad_class = Gnomad()
    last_version = gnomad_class.get_last_release()
    # gnomad_class.download_release_file2()