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


class ZkmlProofService:
    """Loads zkML proof calldata and verifies it via Integrity."""

    def __init__(self, integrity: IntegrityService, config: ZkmlProofConfig):
        self.integrity = integrity
        self.config = config

    def load_calldata(self) -> List[int]:
        if self.config.calldata_path and self.config.calldata_path.exists():
            return load_calldata_file(self.config.calldata_path)
        if self.config.proof_json_path and self.config.serializer_bin:
            return serialize_stone_proof(
                proof_json_path=self.config.proof_json_path,
                serializer_bin=self.config.serializer_bin,
            )
        raise FileNotFoundError("No zkML proof calldata or proof JSON configured.")

    async def verify_demo(self) -> bool:
        calldata = self.load_calldata()
        return await self.integrity.verify_with_calldata(calldata)
