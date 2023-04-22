import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Environment,
    CfnOutput,
    aws_s3 as s3,
    aws_logs as logs,
    aws_ecs as ecs,
    aws_ec2 as ec2
)
from aws_cdk.aws_ecr import Repository
from aws_cdk.aws_ssm import StringParameter
from aws_cdk import aws_iam as iam
from constructs import Construct

import json
class GenomeNexusStack(Stack):
    def __init__(self, scope: Construct,
                 construct_id: str,
                 repository_name: str,
                 image_tag: str,
                 genome_nexus_url: str,
                 task_cpu: str = "1024",
                 task_memory_mib: str = "2048",
                 **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        vpc_id = StringParameter.value_from_lookup(self, 'SHARED_VPC_ID')
        vpc = ec2.Vpc.from_lookup(self, 'vpc', vpc_id=vpc_id)

        cluster = ecs.Cluster(self, "GenomeNexusCluster",
                              container_insights=True,
                              vpc=vpc)

        bucket = s3.Bucket(self, "AnnotatorBucket",
                           versioned=False,
                           removal_policy=cdk.RemovalPolicy.DESTROY,
                           auto_delete_objects=True)

        env = kwargs.get('env')
        GenomeNexusAnnotator(self, "GenomeNexusAnnotator",
                             env=env,
                             repo_name=repository_name,
                             image_tag=image_tag,
                             bucket_name=bucket.bucket_name,
                             genome_nexus_url=genome_nexus_url,
                             task_cpu=task_cpu,
                             task_memory_mib=task_memory_mib
                             )
        CfnOutput(self, 'ClusterName', value=cluster.cluster_name)
        CfnOutput(self, 'BucketName', value=bucket.bucket_name)

class GenomeNexusAnnotator(Construct):
    def __init__(self, scope: Construct,
                 construct_id: str,
                 env: Environment,
                 repo_name: str,
                 bucket_name: str,
                 image_tag: str,
                 genome_nexus_url: str,
                 task_cpu: str,
                 task_memory_mib: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repo_uri = f'arn:aws:ecr:{env.region}:{env.account}:repository/{repo_name}'
        ecr_repo = Repository.from_repository_arn(self, f"{construct_id}RepoArn", repo_uri)

        container_image = ecs.ContainerImage.from_ecr_repository(ecr_repo, tag=image_tag)

        log_group = logs.LogGroup(self, f"{construct_id}Logs", retention=logs.RetentionDays.ONE_WEEK)

        task_role = iam.Role(self, "TaskRole",
                             role_name=f"{construct_id}TaskRole",
                             assumed_by=iam.CompositePrincipal(
                                 iam.ServicePrincipal("ecs.amazonaws.com"),
                                 iam.ServicePrincipal("ecs-tasks.amazonaws.com")
                             ))
        bucket = s3.Bucket.from_bucket_name(self, "Bucket", bucket_name)
        bucket.grant_read_write(task_role)

        task_family = "genome_nexus_annotator"
        self.task_definition = ecs.TaskDefinition(self, "VcfAnnotator",
                                                  family=task_family,
                                                  compatibility=ecs.Compatibility.EC2_AND_FARGATE,
                                                  cpu=task_cpu,
                                                  memory_mib=task_memory_mib,
                                                  task_role=task_role)

        environment = {
            'BUCKET_NAME': bucket_name,
            'GENOME_NEXUS_URL': genome_nexus_url
        }
        job_command = [
            "annotateVcf $VCF_FILE"
        ]
        self.task_definition.add_container(id=task_family,
                                           image=container_image,
                                           environment=environment,
                                           memory_limit_mib=int(task_memory_mib),
                                           logging=ecs.LogDrivers.aws_logs(
                                               log_group=log_group,
                                                stream_prefix="ecs"),
                                           command=job_command)


        CfnOutput(self, 'TaskDefinition', value=self.task_definition.task_definition_arn)
        CfnOutput(self, 'LogGroup', value=log_group.log_group_arn)