#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, TerraformAsset, AssetType
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.default_vpc import DefaultVpc
from cdktf_cdktf_provider_aws.default_subnet import DefaultSubnet
from cdktf_cdktf_provider_aws.lambda_function import LambdaFunction
from cdktf_cdktf_provider_aws.lambda_permission import LambdaPermission
from cdktf_cdktf_provider_aws.data_aws_caller_identity import DataAwsCallerIdentity
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket, S3BucketCorsRule
from cdktf_cdktf_provider_aws.s3_bucket_notification import S3BucketNotification
from cdktf_cdktf_provider_aws.dynamodb_table import DynamodbTable, DynamodbTableAttribute

class ServerlessStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        AwsProvider(self, "AWS", region="us-east-1")

        account_id = DataAwsCallerIdentity(self, "acount_id").account_id
        bucket = S3Bucket(
            self, "s3_bucket",
            bucket_prefix = "my-cdtf-test-bucket",
            force_destroy=True
        )

        bucket = DynamodbTable(
            self, "DynamodDB-table",
            name= "user_score",
            hash_key="username",
            range_key="lastename",
            attribute=[
            DynamodbTableAttribute(name="username",type="S" ),
            DynamodbTableAttribute(name="lastename",type="S" )
            ],
            billing_mode="PROVISIONED",
            read_capacity=5,
            write_capacity=5
        )

        #lambda_function = LambdaFunction()

        permission = LambdaPermission(
            self, "lambda_permission",
            action="lambda:InvokeFunction",
            statement_id="AllowExecutionFromS3Bucket",
            function_name=lambda_function.arn,
            principal="s3.amazonaws.com",
            source_arn=bucket.arn,
            source_account=account_id,
            depends_on=[lambda_function, bucket]
        )

        notification = S3BucketNotification()

        TerraformOutput()
        
        TerraformOutput()

app = App()
ServerlessStack(app, "cdktf_serverless")
app.synth()

