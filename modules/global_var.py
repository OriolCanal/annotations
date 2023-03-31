import logging
import argparse
import sys
import re
import os
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError

parser = argparse.ArgumentParser(description="Program that automatically detects if there is a new version of different vep-related databases.")
parser.add_argument("--CADD", required=False, action="store_true", help="Detect if a new release of CADD exists")
parser.add_argument("--vep", required=False, action="store_true", help="Detect if new release of vep exists" )
parser.add_argument("--clinvar", required=False, action="store_true", help="Detect if new release of clinvar already exists")
parser.add_argument("--spliceai", required=False, action="store_true", help="Detect new releases of spliceAI")
parser.add_argument("--civic", required=False, action="store_true", help="Download civic nightly release file and compare with pipeline version, if nightly release file is different from the pipeline version, the yaml will point to the nightly file downloaded.")
parser.add_argument("--dbnsfp", required=False, action="store_true", help="Detect new versions of dbNSFP.")
parser.add_argument("--gnomad", required=False, action="store_true", help="Detect if a new version of gnomad has been released")
parser.add_argument("--force", action="store_true", help="Download files without user input" )
args = parser.parse_args()


# def send_slack(message: str):
#     client = WebClient(token="xoxb-5028238476320-5001657632341-yddZjBNRkBEZkoKp0I6dLSHh")

#     try:
#         response = client.chat_postMessage(
#             channel="#annotations",
#             text=message
#         )
#         print("message sent: ", response["ts"])
#         return (0)

#     except SlackApiError as e:
#         print("Error sending message: {}".format(e))
#         return (1)


def get_logging():
    # create logging object
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logging.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return (logging)

def get_y_n_from_user(prompt):
    """
    Getting the user response to determine if a database have to be updated or not.
    If the command line argument --force is given, it automatically returns True and
    the databases will be updated automatically without the need of user input
    
    Params:
        prompt: text that will appear in the terminal

    Return:
        True: if --force is given as command line option or if user input is y
        False: if user input is n
    """
    if args.force:
        return (True)
    while True:
        answer = input(prompt).strip().lower()
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else:
            print("Invalid input. Please enter y or n")

def get_last_yaml_file(directory="/home/ocanal/ANN_DIR/yaml/hg19"):
    last_version = 0
    for file in os.listdir(directory):
        if file.endswith(".yaml"):
            pattern = r"v(\d+.\d+).yaml"
            match = float(re.findall(pattern, file)[0])
            print(f"match = {match}")
            if match > last_version:
                last_version = match
            print (f"match = {match}")
    last_file = f"{directory}/annotations_resources_v{last_version}.yaml"
    print(f"last version = {last_version}")
    return (last_file)

yaml_file = get_last_yaml_file()

annotations_dir = "/home/ocanal/ANN_DIR"

logging = get_logging()