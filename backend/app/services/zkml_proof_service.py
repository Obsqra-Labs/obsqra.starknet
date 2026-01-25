"""
zkML proof verification helper.

This service is intentionally lightweight: it loads a precomputed Stone proof JSON
or pre-serialized calldata and verifies it via the Integrity Verifier.

It enables a real zkML demo without requiring proof generation in the backend.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from app.services.proof_loader import serialize_stone_proof, load_calldata_file
from app.services.integrity_service import IntegrityService


@dataclass
class ZkmlProofConfig:
    proof_json_path: Optional[Path]
    calldata_path: Optional[Path]
    serializer_bin: Optional[Path]
    layout: str
    hasher: str
    stone_version: str
    memory_verification: str


class ZkmlProofService:
    """Loads zkML proof calldata and verifies it via Integrity."""

    def __init__(self, integrity: IntegrityService, config: ZkmlProofConfig):
        self.integrity = integrity
        self.config = config

    @staticmethod
    def _string_to_felt(value: str) -> int:
        """
        Encode an ASCII string into a felt (same as verify-on-starknet.sh).
        """
        return int.from_bytes(value.encode("ascii"), "big")

    def load_calldata(self) -> List[int]:
        if self.config.calldata_path and self.config.calldata_path.exists():
            calldata = load_calldata_file(self.config.calldata_path)
        elif self.config.proof_json_path and self.config.serializer_bin:
            calldata = serialize_stone_proof(
                proof_json_path=self.config.proof_json_path,
                serializer_bin=self.config.serializer_bin,
            )
        else:
            raise FileNotFoundError("No zkML proof calldata or proof JSON configured.")

        # Prefix verifier settings expected by Integrity FactRegistry
        config_felts = [
            self._string_to_felt(self.config.layout),
            self._string_to_felt(self.config.hasher),
            self._string_to_felt(self.config.stone_version),
            self._string_to_felt(self.config.memory_verification),
        ]
        return [*config_felts, *calldata]

    async def verify_demo(self) -> bool:
        calldata = self.load_calldata()
        return await self.integrity.verify_with_calldata(calldata)
