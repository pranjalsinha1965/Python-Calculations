from __future__ import annotations

import json
import traceback
from dataclasses import asdict

from api.storage import save_calculation
from core.beam_check import beam_check


def create_response(status_code: int, body: dict) -> dict:
    """Create an API Gateway-compatible JSON response."""

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    """
    AWS Lambda entry point for the beam calculation API.

    Endpoint
    --------
    POST /calculate
    """

    try:
        raw_body = event.get("body") or "{}"

        if event.get("isBase64Encoded"):
            return create_response(
                400,
                {
                    "success": False,
                    "error": "Base64 request bodies are not supported.",
                },
            )

        body = json.loads(raw_body)

        result = beam_check(
            span=float(body["span"]),
            uniform_load=float(body["uniform_load"]),
            section_modulus=float(body["section_modulus"]),
            second_moment_of_area=float(
                body["second_moment_of_area"]
            ),
            youngs_modulus=float(body["youngs_modulus"]),
            yield_strength=float(body["yield_strength"]),
            deflection_limit_ratio=float(
                body["deflection_limit_ratio"]
            ),
            input_units=str(
                body.get("input_units", "si")
            ).lower(),
        )

        result_dict = asdict(result)

        storage_result = save_calculation(
            inputs=body,
            outputs=result_dict,
        )

        return create_response(
            200,
            {
                "success": True,
                "calculation_id": storage_result["calculation_id"],
                "object_key": storage_result["object_key"],
                "result": result_dict,
            },
        )

    except json.JSONDecodeError as error:
        return create_response(
            400,
            {
                "success": False,
                "error": "Request body must contain valid JSON.",
                "detail": str(error),
            },
        )

    except KeyError as error:
        return create_response(
            400,
            {
                "success": False,
                "error": f"Missing required input: {error.args[0]}",
            },
        )

    except ValueError as error:
        return create_response(
            400,
            {
                "success": False,
                "error": str(error),
            },
        )

    except Exception as error:
        print("========== LAMBDA ERROR ==========")
        print(f"Exception type: {type(error).__name__}")
        print(f"Exception message: {error}")
        print(traceback.format_exc())
        print("==================================")

        return create_response(
            500,
            {
                "success": False,
                "error": "Internal server error.",
                "detail": str(error),
                "exception_type": type(error).__name__,
            },
        )