# susecloudlaunch

# Prerequisites
- Need local install of terraform

- Need the following to build instances in AWS

    - AWS credentials in ~/.aws/credentials of following format:
        [default]
        aws_access_key_id = YOUR_ACCESS_KEY
        aws_secret_access_key = YOUR_SECRET_KEY

    - AWS default region in ~/.aws/config of following format:
        [default]
        region=us-east-1


- Need the following to build instances in Azure
    - az login

- Need the following to build instances in GCP
    - gcloud auth application-default login
    - enabled Cloud Resource Manager API for project


- The public key of logged in user will be used to login to instances
