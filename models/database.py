import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from config.settings import settings


class Database:
    """Database management class for the Email Productivity Agent"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                category TEXT DEFAULT 'Uncategorized',
                raw_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create action_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT NOT NULL,
                task TEXT NOT NULL,
                deadline TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
            )
        ''')
        
        # Create prompts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create drafts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE SET NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def clear_all_data(self):
        """Clear all data from database (useful for reloading)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM action_items')
        cursor.execute('DELETE FROM drafts')
        cursor.execute('DELETE FROM emails')
        
        conn.commit()
        conn.close()


class EmailModel:
    """Email data model"""
    
    @staticmethod
    def insert(email_data: Dict[str, Any]) -> bool:
        """Insert a new email"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO emails (id, sender, subject, body, timestamp, category, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                email_data['id'],
                email_data['sender'],
                email_data['subject'],
                email_data['body'],
                email_data['timestamp'],
                email_data.get('category', 'Uncategorized'),
                json.dumps(email_data)
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Email already exists
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_all(category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all emails, optionally filtered by category"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        if category_filter and category_filter != "All":
            cursor.execute(
                'SELECT * FROM emails WHERE category = ? ORDER BY timestamp DESC',
                (category_filter,)
            )
        else:
            cursor.execute('SELECT * FROM emails ORDER BY timestamp DESC')
        
        columns = [desc[0] for desc in cursor.description]
        emails = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return emails
    
    @staticmethod
    def get_by_id(email_id: str) -> Optional[Dict[str, Any]]:
        """Get email by ID"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM emails WHERE id = ?', (email_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'sender', 'subject', 'body', 'timestamp', 'category', 'raw_data', 'created_at']
            return dict(zip(columns, row))
        return None
    
    @staticmethod
    def update_category(email_id: str, category: str) -> bool:
        """Update email category"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE emails SET category = ? WHERE id = ?',
            (category, email_id)
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    @staticmethod
    def get_count_by_category() -> Dict[str, int]:
        """Get count of emails per category"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT category, COUNT(*) FROM emails GROUP BY category')
        counts = dict(cursor.fetchall())
        conn.close()
        
        return counts


class ActionItemModel:
    """Action item data model"""
    
    @staticmethod
    def insert(email_id: str, task: str, deadline: str = "Not specified") -> int:
        """Insert a new action item"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO action_items (email_id, task, deadline)
            VALUES (?, ?, ?)
        ''', (email_id, task, deadline))
        
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        
        return item_id
    
    @staticmethod
    def get_by_email(email_id: str) -> List[Dict[str, Any]]:
        """Get all action items for an email"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM action_items WHERE email_id = ? ORDER BY created_at DESC',
            (email_id,)
        )
        
        columns = [desc[0] for desc in cursor.description]
        items = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return items
    
    @staticmethod
    def get_all(status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all action items, optionally filtered by status"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                'SELECT * FROM action_items WHERE status = ? ORDER BY created_at DESC',
                (status,)
            )
        else:
            cursor.execute('SELECT * FROM action_items ORDER BY created_at DESC')
        
        columns = [desc[0] for desc in cursor.description]
        items = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return items
    
    @staticmethod
    def update_status(item_id: int, status: str) -> bool:
        """Update action item status"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE action_items SET status = ? WHERE id = ?',
            (status, item_id)
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success


class PromptModel:
    """Prompt data model"""
    
    @staticmethod
    def insert(name: str, content: str, is_active: bool = True) -> int:
        """Insert a new prompt"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO prompts (name, content, is_active)
                VALUES (?, ?, ?)
            ''', (name, content, 1 if is_active else 0))
            
            conn.commit()
            prompt_id = cursor.lastrowid
            return prompt_id
        except sqlite3.IntegrityError:
            # Prompt with this name already exists, update it
            cursor.execute('''
                UPDATE prompts SET content = ?, is_active = ?
                WHERE name = ?
            ''', (content, 1 if is_active else 0, name))
            conn.commit()
            cursor.execute('SELECT id FROM prompts WHERE name = ?', (name,))
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    @staticmethod
    def get_by_name(name: str) -> Optional[Dict[str, Any]]:
        """Get prompt by name"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM prompts WHERE name = ? AND is_active = 1', (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'name', 'content', 'is_active', 'created_at']
            return dict(zip(columns, row))
        return None
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all prompts"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM prompts ORDER BY created_at DESC')
        columns = [desc[0] for desc in cursor.description]
        prompts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return prompts
    
    @staticmethod
    def update(name: str, content: str) -> bool:
        """Update prompt content"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE prompts SET content = ? WHERE name = ?',
            (content, name)
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success


class DraftModel:
    """Draft data model"""
    
    @staticmethod
    def insert(subject: str, body: str, email_id: Optional[str] = None, metadata: Optional[Dict] = None) -> int:
        """Insert a new draft"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO drafts (email_id, subject, body, metadata)
            VALUES (?, ?, ?, ?)
        ''', (email_id, subject, body, json.dumps(metadata) if metadata else None))
        
        conn.commit()
        draft_id = cursor.lastrowid
        conn.close()
        
        return draft_id
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all drafts"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM drafts ORDER BY created_at DESC')
        columns = [desc[0] for desc in cursor.description]
        drafts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return drafts
    
    @staticmethod
    def get_by_id(draft_id: int) -> Optional[Dict[str, Any]]:
        """Get draft by ID"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM drafts WHERE id = ?', (draft_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'email_id', 'subject', 'body', 'metadata', 'created_at']
            return dict(zip(columns, row))
        return None
    
    @staticmethod
    def update(draft_id: int, subject: str, body: str) -> bool:
        """Update draft content"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE drafts SET subject = ?, body = ? WHERE id = ?',
            (subject, body, draft_id)
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    @staticmethod
    def delete(draft_id: int) -> bool:
        """Delete a draft"""
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM drafts WHERE id = ?', (draft_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success


# Initialize database when module is imported
if __name__ == "__main__":
    db = Database()
    print("Database initialized successfully!")
