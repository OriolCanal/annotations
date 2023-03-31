#!/usr/bin/env python3

import yaml
import os
import copy
from global_var import annotations_dir
import re


class Yaml:
    """
    Class for working with the annotation_resources.yaml
    
    Attributes
    ----------
    yaml_path = path to the yaml file

    """
    
    def __init__(self, yaml_path):
        self.yaml_path = yaml_path


class Yaml_file(Yaml):

    def parse_yaml(self) -> dict:
        """parsing the yaml file into a python dictionary"""

        with open(self.yaml_path) as f:
            yaml_dict = yaml.load(f, Loader=yaml.BaseLoader)
        
        return (yaml_dict)
    

class Yaml_dict(Yaml):

    def __init__(self, yaml_dict):
        self.yaml_dict = yaml_dict
        self.initial_dict = copy.deepcopy(yaml_dict)
        self.new_version = float(yaml_dict["version"]) + 0.01
        self.annotations_dir = annotations_dir

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
        obtaines when calling this function are the same or not
        
        Return:
            True : dictionaries (yaml file) has changed
            False: No changes
        """
        print(self.initial_dict)
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
        self.yaml_dict["yaml"]["hg19"] = f"hg19/{yaml_file_name}"

    def dict_to_yaml(self):
        """
        Given the yaml dictionary, it will create a file on anndir/yaml/hg19/annotations_resources_vx.xx 
        where x.xx is the version that contains the elements of the dictionary in yaml format
        
        Parameters: None

        Return: new_yaml_filename -> path of the new yaml file
        """

        self.change_yaml_version()
        self.change_yaml_filename()
        yaml_dir = self.annotations_dir + "/" + self.get_database_dir("yaml") + "/hg19"
        print(f"yaml_dir : {yaml_dir}")
        new_yaml_filename = f"{yaml_dir}/annotations_resources_v{self.new_version}.yaml"
        with open(new_yaml_filename, "w") as yaml_file:
            yaml.dump(self.yaml_dict, yaml_file, sort_keys=False)
        
        return (new_yaml_filename)
        
