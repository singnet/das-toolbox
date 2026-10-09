"""Unit tests for atomdb_keys builder module."""

import pytest

from commands.config.config_sections.atomdb_keys import build_public_key_tokens


class TestBuildPublicKeyTokens:
    """Test suite for build_public_key_tokens function."""

    @pytest.mark.parametrize("location", ["local", "remote_peer", "local_persistence"])
    @pytest.mark.parametrize("field", ["uid", "public_keys"])
    @pytest.mark.parametrize("value", ["", " ", "two tokens", "key\tsecond", "key\nsecond", None, 123])
    def test_rejects_invalid_uid_or_first_key(self, location, field, value):
        database_config = {"uid": "local", "public_keys": ["valid_key"]}
        database_config[field] = [value, "valid_fallback"] if field == "public_keys" else value
        if location == "local":
            config = database_config
        elif location == "remote_peer":
            config = {"remote_peers": [database_config]}
        else:
            config = {"remote_peers": [{"local_persistence": database_config}]}

        with pytest.raises(ValueError, match="single non-empty token"):
            build_public_key_tokens(config)

    @pytest.mark.parametrize("public_keys", ["valid_key", {}, 123])
    def test_rejects_public_keys_that_are_not_an_array(self, public_keys):
        with pytest.raises(ValueError, match="public_keys must be an array"):
            build_public_key_tokens({"uid": "local", "public_keys": public_keys})

    def test_simple_local_atomdb_only(self):
        """Test with only local atomdb having public keys."""
        config = {
            "uid": "local",
            "public_keys": ["local_key_primary"],
            "remote_peers": [],
        }
        result = build_public_key_tokens(config)
        assert result == "local local_key_primary"

    def test_local_and_two_remote_peers(self):
        """Test with local atomdb and multiple remote peers."""
        config = {
            "uid": "local",
            "public_keys": ["local_key_primary"],
            "remote_peers": [
                {
                    "uid": "peer1",
                    "public_keys": ["peer1_key_primary"],
                },
                {
                    "uid": "peer2",
                    "public_keys": ["peer2_key_primary"],
                },
            ],
        }
        result = build_public_key_tokens(config)
        assert result == "local local_key_primary peer1 peer1_key_primary peer2 peer2_key_primary"

    def test_uses_first_key_when_multiple(self):
        """Test that only the first public key is used when multiple exist."""
        config = {
            "uid": "local",
            "public_keys": ["local_key_primary", "local_key_secondary", "local_key_tertiary"],
            "remote_peers": [
                {
                    "uid": "peer1",
                    "public_keys": ["peer1_key_primary", "peer1_key_secondary"],
                },
            ],
        }
        result = build_public_key_tokens(config)
        assert result == "local local_key_primary peer1 peer1_key_primary"

    def test_skip_peer_without_public_keys(self):
        """Test that peers without public_keys are skipped."""
        config = {
            "uid": "local",
            "public_keys": ["local_key_primary"],
            "remote_peers": [
                {
                    "uid": "peer1",
                    "public_keys": ["peer1_key_primary"],
                },
                {
                    "uid": "peer2",
                    # No public_keys field
                },
            ],
        }
        result = build_public_key_tokens(config)
        assert result == "local local_key_primary peer1 peer1_key_primary"

    def test_skip_peer_with_empty_public_keys(self):
        """Test that peers with empty public_keys array are skipped."""
        config = {
            "uid": "local",
            "public_keys": ["local_key_primary"],
            "remote_peers": [
                {
                    "uid": "peer1",
                    "public_keys": ["peer1_key_primary"],
                },
                {
                    "uid": "peer2",
                    "public_keys": [],  # Empty array
                },
            ],
        }
        result = build_public_key_tokens(config)
        assert result == "local local_key_primary peer1 peer1_key_primary"

    def test_local_atomdb_without_public_keys(self):
        """Test with local atomdb missing public_keys."""
        config = {
            "uid": "local",
            # No public_keys field
            "remote_peers": [
                {
                    "uid": "peer1",
                    "public_keys": ["peer1_key_primary"],
                },
            ],
        }
        result = build_public_key_tokens(config)
        assert result == "peer1 peer1_key_primary"

    def test_with_nested_local_persistence(self):
        """Test with nested local_persistence peer inside remote peer."""
        config = {
            "uid": "local",
            "public_keys": ["local_key_primary"],
            "remote_peers": [
                {
                    "uid": "peer1",
                    "public_keys": ["peer1_key_primary"],
                    "local_persistence": {
                        "uid": "peer1_local",
                        "public_keys": ["peer1_local_key_primary"],
                    },
                },
            ],
        }
        result = build_public_key_tokens(config)
        assert (
            result
            == "local local_key_primary peer1 peer1_key_primary peer1_local peer1_local_key_primary"
        )

    def test_empty_config(self):
        """Test with empty atomdb config."""
        config = {}
        result = build_public_key_tokens(config)
        assert result == ""

    def test_no_public_keys_anywhere(self):
        """Test when no public_keys exist anywhere in config."""
        config = {
            "uid": "local",
            "remote_peers": [
                {
                    "uid": "peer1",
                },
            ],
        }
        result = build_public_key_tokens(config)
        assert result == ""

    def test_complex_nested_structure(self):
        """Test complex structure with local atomdb, multiple peers, and nested local_persistence."""
        config = {
            "uid": "local",
            "public_keys": ["local_key_primary"],
            "remote_peers": [
                {
                    "uid": "peer1",
                    "public_keys": ["peer1_key_primary"],
                },
                {
                    "uid": "peer2",
                    "public_keys": ["peer2_key_primary"],
                    "local_persistence": {
                        "uid": "peer2_local",
                        "public_keys": ["peer2_local_key_primary"],
                    },
                },
                {
                    "uid": "peer3",
                    "public_keys": ["peer3_key_primary", "peer3_key_secondary"],
                    "local_persistence": {
                        "uid": "peer3_local",
                        # No public_keys
                    },
                },
            ],
        }
        result = build_public_key_tokens(config)
        assert (
            result
            == "local local_key_primary peer1 peer1_key_primary peer2 peer2_key_primary peer2_local peer2_local_key_primary peer3 peer3_key_primary"
        )
