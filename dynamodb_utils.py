#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class Comment_loader:

    def __init__(self):
        pass

    def connect_to_db(self, aws_access_key_id: str="", aws_secret_access_key: str=""):
        print("Connecting to dynamodb:", end=" ")

        if aws_access_key_id and aws_secret_access_key:
            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            self.dynamodb = session.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
            self.db_client = session.client('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
            print("connected using keypairs")
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
            self.db_client = session.client('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
            print("connected using without keypairs")


    def create_comment_table(self, table_name: str):
        return self.dynamodb.create_table(
             TableName=table_name,
             KeySchema=[
                 {
                     'AttributeName': 'instance_name',
                     'KeyType': 'HASH' #Partition key
                 },
                 {
                     'AttributeName': 'fetched_date',
                     'KeyType': 'RANGE' #Sort key
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
                 'ReadCapacityUnits': 5,
                 'WriteCapacityUnits': 5
             }
         )


    def set_table(self, table_name: str):
        if table_name in self.db_client.list_tables()["TableNames"]:
            print("Table found:", table_name)
            self.table = self.dynamodb.Table(table_name)
        else:
            print("Table created:", table_name)
            self.table = self.create_comment_table(table_name)

if __name__ == '__main__':
    loader = Comment_loader()
    loader.connect_to_db("Test", "Test")
    # loader.connect_to_db()
    loader.set_table("Yahoo_fin_comment")
