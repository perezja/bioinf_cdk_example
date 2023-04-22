import aws_cdk as core
import aws_cdk.assertions as assertions

from genome_nexus_annotator.genome_nexus_annotator_stack import GenomeNexusAnnotatorStack

# example tests. To run these tests, uncomment this file along with the example
# resource in genome_nexus_annotator/genome_nexus_annotator_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = GenomeNexusAnnotatorStack(app, "genome-nexus-annotator")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
