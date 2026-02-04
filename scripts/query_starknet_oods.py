#!/usr/bin/env python3
"""
Query ask_starknet tool for OODS validation process, Stone version compatibility, and Integrity verification format.

This gathers additional context about OODS validation to help diagnose the issue.
"""
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def query_ask_starknet(question: str) -> Optional[str]:
    """
    Query ask_starknet tool using MCP.
    
    Note: This is a placeholder implementation. The actual MCP tool call
    would be made here. For now, we'll document the queries to make.
    """
    logger.info(f"Query: {question}")
    logger.warning("⚠️  ask_starknet MCP integration not yet implemented in this script")
    logger.info("To use ask_starknet, call the MCP tool directly or integrate it here")
    return None


def save_query_result(query: str, result: Optional[str], output_dir: Path):
    """Save query result to file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    query_file = output_dir / f"query_{hash(query) % 10000}.json"
    data = {
        "query": query,
        "result": result,
    }
    
    with open(query_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved query result to {query_file}")


def main():
    """Main entry point."""
    queries = [
        (
            "OODS Validation Process",
            "What is the exact OODS validation process in STARK proofs? How does the verifier reconstruct the composition polynomial from trace values and compare it with the proof's claimed value? What parameters affect OODS calculation?"
        ),
        (
            "Stone Prover Version Compatibility",
            "What are the differences between stone5 and stone6 proof formats? How do OODS values differ between versions? What parameters must match between prover and verifier for OODS validation to pass? How can I determine which Stone version a cpu_air_prover binary generates?"
        ),
        (
            "Integrity FactRegistry Verification",
            "How does Integrity FactRegistry verify OODS values? What is the exact format expected for OODS values in the proof calldata? How are OODS values serialized and what fields are required?"
        ),
        (
            "FRI Parameters and OODS",
            "How do FRI parameters (fri_step_list, n_queries, log_n_cosets) affect OODS calculation? What is the relationship between FRI configuration and OODS point selection?"
        ),
        (
            "Canonical Example Stone Commit",
            "What Stone commit hash was used to generate Integrity's recursive cairo0_stone5_keccak_160_lsb_example_proof.json? How can I determine which Stone version a cpu_air_prover binary generates?"
        ),
    ]
    
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / "scripts" / "starknet_queries"
    
    logger.info("=" * 80)
    logger.info("QUERYING ASK_STARKNET FOR OODS CONTEXT")
    logger.info("=" * 80)
    
    results: Dict[str, Optional[str]] = {}
    
    for title, question in queries:
        logger.info("")
        logger.info(f"Query: {title}")
        logger.info(f"Question: {question}")
        
        result = query_ask_starknet(question)
        results[title] = result
        
        if result:
            logger.info(f"✅ Got response (length: {len(result)} chars)")
            save_query_result(question, result, output_dir)
        else:
            logger.warning("⚠️  No response (MCP tool not integrated)")
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    
    successful = sum(1 for r in results.values() if r is not None)
    logger.info(f"Successful queries: {successful}/{len(queries)}")
    
    if successful == 0:
        logger.warning("⚠️  No queries succeeded. MCP tool integration needed.")
        logger.info("To integrate:")
        logger.info("1. Import MCP tool: from mcp import mcp_Ask_Starknet_MCP_ask_starknet")
        logger.info("2. Call tool with question as userInput parameter")
        logger.info("3. Store and process responses")
    
    logger.info(f"Results saved to: {output_dir}")
    sys.exit(0)


if __name__ == "__main__":
    main()
