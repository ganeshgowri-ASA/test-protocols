"""Pinecone Bootstrap Script - Phase 1
Initializes Pinecone index for PV LIMS-QMS system
"""
import os
try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    print("Warning: pinecone-client not installed. Run: pip install pinecone-client")
    Pinecone = None
    ServerlessSpec = None

INDEX_NAME = "pv-lims-qms"

def create_pinecone_index():
    """Create Pinecone index if it doesn't exist"""
    if Pinecone is None:
        print("❌ Pinecone client not available")
        return None
    
    try:
        api_key = os.environ.get('PINECONE_API_KEY')
        if not api_key or api_key == 'dummy':
            print("⚠️  PINECONE_API_KEY not configured in environment")
            return None
        
        pc = Pinecone(api_key=api_key)
        
        # Check if index exists
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        if INDEX_NAME not in existing_indexes:
            print(f"🚀 Creating Pinecone index: {INDEX_NAME}...")
            pc.create_index(
                name=INDEX_NAME,
                dimension=1536,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            print(f"✅ Index '{INDEX_NAME}' created successfully")
        else:
            print(f"✅ Index '{INDEX_NAME}' already exists")
        
        return pc.Index(INDEX_NAME)
    
    except Exception as e:
        print(f"❌ Error creating Pinecone index: {str(e)}")
        return None

if __name__ == "__main__":
    print("="*50)
    print("🚀 PINECONE BOOTSTRAP - PV LIMS QMS")
    print("="*50)
    
    index = create_pinecone_index()
    
    if index:
        print("\n✅ Bootstrap completed successfully")
        print(f"Index: {INDEX_NAME}")
        print("\nNext steps:")
        print("1. Load protocol parameters (future enhancement)")
        print("2. Load PV knowledge base (future enhancement)")
        print("3. Configure AI assistant in Streamlit")
    else:
        print("\n❌ Bootstrap failed")
        print("Please configure PINECONE_API_KEY in Railway environment variables")
    
    print("="*50)