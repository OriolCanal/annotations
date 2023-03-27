import os
import requests
import re
import urllib.request
from global_var import logging, annotations_dir
import datetime
from packaging import version


class DbNSFP:
    dbnsfp_ann_dir = f"{annotations_dir}/dbNSFP"
    dbnsfp_url = "https://sites.google.com/site/jpopgen/dbNSFP"

    def __init__(self):
        if not os.path.exists(self.dbnsfp_ann_dir):
            os.mkdir(self.dbnsfp_ann_dir)

    def get_html_dbnsfp(self):
        """
        Obtains the text of the dbNSFP html
        """
        return (requests.get(self.dbnsfp_url).text)
    
    def get_dbnsfp_versions(self) -> list:
        """
        gets the versions of the dbnsfp from the html
        
        Returns:
            versions_dates = list of versions dates that have been released
        """
        html = self.get_html_dbnsfp()
        pattern = r"NEW VERSION \((\w+ \d+, \d+)\)"
        matches = re.findall(pattern, html)
        version_dates = []
        if matches:
            for match in matches:
                print(f"{match = }")
                date = match.replace(",","").split()
                print(f"{date = }")
                year, month, day = date[2], date[0], date[1]
                if len(month) == 3:
                    try:
                        # Converting months in abbrebiation format to number format
                        month_num = datetime.datetime.strptime(month, "%b").strftime("%m")
                    except ValueError:
                        logging.warning(f"There is a dbNSFP new version that is not indicated in the website in the expected format: {match}")
                else:
                    # Converting months in whole month format to number format          
                    month_num = datetime.datetime.strptime(month, "%B").strftime("%m")
                date_yyyymmdd = f"{year}{month_num.zfill(2)}{day.zfill(2)}"
                version_dates.append(int(date_yyyymmdd))

        return (version_dates)
    
    def get_last_version_date(self):
        """
        Get the last version date of dbnsfp
        
        Return:
            last_release_date: date of the last release
            """
        version_dates = self.get_dbnsfp_versions()
        print(f"{version_dates = }")
        last_release_date = 0
        for date in version_dates:
            if date > last_release_date:
                last_release_date = date
        if last_release_date == 0:
            logging.critical(f"NO RELEASES FOR dbNSFP have been found")
            raise (ValueError("the algorithm hasn't been able to find releases of dbNSFP the following url is OK?\n \
                             https://sites.google.com/site/jpopgen/dbNSFP"))
        return (last_release_date)

    def get_dbnsfp_updates(self) -> list:
        html = self.get_html_dbnsfp()
        pattern = r"UPDATE \((\w+ \d+, \d+)\)"
        updates_matches = re.findall(pattern, html)
        updates_dates = []
        if updates_matches:
            for update_match in updates_matches:
                date = update_match.replace(",","").split()
                year, month, day = date[2], date[0], date[1]
                if len(month) == 3:
                    try:
                        month_num = datetime.datetime.strptime(month, "%b").strftime("%m")
                    except ValueError:
                        logging.warning(f"There is a new update that the release date is not written with the format expected (abbreviated month): \n {update_match}")
                else:
                    try:
                        month_num = datetime.datetime.strptime(month, "%B").strftime("%m")
                    except ValueError:
                        logging.warning(f"An update release is not written as expected (full month): {update_match}")
                date_yyyymmdd = f"{year}{month_num.zfill(2)}{day.zfill(2)}"
                updates_dates.append(int(date_yyyymmdd))
        return (updates_dates)
    
    def get_dbnsfp_releases(self) -> list:
        html = self.get_html_dbnsfp()
        pattern = r"(?i)dbNSFP(?:\s+\w+){0,5}\s+v(\d+\.\d+(\.\d+)?)\b"
        matches = re.findall(pattern, html)
        versions = [t[0] for t in matches]
        return (set(versions))


    def get_dbnsfp_last_release(self) -> int:
        dbnsfp_releases = self.get_dbnsfp_releases()

        last_version = "0"
        for dbnsfp_release in dbnsfp_releases:
            if version.parse(dbnsfp_release) > version.parse(last_version):
                last_version = dbnsfp_release
        return (last_version)
    
    def get_last_update_date(self) -> int:
        updates_dates = self.get_dbnsfp_updates()
        last_update = 0
        for update_date in updates_dates:
            if update_date > last_update:
                last_update = update_date
        return (last_update)

    def compare_versions(self, version1, version2) -> bool:
        """
        Compare 2 dbnsfp versions
        
        Params:
            version1: version1 
            version2: version2
        
        Return:
            True: If verison1 > version2
            False: if version1 = version2 or version1 < version2
        """
        if version.parse(str(version1)) > version.parse(str(version2)):
            return True
        

if "__main__" == __name__:
    dbnsfp_class = DbNSFP()
    last_version_date = dbnsfp_class.get_last_version_date()
    last_update_date = dbnsfp_class.get_last_update_date()
    releases = dbnsfp_class.get_dbnsfp_releases()
    print(f"{releases = }")
    # print(f"{last_version_date = }")
    # print(f"{last_update_date = }")