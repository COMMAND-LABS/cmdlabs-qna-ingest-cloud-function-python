"""
Credential decryption — ported from the API microservice's encryption module.

Decrypts the Fernet-encrypted credential blob using CREDENTIALS_ENCRYPTION_KEY
(plus optional comma-separated CREDENTIALS_ENCRYPTION_KEY_OLD for rotation),
read from environment variables. The decrypted service-account JSON never leaves
function memory and must never be logged.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet, MultiFernet
from singletons.environment_variables import EnvironmentVariables

logger = logging.getLogger(__name__)

_cached_multi_fernet: Optional[MultiFernet] = None


def _load_keys() -> List[bytes]:
    keys: List[bytes] = []
    primary = EnvironmentVariables.CREDENTIALS_ENCRYPTION_KEY
    if not primary:
        raise ValueError("CREDENTIALS_ENCRYPTION_KEY environment variable is not set")
    keys.append(primary.encode())

    # Optional rotation keys.
    for k in EnvironmentVariables.CREDENTIALS_ENCRYPTION_KEY_OLD.split(","):
        k = k.strip()
        if k:
            keys.append(k.encode())
    return keys


def _get_cipher() -> MultiFernet:
    global _cached_multi_fernet
    if _cached_multi_fernet is None:
        _cached_multi_fernet = MultiFernet([Fernet(k) for k in _load_keys()])
    return _cached_multi_fernet


def decrypt_credential_data(encrypted_data: str) -> Dict[str, Any]:
    """Decrypt an encrypted credential blob into its dict form."""
    if not encrypted_data:
        raise ValueError("Encrypted data cannot be empty")
    cipher = _get_cipher()
    decrypted = cipher.decrypt(encrypted_data.encode())
    return json.loads(decrypted.decode())
