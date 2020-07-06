# susecloudlaunch

# Prerequisites
- Need the following to build instances in AWS

    a. AWS credentials in ~/.aws/credentials of following format:
        [default]
        aws_access_key_id = YOUR_ACCESS_KEY
        aws_secret_access_key = YOUR_SECRET_KEY

    b. AWS default region in ~/.aws/config of following format:
        [default]
        region=us-east-1


- Need the following to build instances in Azure
    a. az login

- Need the following to build instances in GCP
    a. gcloud auth login
    b. gcloud auth application-default login
    b. enabled Cloud Resource Manager API