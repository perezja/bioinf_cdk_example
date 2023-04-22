#!/usr/bin/env bash

object_key=$1

filename=${object_key##*/}
prefix=${filename%%.*}

# localize vcf from s3 and convert to maf format
echo "Downloading ${object_key} from bucket ${BUCKET_NAME}"
aws s3 cp s3://${BUCKET_NAME}/${object_key} /annotator/input/${filename}

echo "Converting to MAF"
genome-nexus convert /annotator/input/${filename} > /annotator/input/${prefix}.maf

# annotate maf
if [ -f /annotator/input/${prefix}.maf ]; then
  echo "Conversion successful."
  echo "Attempting to annotate MAF file ${prefix}.maf"
  mkdir -p /annotator/output
  head /annotator/input/${prefix}.maf
  genome-nexus annotate maf /annotator/input/${prefix}.maf --api-url ${GENOME_NEXUS_URL} > /annotator/output/${prefix}.maf
else
  echo "Error converting file: ${filename}"
fi

# upload annotated maf to s3
if [ -f /annotator/output/${prefix}.maf ]; then
  echo "Annotation successful. Uploading to S3."
  aws s3 cp /annotator/output/${prefix}.maf s3://${BUCKET_NAME}/annotated_maf/${prefix}.maf
else
  echo "Error annotating file: ${filename}"
fi