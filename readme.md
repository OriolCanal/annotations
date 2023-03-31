# To take into account:
The pipeline should detect the last yaml file used in the server where Bernat has the pipeline, so I should download the yaml file from its server and extract the versions used from there as a first step of the pipeline (TO BE DONE: SHOULD KNOW THE IP).

When installing in a new server, we should change the sys.path.append to where the script is executed

Crete a docker group to give permissions to docker api:

```
sudo gpasswd -a $USER docker
newgrp docker
```
## Give Github and email credentials
You should give as environmental variables the github token and the email token:

```
export github_token=<Your_github_token>
export pwd_bioinf=<email_token>
``` 

The email token can be found in email sended by ocanal@idigbi.org with the following subject: email bioinformàtica bioinformaticaudmmp@gmail.com

# install gsutil

Download the linux 64-bit archive file:

```
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-423.0.0-linux-x86_64.tar.gz
```

Extract the contents:
```
tar -xf google-cloud-cli-423.0.0-linux-x86.tar.gz
```

Run the installation script:
```
./google-cloud-sdk/install.sh
```


# Requeriments

docker_py==1.10.6
packaging==20.1
PyGithub==1.58.1
pytest==5.3.5
PyYAML==6.0
requests==2.28.2
slack_sdk==3.20.2


# DATABASES


## YAML

In annotation_resources_v0.0.yaml the file location needs to be set to /home/gencardio/Desktop/ANN_DIR for ann_dir, yaml_file and yaml_dir

## CLINVAR

Clinvar updates every monday and a new release is uploaded here:

[Clinvar weekly updates webpage](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/weekly/)

The clinvar_date.vcf.gz are already compressed using bgzip and we can find also the indexed file with the same name including .tbi.


## SPLICEAI

des del 2019 no sha generat cap actualització en els fitxers.


## DbNSFP:

They have a mailing list to receive emails notifications about new versions of dbNSFP

We can join the dbnsfp mailing list to receive notifications when a new version is released:

https://groups.google.com/g/dbnsfp_announcements

## CADD

New release approximately once a year for minor imporvement mainly.

On its download webpage: https://cadd.gs.washington.edu/download they always use the same methodology to indicate a new release:
Developmental release: vx.x 

I read its html and find for Developmental release: vx.x and extract the x.x to know its versions.

