#!/usr/bin/env python3
import os

import aws_cdk
import aws_cdk as cdk

from genome_nexus_annotator.genome_nexus_annotator_stack import (
    GenomeNexusStack
)
from genome_nexus_annotator.genome_nexus_image_stack import (
    GenomeNexusImageStack
)

app = cdk.App()
env = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                      region=os.getenv('CDK_DEFAULT_REGION'))

repository_name = app.node.try_get_context('repository_name')
image_tag = app.node.try_get_context('image_tag')
genome_nexus_url = app.node.try_get_context('genome_nexus_url')

GenomeNexusImageStack(
    app, f'GenomeNexusImageStack',
    repository_name=repository_name,
    image_tag=image_tag,
    env=env
)

GenomeNexusStack(
    app, "GenomeNexusStack",
    repository_name=repository_name,
    image_tag=image_tag,
    genome_nexus_url=genome_nexus_url,
    env=env
)

app.synth()
