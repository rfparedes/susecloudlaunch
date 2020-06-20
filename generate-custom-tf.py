#!/usr/bin/python3

import argparse
import subprocess
import json

parser = argparse.ArgumentParser(description='generate-custom-tf')
parser.add_argument("--image", default=None, help="image/ami id")
parser.add_argument("--region", default="us-east-1", help="instance/VM region")
parser.add_argument("--os", default="sles-15-sp1", help="SUSE OS version")

args = parser.parse_args()

image  = args.image
region = args.region
os     = args.os 

pint_arg = 'pint amazon images --active --region=' + region + ' ' + "--filter=name~" + os + ",name\!byo,name~x86_64,name\!ecs --json"
pint_output = json.loads(subprocess.check_output(pint_arg,shell=True))

imageid= (pint_output["images"][0]['id'])
print (imageid)
