import pytest

from shared.utils.command_router_payload import build_query_execution_payload


def test_build_payload_uses_command_text_for_query_tokens():
    payload = build_query_execution_payload(
        '(Similarity "human" %C)',
        {"max_answers": 1, "populate_metta_mapping": True},
    )

    assert payload == {
        "command": "query",
        "params": {
            "query": {
                "syntax": "metta",
                "tokens": ['(Similarity "human" %C)'],
            },
            "max_answers": 1,
            "populate_metta_mapping": True,
        },
    }


def test_build_payload_rejects_reserved_query_parameter():
    with pytest.raises(ValueError, match="Reserved parameter 'query'"):
        build_query_execution_payload(
            '(Similarity "human" %C)',
            {"query": {"syntax": "metta", "tokens": ["(evil query)"]}},
        )


def test_build_payload_requires_non_empty_query_text():
    with pytest.raises(ValueError, match="Query text must not be empty"):
        build_query_execution_payload("   ")
