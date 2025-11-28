import re
import os
from pathlib import Path

# Files to migrate
FILES_TO_FIX = [
    'pages/2_📋_Service_Request.py',
    'pages/3_📦_Incoming_Inspection.py',
    'pages/4_⚙️_Equipment_Booking.py',
    'pages/5_🔬_Test_Protocols.py',
    'components/analytics_engine.py',
    'components/navigation.py',
]

def add_imports(content):
    """Add SQLAlchemy 2.0 imports if not present"""
    if 'from sqlalchemy import select' in content:
        return content
    
    # Find the import section
    lines = content.split('\n')
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            last_import_idx = i
    
    if last_import_idx > 0:
        insert_line = 'from sqlalchemy import select, desc, asc, and_, or_, func'
        lines.insert(last_import_idx + 1, insert_line)
    
    return '\n'.join(lines)

def migrate_query_to_select(content):
    """Migrate .query() calls to select() syntax"""
    
    # Pattern 1: db.query(Model).order_by(...).limit(...).all()
    content = re.sub(
        r'db\.query\(([^)]+)\)\.order_by\(([^)]+)\.desc\(\)\)\.limit\(([^)]+)\)\.all\(\)',
        r'db.execute(select(\1).order_by(desc(\2)).limit(\3)).scalars().all()',
        content
    )
    
    # Pattern 2: db.query(Model).filter(...).all()
    content = re.sub(
        r'db\.query\(([^)]+)\)\.filter\(\n\s*\(([^)]+)\)\n\s*\|\n\s*\(([^)]+)\)\n\s*\|\n\s*\(([^)]+)\)\n\s*\)\.all\(\)',
        r'db.execute(select(\1).where(or_(\2, \3, \4))).scalars().all()',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 3: db.query(Model).filter(...).all() - single line
    content = re.sub(
        r'db\.query\(([^)]+)\)\.filter\(([^)]+)\)\.all\(\)',
        r'db.execute(select(\1).where(\2)).scalars().all()',
        content
    )
    
    # Pattern 4: db.query(Model).all()
    content = re.sub(
        r'db\.query\(([^)]+)\)\.all\(\)',
        r'db.execute(select(\1)).scalars().all()',
        content
    )
    
    # Pattern 5: db.query(Model).first()
    content = re.sub(
        r'db\.query\(([^)]+)\)\.first\(\)',
        r'db.execute(select(\1)).scalars().first()',
        content
    )
    
    return content

def fix_file(file_path):
    """Fix a single file"""
    if not os.path.exists(file_path):
        print(f"SKIP: {file_path} (not found)")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        content = add_imports(content)
        content = migrate_query_to_select(content)
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"FIXED: {file_path}")
            return True
        else:
            print(f"OK: {file_path} (no changes)")
            return False
    except Exception as e:
        print(f"ERROR: {file_path} - {str(e)}")
        return False

if __name__ == '__main__':
    print("SQLAlchemy 2.0 Migration")
    print("="*50)
    
    fixed_count = 0
    for file in FILES_TO_FIX:
        if fix_file(file):
            fixed_count += 1
    
    print("="*50)
    print(f"Fixed {fixed_count} file(s)")
