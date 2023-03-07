#!/usr/bin/env python3

import yaml


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

    def get_yaml_dict(self):
        return(self.yaml_dict)
    
    def substitute_yaml_value(self, database, parameter, value):
        """Given a database, a parameter and a value to introduce, it modifies the indicated value of the yaml object"""
        self.yaml_dict[database][parameter] = value

