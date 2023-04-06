#!/usr/bin/env python3

import yaml
import os
import copy
from global_var import annotations_dir, genome_v, main_dir, logging
import re


class Yaml:
    """
    Class for working with the annotation_resources.yaml

    main_yaml is in the main directory and is the one used by the pipeline
    In annotations_yaml folder we have all the yaml versions.
    
    Attributes
    ----------
    yaml_path = path to the yaml file

    """
    
    def __init__(self, main_yaml_path):
        self.yaml_path = main_yaml_path
        self.yamls_folder = os.path.join(annotations_dir, "annotations_yaml")


    def get_last_yaml_file(self):
        last_version = 0
        for file in os.listdir(self.yamls_folder):
            if file.endswith(".yaml"):
                pattern = r"v(\d+.\d+).yaml"
                match = float(re.findall(pattern, file)[0])
                if match > last_version:
                    last_version = match
        last_file = f"{self.yamls_folder}/annotations_resources_v{last_version}.yaml"
        logging.info(f"The last yaml version in {self.yamls_folder} is {last_version}")
        return (last_file)


class Yaml_file(Yaml):

    def parse_yaml(self) -> dict:
        """parsing the yaml file into a python dictionary"""

        with open(self.yaml_path) as f:
            yaml_dict = yaml.load(f, Loader=yaml.BaseLoader)
        
        return (yaml_dict)
    

class Yaml_dict(Yaml_file):

    def __init__(self, yaml_dict):
        self.yaml_dict = yaml_dict
        self.initial_dict = copy.deepcopy(yaml_dict)
        self.new_version = float(yaml_dict["version"]) + 0.01
        self.annotations_dir = annotations_dir

    def get_ann_dir(self):
        return (self.yaml_dict["ann_dir"])
    
    def get_yaml_dict(self):
        return (self.yaml_dict)
    
    def substitute_yaml_value(self, database, parameter, value):
        """Given a database, a parameter and a value to introduce, it modifies the indicated value of the yaml object"""
        self.yaml_dict[database][parameter] = value

    def get_database_dir(self, database):
        """
        Get the database directory in annotations directory given a database"""
        return (self.yaml_dict[database]["dirname"])
    
    def get_database_file(self, database):
        """
        Returns the file from a given database
        """
        file_path = self.yaml_dict[database]["hg19"]
        return (os.path.basename(file_path))
    
    def get_database_version(self, database):
        """
        Returns the version of specified database
        """
        return (self.yaml_dict[database]["version"])
    
    def get_dict_hash(self):
        return (hash(frozenset(self.yaml_dict)))
    
    def compare_dict_changes(self):
        """
        Compares if the yaml dictionary given when created the class and the dictionary
        obtained when calling this function are the same or not
        
        Return:
            True : dictionaries (yaml file) has changed
            False: No changes
        """
        return (self.initial_dict != self.yaml_dict)
    
    def get_yaml_version(self):
        return (self.yaml_dict["version"])

    def change_yaml_version(self) -> float:
        """
        Changes the absolute version and the specific yaml version
        """
        self.yaml_dict["version"] = self.new_version
        self.yaml_dict["yaml"]["version"] = self.new_version
        self.change_yaml_filename()
        return (float(self.new_version))

    def change_yaml_filename(self) -> None:
        """
        Changes the name of the yaml file in the yaml dictionary
        """
        yaml_file_name = f"annotation_resources_v{self.new_version}.yaml"
        self.yaml_dict["yaml"][genome_v] = os.path.join(genome_v, yaml_file_name)

    def dict_to_yaml(self):
        """
        Given the yaml dictionary, it will create a file on anndir/yaml/hg19/annotations_resources_vx.xx 
        where x.xx is the version that contains the elements of the dictionary in yaml format
        
        Parameters: None

        Return: 
            yaml_abs_path : path of the new yaml file that is sotred in yaml folder (in anndir)
            yaml_pipeline : path of the new yaml file that is sotred in the main directory 
                (the one that will be used by the pipeline)
        """

        self.change_yaml_version()
        self.change_yaml_filename()

        # It will be stored 2 copies of the yaml file, one in the main directory without version number in the name (yaml_pipeline)
        # and one in the annotations yaml folder
        # yaml that will be stored in yaml folder
        ann_dir = self.get_ann_dir()
        yaml_dir = self.yaml_dict["yaml"]["dirname"]
        yaml_filename = self.yaml_dict["yaml"][genome_v]
        yaml_abs_path = os.path.join(ann_dir, yaml_dir, yaml_filename)

        yaml_pipeline = os.path.join(main_dir, "annotation_resources.yaml")
        with open(yaml_abs_path, "w") as yaml_file:
            yaml.dump(self.yaml_dict, yaml_file, sort_keys=False)
        
        with open(yaml_pipeline, "w") as yaml_file:
            yaml.dump(self.yaml_dict, yaml_file, sort_keys=False)
        
        return (yaml_abs_path, yaml_pipeline)
        
