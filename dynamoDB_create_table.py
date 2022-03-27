import boto3


dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1', aws_access_key_id ='AKIAWANQWOMS5FXZBOM5', aws_secret_access_key = '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')
table = dynamodb.create_table(
    TableName='users',
    KeySchema=[{'AttributeName': 'email','KeyType': 'HASH'},{'AttributeName': 'password','KeyType': 'RANGE'}],
    AttributeDefinitions=[{'AttributeName': 'email','AttributeType': 'S'},{'AttributeName': 'password','AttributeType': 'S'},],
    ProvisionedThroughput={'ReadCapacityUnits': 5,'WriteCapacityUnits': 5}
)