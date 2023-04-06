import logging
import argparse
import sys
import re
import os

main_dir = "/home/ocanal/Desktop/pipeline/GC_NGS_PIPELINE"
yaml_pipeline = os.path.join(main_dir, "annotation_resources.yaml")
annotations_dir = "/home/ocanal/ANN_DIR"
genome_v = "hg19"


parser = argparse.ArgumentParser(description="Program that automatically detects if there is a new version of different vep-related databases.")
parser.add_argument(
    "--CADD",
    required=False,
    action="store_true",
    help="Detect new CADD release"
)
parser.add_argument(
    "--vep",
    required=False,
    action="store_true",
    help="Detect new vep release"
)
parser.add_argument(
    "--clinvar",
    required=False,
    action="store_true",
    help="Detect new clinvar release"
)
parser.add_argument(
    "--spliceai",
    required=False,
    action="store_true",
    help="Detect new releases of spliceAI"
)
parser.add_argument(
    "--civic",
    required=False,
    action="store_true",
    help="Download civic nightly release file and compare with pipeline version, if nightly release file is different from the pipeline version, the yaml will point to the nightly file downloaded."
)
parser.add_argument(
    "--dbnsfp",
    required=False,
    action="store_true",
    help="Detect new dbNSFP release."
)
parser.add_argument(
    "--gnomad",
    required=False,
    action="store_true",
    help="Detect new gnomad release"
)
parser.add_argument(
    "--all",
    required=False,
    action="store_true",
    help="Activates all database flags"
)
parser.add_argument(
    "--add_email",
    required=False,
    action="store",
    nargs="+",
    help="Emails to send notifications on new database releases e.g.(--add_email ocanal@example.com) will send an email to ocanal@example.com when the script run finishes."
)
parser.add_argument(
    "--force",
    required=False,
    action="store_true",
    help="Download database files without user input"
)
parser.add_argument(
    "--no_install",
    required=False,
    action="store_true",
    help="Don't install any database file"
)
args = parser.parse_args()

if args.all:
    args.CADD = True
    args.vep = True 
    args.clinvar = True
    args.spliceai = True
    args.civic = True
    args.dbnsfp = True
    args.gnomad = True

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

logging = get_logging()

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
    if args.force and args.no_install:
        msg = "Incompatible flags! Force and no_install flags are incompatible. Read documentation!"
        raise (ValueError(msg))
    if args.force:
        return True
    if args.no_install:
        return False
    while True:
        answer = input(prompt).strip().lower()
        if answer == "y" or answer == "yes":
            return True
        elif answer == "n" or answer == "no":
            return False
        else:
            print("Invalid input. Please enter y or n")



