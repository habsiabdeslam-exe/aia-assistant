"""
Example usage of the NamingService for generating Sodexo GCCC-compliant Resource Group names.

This demonstrates how to use the naming service to:
1. Search for naming conventions in the RAG knowledge base
2. Extract patterns and codes from retrieved documents
3. Generate compliant Resource Group names
4. Validate generated names
"""

import logging
from app.services.naming_service import naming_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_generate_iot_platform_names():
    """Example: Generate RG names for an IoT Platform project"""
    
    logger.info("=" * 80)
    logger.info("EXAMPLE 1: IoT Platform in North Europe")
    logger.info("=" * 80)
    
    # Production environment
    requirements_prd = {
        "project_name": "IOT",
        "cloud_region": "North Europe",
        "environment": "PRD",
        "business_line": "GLB",  # Optional, defaults to GLB
        "region": "GLB"  # Optional, defaults to GLB
    }
    
    result_prd = naming_service.generate_resource_group_name(requirements_prd)
    
    if "error" in result_prd:
        logger.error(f"❌ Error: {result_prd['error']}")
        logger.info("\nValidation Info:")
        logger.info(f"  - RAG Query Executed: {result_prd['validation']['rag_query_executed']}")
        logger.info(f"  - Naming Convention Found: {result_prd['validation']['naming_convention_found']}")
    else:
        logger.info(f"\n✅ Generated Production RG Name: {result_prd['name']}")
        logger.info(f"\nPattern: {result_prd['pattern']}")
        logger.info(f"\nComponents:")
        for comp_name, comp_data in result_prd['components'].items():
            logger.info(f"  - {comp_name}: {comp_data['value']} ({comp_data['description']})")
        logger.info(f"\nSource:")
        logger.info(f"  - File: {result_prd['source']['file']}")
        logger.info(f"  - Section: {result_prd['source']['section']}")
        if result_prd['source'].get('examples_from_docs'):
            logger.info(f"  - Examples from docs: {', '.join(result_prd['source']['examples_from_docs'])}")
    
    # Development environment
    requirements_dev = {
        "project_name": "IOT",
        "cloud_region": "North Europe",
        "environment": "DEV"
    }
    
    result_dev = naming_service.generate_resource_group_name(requirements_dev)
    
    if "error" not in result_dev:
        logger.info(f"\n✅ Generated Development RG Name: {result_dev['name']}")


def example_generate_analytics_names():
    """Example: Generate RG names for an Analytics project in different regions"""
    
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 2: Analytics Platform in West Europe")
    logger.info("=" * 80)
    
    requirements = {
        "project_name": "ANALYTICS",
        "cloud_region": "West Europe",
        "environment": "PRD",
        "business_line": "OSS",  # On-Site Services
        "region": "NAM"  # North America
    }
    
    result = naming_service.generate_resource_group_name(requirements)
    
    if "error" not in result:
        logger.info(f"\n✅ Generated RG Name: {result['name']}")
        logger.info(f"Pattern: {result['pattern']}")
        
        # Validate the generated name
        validation = naming_service.validate_resource_group_name(result['name'])
        logger.info(f"\nValidation Result: {'✅ VALID' if validation['valid'] else '❌ INVALID'}")
        if validation['valid']:
            logger.info(f"Segments: {validation['segments']}")


def example_validate_names():
    """Example: Validate existing Resource Group names"""
    
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 3: Validate Resource Group Names")
    logger.info("=" * 80)
    
    test_names = [
        "GLB-GLB-IENO-IOT-PRD-RG01",  # Valid
        "OSS-NAM-NLWE-ANALYTICS-DEV-RG01",  # Valid
        "invalid-name",  # Invalid
        "GLB-GLB-IENO-IOT-RG01",  # Invalid (missing segment)
        "GLB-GLB-IENO-IOT-PRD-XX01"  # Invalid (wrong suffix)
    ]
    
    for name in test_names:
        result = naming_service.validate_resource_group_name(name)
        status = "✅ VALID" if result['valid'] else "❌ INVALID"
        logger.info(f"\n{name}: {status}")
        if not result['valid']:
            logger.info(f"  Error: {result['error']}")


def example_handle_missing_convention():
    """Example: Handle case when naming convention is not found in RAG"""
    
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 4: Handling Missing Naming Convention")
    logger.info("=" * 80)
    
    # This will search RAG for naming convention
    # If not found, it will return an error with clear instructions
    
    requirements = {
        "project_name": "TESTPROJECT",
        "cloud_region": "North Europe",
        "environment": "PRD"
    }
    
    result = naming_service.generate_resource_group_name(requirements)
    
    if "error" in result:
        logger.warning(f"\n⚠️  {result['error']}")
        logger.info("\nValidation Details:")
        logger.info(f"  - RAG Query Executed: {result['validation']['rag_query_executed']}")
        logger.info(f"  - Naming Convention Found: {result['validation']['naming_convention_found']}")
        logger.info(f"  - All Codes Validated: {result['validation']['all_codes_validated']}")
        logger.info("\nAction Required:")
        logger.info("  1. Upload Sodexo naming convention documents to Azure Blob Storage")
        logger.info("     Container: knowledge-base")
        logger.info("     Folder: naming-convention/")
        logger.info("  2. Re-run the indexer: rag-1770901801308-indexer")
        logger.info("  3. Retry name generation")
    else:
        logger.info(f"\n✅ Generated RG Name: {result['name']}")


def example_search_naming_convention():
    """Example: Search for naming convention documents in RAG"""
    
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 5: Search for Naming Convention in RAG")
    logger.info("=" * 80)
    
    results = naming_service.search_naming_convention_for_resource_groups()
    
    logger.info(f"\nFound {len(results)} relevant chunks in knowledge base:")
    for i, result in enumerate(results, 1):
        logger.info(f"\n{i}. {result.get('title', 'Unknown')}")
        logger.info(f"   Score: {result.get('score', 0):.2f}")
        content_preview = result.get('content', '')[:200]
        logger.info(f"   Preview: {content_preview}...")


if __name__ == "__main__":
    """
    Run all examples to demonstrate the NamingService functionality.
    
    Prerequisites:
    - Azure AI Search index must be populated with Sodexo naming convention documents
    - Documents should be in the knowledge-base blob container
    - Indexer should have run successfully
    """
    
    try:
        # Example 1: Generate names for IoT Platform
        example_generate_iot_platform_names()
        
        # Example 2: Generate names for Analytics Platform
        example_generate_analytics_names()
        
        # Example 3: Validate Resource Group names
        example_validate_names()
        
        # Example 4: Handle missing naming convention
        example_handle_missing_convention()
        
        # Example 5: Search for naming convention in RAG
        example_search_naming_convention()
        
        logger.info("\n" + "=" * 80)
        logger.info("All examples completed!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"\n❌ Error running examples: {e}", exc_info=True)
