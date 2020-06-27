#!/usr/bin/env python3
import boto3
import botocore
import os
from tqdm import tqdm


AWS_DEFAULT_KEY_ID = "SOME_ACCESS_KEY_ID"
AWS_DEFAULT_ACCESS_KEY = "SOME_SECRET_ACCESS_KEY"
SYSTEM_VAR_MESSAGE = "Obtain credentials from system varaiables"
CONNECT_PARAMETERS = """
================================================================================
service: str="" # Ex. aws
region_name: str="us-east-1" # default to "us-east-1"
aws_access_key_id: str="" # default to use env var if this is not provided
aws_secret_access_key: str="" # default to use env var if this is not provided
================================================================================
"""


class AWSUtils:

    def __init__(self, get_envir_key: bool=False):
        self.resource = None
        self.client = None
        self.aws_access_key_id = None
        self.aws_secret_access_key = None
        if get_envir_key:
            self.get_envir_key()

    def get_envir_key(self, key_id_env_key: str = "AWS_ACCESS_KEY_ID",
            access_key_env_key: str = "AWS_SECRET_ACCESS_KEY"):
        print(f'Fetching env vars: [{key_id_env_key}] [{access_key_env_key}]')
        aws_access_key_id = os.environ.get(key_id_env_key)
        aws_secret_access_key = os.environ.get(access_key_env_key)

        if aws_access_key_id == AWS_DEFAULT_KEY_ID \
                or aws_secret_access_key == AWS_DEFAULT_ACCESS_KEY:
            self.aws_access_key_id = self.aws_secret_access_key = None

        if self.aws_access_key_id and self.aws_secret_access_key:
            print(f'Succeeded: {SYSTEM_VAR_MESSAGE}')
        else:
            print(f'Failed {SYSTEM_VAR_MESSAGE}\nPlesae specify the credentials when connected')

    def connect(self, service: str = "", region_name: str = "us-east-1",
                aws_access_key_id: str = "", aws_secret_access_key: str = ""):

        if not service:
            print("Please specify the service you want to connect")
            print(CONNECT_PARAMETERS)
            return

        print(f'Connecting to {service}:', end=" ")
        if aws_access_key_id and aws_secret_access_key:
            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            self.aws_access_key_id = aws_access_key_id
            self.aws_secret_access_key = aws_secret_access_key

            self.resource = session.resource(service, region_name=region_name)
            self.client = session.client(service, region_name=region_name)
            print("connected using provided keypairs")
        elif self.aws_access_key_id and self.aws_secret_access_key:
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            self.resource = session.resource(service, region_name=region_name)
            self.client = session.client(service, region_name=region_name)
            print("connected using env var defined keypairs")
        else:
            self.resource = boto3.resource(service, region_name=region_name)
            self.client = boto3.client(service, region_name=region_name)
            print("connected using without keypairs")


class DynamodbCommentsLoader(AWSUtils):

    def __init__(self):
        super().__init__()
        self.table = None

    def create_comment_table(self, table_name: str):
        return self.resource.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'instance_name',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'fetched_date',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'instance_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'fetched_date',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    def set_table(self, table_name: str):
        if table_name not in self.client.list_tables()["TableNames"]:
            self.table = self.create_comment_table(table_name)
            print("Table created:", table_name)

        self.table = self.resource.Table(table_name)
        print("Table found:", table_name)


class S3Utils(AWSUtils):

    def list_bucket_names(self):
        return [bucket["Name"] for bucket in self.client.list_buckets()["Buckets"]]

    def download_dir(self, prefix, local, bucket):
        # https://stackoverflow.com/questions/31918960/boto3-to-download-all-files-from-a-s3-bucket/31929277
        # When working with buckets that have 1000+ objects
        # its necessary to implement a solution that uses the NextContinuationToken on sequential sets of,
        # at most, 1000 keys. This solution first compiles a list of objects then iteratively creates
        # the specified directories and downloads the existing objects

        keys = list()
        dirs = list()
        next_token = ''
        base_kwargs = {
            'Bucket': bucket,
            'Prefix': prefix,
        }
        while next_token is not None:
            kwargs = base_kwargs.copy()
            if next_token != '':
                kwargs.update({'ContinuationToken': next_token})
            results = self.client.list_objects_v2(**kwargs)
            contents = results.get('Contents')
            for i in contents:
                k = i.get('Key')
                if k[-1] != '/':
                    keys.append(k)
                else:
                    dirs.append(k)
            next_token = results.get('NextContinuationToken')
        for d in dirs:
            dest_pathname = os.path.join(local, d)
            if not os.path.exists(os.path.dirname(dest_pathname)):
                os.makedirs(os.path.dirname(dest_pathname))
        for k in keys:
            dest_pathname = os.path.join(local, k)
            if not os.path.exists(os.path.dirname(dest_pathname)):
                os.makedirs(os.path.dirname(dest_pathname))
            self.client.download_file(bucket, k, dest_pathname)

        with tqdm(desc=f"Downloading:", total=len(keys)) as pbar:
            for k in keys:
                pbar.update(1)
                dest_pathname = os.path.join(local, k)
                if not os.path.exists(os.path.dirname(dest_pathname)):
                    os.makedirs(os.path.dirname(dest_pathname))
                self.client.download_file(bucket, k, dest_pathname)
