"""
Database utilities
Handles file system setup and optional Replit DB integration
"""

import os
from pathlib import Path

def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'backend/uploads',
        'backend/generated_contracts',
        'backend/templates'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create .gitkeep if directory is empty
        gitkeep = Path(directory) / '.gitkeep'
        if not gitkeep.exists() and not any(Path(directory).iterdir()):
            gitkeep.touch()

def get_template_path():
    """Get the path to the Word template"""
    template_path = os.getenv('TEMPLATE_PATH', 'backend/templates/template.docx')
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(
            f"Template not found at {template_path}. "
            "Please upload your template.docx to backend/templates/"
        )
    
    return template_path

# Optional: Replit DB integration
try:
    from replit import db as replit_db
    HAS_REPLIT_DB = True
except ImportError:
    HAS_REPLIT_DB = False
    replit_db = None

class Database:
    """Simple database abstraction that works with both memory and Replit DB"""
    
    def __init__(self):
        self.use_replit = HAS_REPLIT_DB and os.getenv('USE_REPLIT_DB', 'false').lower() == 'true'
        
        if not self.use_replit:
            # In-memory storage
            self.storage = {
                'contracts': {},
                'documents': {}
            }
    
    def get(self, key, default=None):
        """Get value from database"""
        if self.use_replit:
            return replit_db.get(key, default)
        return self.storage.get(key, default)
    
    def set(self, key, value):
        """Set value in database"""
        if self.use_replit:
            replit_db[key] = value
        else:
            self.storage[key] = value
    
    def delete(self, key):
        """Delete value from database"""
        if self.use_replit:
            if key in replit_db:
                del replit_db[key]
        else:
            if key in self.storage:
                del self.storage[key]
    
    def keys(self):
        """Get all keys"""
        if self.use_replit:
            return replit_db.keys()
        return self.storage.keys()
    
    def __getitem__(self, key):
        return self.get(key)
    
    def __setitem__(self, key, value):
        self.set(key, value)
    
    def __delitem__(self, key):
        self.delete(key)
    
    def __contains__(self, key):
        if self.use_replit:
            return key in replit_db
        return key in self.storage
