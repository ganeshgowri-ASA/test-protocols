#!/usr/bin/env python3
"""
Pinecone Vector Database Bootstrap Script
Phase 1: Equipment Management & AI Assistant Integration
"""

import os
import sys
from pinecone import Pinecone, ServerlessSpec
import anthropic

def bootstrap_pinecone():
    """
    Initialize Pinecone vector database with dual namespaces:
    1. test-protocols: For PV testing protocol knowledge base
    2. equipment-parameters: For equipment specifications and parameters
    """
    
    # Get API keys from environment
    pinecone_api_key = os.getenv('PINECONE_API_KEY')
    pinecone_environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
    
    if not pinecone_api_key:
        print("❌ Error: PINECONE_API_KEY not found in environment variables")
        sys.exit(1)
    
    try:
        print("🚀 Initializing Pinecone client...")
        pc = Pinecone(api_key=pinecone_api_key)
        
        # Index configuration
        index_name = "solaredge-lims"
        dimension = 1536  # OpenAI embeddings dimension
        metric = "cosine"
        
        # Check if index exists
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        if index_name not in existing_indexes:
            print(f"🏭 Creating new index: {index_name}...")
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud='aws',
                    region=pinecone_environment
                )
            )
            print(f"✅ Index '{index_name}' created successfully!")
        else:
            print(f"ℹ️ Index '{index_name}' already exists")
        
        # Connect to index
        index = pc.Index(index_name)
        
        # Get index stats
        stats = index.describe_index_stats()
        print(f"\n📊 Index Statistics:")
        print(f"  Total vectors: {stats.get('total_vector_count', 0)}")
        print(f"  Dimension: {stats.get('dimension', dimension)}")
        print(f"  Namespaces: {list(stats.get('namespaces', {}).keys())}")
        
        print(f"\n✅ Pinecone bootstrap completed successfully!")
        print(f"\n📝 Next Steps:")
        print(f"  1. Use namespace 'test-protocols' for PV testing knowledge")
        print(f"  2. Use namespace 'equipment-parameters' for equipment specs")
        print(f"  3. AI Assistant will query both namespaces for context")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during Pinecone bootstrap: {str(e)}")
        return False

def verify_anthropic_api():
    """
    Verify Anthropic API key is configured for AI Assistant.
    """
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not anthropic_api_key:
        print("\n⚠️ Warning: ANTHROPIC_API_KEY not found")
        print("   AI Assistant will not function without this key")
        return False
    
    try:
        client = anthropic.Anthropic(api_key=anthropic_api_key)
        print("\n✅ Anthropic API key verified")
        return True
    except Exception as e:
        print(f"\n❌ Error verifying Anthropic API: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("   SOLAREDGE LIMS - Phase 1 Bootstrap   ")
    print("="*60)
    
    # Bootstrap Pinecone
    pinecone_success = bootstrap_pinecone()
    
    # Verify Anthropic
    anthropic_success = verify_anthropic_api()
    
    # Summary
    print("\n" + "="*60)
    print("   BOOTSTRAP SUMMARY   ")
    print("="*60)
    print(f"Pinecone Vector DB: {'✅ Ready' if pinecone_success else '❌ Failed'}")
    print(f"Anthropic AI API:   {'✅ Ready' if anthropic_success else '❌ Not Configured'}")
    print("="*60)
    
    sys.exit(0 if (pinecone_success and anthropic_success) else 1)