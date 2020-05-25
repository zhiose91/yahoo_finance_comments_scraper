#!/usr/bin/env python3
import boto3


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
            self.dynamodb = session.resource('dynamodb', region_name='us-east-1')
            self.db_client = session.client('dynamodb', region_name='us-east-1')
            print("connected using keypairs")
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            self.db_client = boto3.client('dynamodb', region_name='us-east-1')
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
        if table_name not in self.db_client.list_tables()["TableNames"]:
            self.table = self.create_comment_table(table_name)
            print("Table created:", table_name)

        self.table = self.dynamodb.Table(table_name)
        print("Table found:", table_name)
