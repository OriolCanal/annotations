import logging
import argparse

parser = argparse.ArgumentParser(description="Program that automatically detects if there is a new version of different vep-related databases.")
parser.add_argument("--CADD", required=False, action="store_true", help="Detect if a new release of CADD exists")
parser.add_argument("--vep", required=False, action="store_true", help="Detect if new release of vep exists" )
parser.add_argument("--clinvar", required=False, action="store_true", help="Detect if new release of clinvar already exists")
args = parser.parse_args()

# create logging object
logger = logging.getLogger("my_logger")

# Create a file handler
handler = logging.FileHandler("logging.log")

# Set the logging format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

yaml_file = "/home/ocanal/Desktop/annotations/annotation_resources.yaml"

annotations_dir = "/home/ocanal/ANN_DIR"