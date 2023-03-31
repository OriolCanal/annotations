import ftplib
import re
files_list = ["clinvar_20230121_papu.vcf.gz"     ,
"clinvar_20230121_papu.vcf.gz.md5" ,
"clinvar_20230121_papu.vcf.gz.tbi" ,
"clinvar_20230208.vcf.error.txt"   ,
"clinvar_20230208.vcf.gz"          ,
"clinvar_20230208.vcf.gz.md5"      ,
"clinvar_20230208.vcf.gz.tbi"      ,
"clinvar_20230208_papu.vcf.gz"     ,
"clinvar_20230208_papu.vcf.gz.md5" ,
"clinvar_20230208_papu.vcf.gz.tbi" ,
"clinvar_20230213.vcf.error.txt"   ,
"clinvar_20230213.vcf.gz"          ,
"clinvar_20230213.vcf.gz.md5"      ,
"clinvar_20230213.vcf.gz.tbi"      ,
"clinvar_20230213_papu.vcf.gz"     ,
"clinvar_20230213_papu.vcf.gz.md5" ,
"clinvar_20230213_papu.vcf.gz.tbi" ,
"clinvar_20230218.vcf.error.txt"   ,
"clinvar_20230218.vcf.gz"          ,
"clinvar_20230218.vcf.gz.md5"      ,
"clinvar_20230218.vcf.gz.tbi"      ,
"clinvar_20230218_papu.vcf.gz"     ,
"clinvar_20230218_papu.vcf.gz.md5" ,
"clinvar_20230218_papu.vcf.gz.tbi" ,
"clinvar_20230226.vcf.error.txt"   ,
"clinvar_20230226.vcf.gz"          ,
"clinvar_20230226.vcf.gz.md5"      ,
"clinvar_20230226.vcf.gz.tbi"      ,
"clinvar_20230226_papu.vcf.gz"     ,
"clinvar_20230226_papu.vcf.gz.md5" ,
"clinvar_20230226_papu.vcf.gz.tbi" ,
"clinvar_20230305.vcf.error.txt"   ,
"clinvar_20230305.vcf.gz"          ,
"clinvar_20230305.vcf.gz.md5"      ,
"clinvar_20230305.vcf.gz.tbi"      ,
"clinvar_20230305_papu.vcf.gz"     ,
"clinvar_20230305_papu.vcf.gz.md5" ,
"clinvar_20230305_papu.vcf.gz.tbi"]

class Clinvar:
    def __init__(self):
        self.ftp_url = "ftp.ncbi.nlm.nih.gov"
        self.ftp_weekly_release= f"{self.ftp_url}pub/clinvar/vcf_GRCh37/weekly/"
        self.ftp = ftplib.FTP(self.ftp_url)


    
    def obtain_weekly_files(self) -> list:
        """
        list of files from clinvar weekly directory for genome GRCh37
        
        Return:
            ftp.nlst() : List of files that are on https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/weekly/
        """

        self.ftp.cwd(self.ftp_weekly_release)
        return (self.ftp.nlst())
    
    def ftp_quit_connexion(self, ftp_con):
        self.ftp.quit()

    def get_last_release(self):
        """
        From a list of files that are found in the weekly ftp directory,
        it extracts the latest realease file with extension.vcf.gz and its index file
        
        Returns:
            last_file = latest release of clinvar with extension .vcf.gz
            index_last_file = index of the last file
        """

        files_list = self.obtain_weekly_files() 
        last_date = 0
        regex = r"clinvar_\d{8}\.vcf\.gz"
        for file in files_list:
            match = re.search(regex, file)
            if match:
                file_no_ext = file.split(".")[0]
                date = int(file_no_ext.split("_")[1])
                if date > last_date:
                    last_file = file
        index_last_file = f"{last_file}.tbi"
        return (last_file, index_last_file)

    def download_weekly_file(self, output_filename, ftp_file):
        """
        Download the indicated file from the clinvar weekly release.
        Saved at ouptut_filename path.
        """
        self.ftp.cwd(self.ftp_weekly_release)
        with open(output_filename, "wb") as f:
            self.ftp.retrbinary(f"RETR {ftp_file}", f.write)

if "__main__" == __name__:

    clinvar_class = Clinvar()
    weekly_releases = clinvar_class.obtain_weekly_files()
    print(weekly_releases)


# # Define the FTP server URL and the file path
# ftp_url = "ftp.ncbi.nlm.nih.gov"
# file_path = "/pub/clinvar/vcf_GRCh37/weekly/"

# # Define the file name you want to download
# file_name = "clinvar_2022-03-06.vcf.gz"

# # Connect to the FTP server
# ftp = ftplib.FTP(ftp_url)

# # Change to the directory containing the file
# ftp.cwd(file_path)

# # Download the file
# with open(file_name, "wb") as f:
#     ftp.retrbinary("RETR " + file_name, f.write)

# # Close the FTP connection
# ftp.quit()






# connect to ncbi ftp server
print("hey")
ftp = ftplib.FTP("ftp.ncbi.nlm.nih.gov")
print("ho")
ftp.login()
print("hu")
# navigate to the weekly release clinvar directory for genome grch37
ftp.cwd("/pub/clinvar/vcf_GRCh37/weekly/")
print(ftp)
file_list = ftp.nlst()

# print (file_list)