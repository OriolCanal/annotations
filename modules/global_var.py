import logging

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
