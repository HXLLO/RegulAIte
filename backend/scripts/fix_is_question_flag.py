#!/usr/bin/env python3
"""
Script to fix document chunks incorrectly marked with is_question=true

This script:
1. Connects to Qdrant
2. Identifies document chunks marked with is_question=true that aren't questions
3. Updates those documents to remove the is_question flag
"""

import os
import logging
import argparse
from tqdm import tqdm
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fix_is_question")

def is_valid_question(point: Dict[str, Any]) -> bool:
    """
    Check if a document is a valid question or incorrectly flagged document chunk
    
    Valid questions should:
    - Have the is_question flag set to True
    - Have a "question" field containing the text of the question
    - End with a question mark or have question-like structure
    
    Args:
        point: The document point from Qdrant
        
    Returns:
        True if it's a valid question, False if it's a document chunk incorrectly flagged
    """
    payload = point.get("payload", {})
    
    # Check if it has is_question flag set to True
    if not payload.get("is_question", False):
        return True  # Not marked as a question, so no problem
    
    # Check if it has a question field
    if "question" not in payload:
        return False  # Marked as question but no question field
    
    # Check if the content looks like a question
    question_text = payload.get("question", "")
    
    # Simple heuristic: real questions often end with a question mark
    if question_text.strip().endswith("?"):
        return True
    
    # If the point has a question_index field, it's likely a valid question
    if "question_index" in payload:
        return True
    
    # If content is too long, it's probably not a question
    if len(question_text) > 300:  # Arbitrary threshold
        return False
    
    # Default to true for anything else
    return True

def fix_qdrant_questions(
    qdrant_url: str = "http://localhost:6333",
    collection_name: str = "regulaite_docs",
    dry_run: bool = True
) -> None:
    """
    Identify and fix document chunks incorrectly marked as questions
    
    Args:
        qdrant_url: URL of the Qdrant server
        collection_name: Name of the collection to fix
        dry_run: If True, only identify issues without fixing
    """
    try:
        # Connect to Qdrant
        client = QdrantClient(url=qdrant_url)
        logger.info(f"Connected to Qdrant at {qdrant_url}")
        
        # Get all documents with is_question=true
        scroll_result = client.scroll(
            collection_name=collection_name,
            scroll_filter={
                "must": [
                    {"key": "is_question", "match": {"value": True}}
                ]
            },
            with_payload=True,
            with_vector=False,
            limit=100  # Process in batches
        )
        
        all_points = scroll_result[0]
        while len(all_points) > 0 and scroll_result[1] is not None:
            # Get next batch
            scroll_result = client.scroll(
                collection_name=collection_name,
                scroll_filter={
                    "must": [
                        {"key": "is_question", "match": {"value": True}}
                    ]
                },
                with_payload=True,
                with_vector=False,
                limit=100,
                offset=scroll_result[1]
            )
            all_points.extend(scroll_result[0])
        
        logger.info(f"Found {len(all_points)} documents marked as questions")
        
        # Identify incorrect points
        incorrect_points = []
        for point in all_points:
            if not is_valid_question(point):
                incorrect_points.append(point)
        
        logger.info(f"Found {len(incorrect_points)} documents incorrectly marked as questions")
        
        if not incorrect_points:
            logger.info("No documents to fix. Exiting.")
            return
        
        # Show examples of incorrect documents
        for i, point in enumerate(incorrect_points[:3]):
            logger.info(f"Example {i+1} of incorrect question:")
            logger.info(f"  ID: {point.id}")
            logger.info(f"  Text preview: {point.payload.get('text', '')[:100]}...")
        
        if dry_run:
            logger.info("Dry run mode. No changes were made.")
            return
        
        # Fix incorrect points
        points_to_update = []
        for point in tqdm(incorrect_points, desc="Preparing updates"):
            # Create a new payload without is_question
            new_payload = point.payload.copy()
            if "is_question" in new_payload:
                del new_payload["is_question"]
            
            # Create update point
            points_to_update.append(
                PointStruct(
                    id=point.id,
                    payload=new_payload
                )
            )
        
        # Update in batches of 100
        batch_size = 100
        for i in tqdm(range(0, len(points_to_update), batch_size), desc="Updating documents"):
            batch = points_to_update[i:i+batch_size]
            client.upsert(
                collection_name=collection_name,
                points=batch
            )
        
        logger.info(f"Successfully updated {len(points_to_update)} documents")
        
    except Exception as e:
        logger.error(f"Error fixing questions: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix documents incorrectly marked as questions in Qdrant")
    parser.add_argument("--qdrant-url", default="http://localhost:6333", help="URL of the Qdrant server")
    parser.add_argument("--collection", default="regulaite_docs", help="Name of the collection to fix")
    parser.add_argument("--fix", action="store_true", help="Actually fix the documents (without this flag, only a dry run is performed)")
    
    args = parser.parse_args()
    
    fix_qdrant_questions(
        qdrant_url=args.qdrant_url,
        collection_name=args.collection,
        dry_run=not args.fix
    ) 