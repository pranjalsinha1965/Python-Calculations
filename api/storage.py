import json
import os
from datetime import datetime, timezone
from uuid import uuid4

import boto3


s3_client = boto3.client("s3")

BUCKET_NAME = os.getenv("CALCULATION_BUCKET")


def save_calculation(
    inputs: dict,
    outputs: dict,
) -> dict:
    """
    Save a successful beam calculation as a JSON record in Amazon S3.

    Parameters
    ----------
    inputs : dict
        Validated calculation inputs.

    outputs : dict
        Engineering calculation outputs.

    Returns
    -------
    dict
        Calculation ID and S3 object key.

    Raises
    ------
    RuntimeError
        If CALCULATION_BUCKET is not configured.
    """

    if not BUCKET_NAME:
        raise RuntimeError(
            "CALCULATION_BUCKET environment variable is not configured."
        )

    calculation_id = str(uuid4())
    now = datetime.now(timezone.utc)

    object_key = (
        f"calculations/"
        f"{now:%Y/%m/%d}/"
        f"{calculation_id}.json"
    )

    record = {
        "calculation_id": calculation_id,
        "created_at": now.isoformat(),
        "inputs": inputs,
        "outputs": outputs,
    }

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=object_key,
        Body=json.dumps(record, indent=2),
        ContentType="application/json",
    )

    return {
        "calculation_id": calculation_id,
        "object_key": object_key,
    }