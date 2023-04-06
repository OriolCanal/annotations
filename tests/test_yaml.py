import yaml
from ..modules import annotations_yaml


test_yaml_file = "/home/ocanal/Desktop/annotations/annotation_resources.yaml"
yaml_file_class = annotations_yaml.Yaml_file(test_yaml_file)

yaml_dict = yaml_file_class.parse_yaml()

def test_parse_yaml():

    keys = [
        'version',
        'ann_dir',
        'missense_predictors',  
        'splicing_predictors',
        'genomewide_predictors',
        'yaml',
        'vep',
        'clinvar',
        'gene_synonyms',
        'thousand_genomes',
        'gnomad',
        'gnomad_exomes',
        'gnomad_only_af',
        'gnomad_sv',
        'cadd',
        'dbnsfp',
        'spliceai_snv',
        'spliceai_indel',
        'dbscsnv',
        'maxent',
        'tier_catsalut',
        'cancer_hotspots',
        'civic',
        'cgi',
        'chimerdb',
        'blacklist',
        'phastcons',
        'phylop',
        'mappability',
        'grapes_db'
    ]

    assert len(keys) == len(yaml_dict)

    for key in keys:
        assert key in yaml_dict

    
    
Yaml_dict_class = annotations_yaml.Yaml_dict(yaml_dict)

def test_get_yaml_dict():
    yaml_dict = Yaml_dict_class.get_yaml_dict()
    assert isinstance(yaml_dict, dict)

def test_substitute_yaml_value():
    Yaml_dict_class.substitute_yaml_value("vep", "version", "12")
    new_yaml_dict = Yaml_dict_class.get_yaml_dict()

    assert isinstance(new_yaml_dict, dict)
    assert new_yaml_dict["vep"]["version"] == "12" 
