import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

class DatabaseService:
    def __init__(self, db_path: str = "spacetask.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                coin_balance INTEGER DEFAULT 200,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                creator_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                label TEXT,
                completion_criteria TEXT NOT NULL,
                bounty_amount INTEGER NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                location_name TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (creator_id) REFERENCES users (id)
            )
        ''')
        
        # Task submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                submitter_id INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                note TEXT,
                status TEXT DEFAULT 'pending',
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (submitter_id) REFERENCES users (id)
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                device_token TEXT,
                platform TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Transactions table for coin transfers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER,
                to_user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                task_id INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_user_id) REFERENCES users (id),
                FOREIGN KEY (to_user_id) REFERENCES users (id),
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User operations
    def create_user(self, username: str, email: str, password_hash: str) -> Optional[int]:
        """Create a new user with 200 starting coins"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, coin_balance)
                VALUES (?, ?, ?, 200)
            ''', (username, email, password_hash))
            user_id = cursor.lastrowid
            
            # Record initial coin grant
            cursor.execute('''
                INSERT INTO transactions (to_user_id, amount, transaction_type, description)
                VALUES (?, 200, 'signup_bonus', 'Initial signup bonus')
            ''', (user_id,))
            
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    
    def update_user_balance(self, user_id: int, new_balance: int) -> bool:
        """Update user's coin balance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET coin_balance = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_balance, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # Task operations
    def create_task(self, creator_id: int, title: str, description: str, label: str,
                   completion_criteria: str, bounty_amount: int, latitude: float,
                   longitude: float, location_name: str = None) -> Optional[int]:
        """Create a new task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (creator_id, title, description, label, completion_criteria,
                             bounty_amount, latitude, longitude, location_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (creator_id, title, description, label, completion_criteria,
              bounty_amount, latitude, longitude, location_name))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def get_tasks(self, limit: int = 50, offset: int = 0, status: str = 'active') -> List[Dict[str, Any]]:
        """Get list of tasks"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, u.username as creator_username
            FROM tasks t
            JOIN users u ON t.creator_id = u.id
            WHERE t.status = ?
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        ''', (status, limit, offset))
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, u.username as creator_username
            FROM tasks t
            JOIN users u ON t.creator_id = u.id
            WHERE t.id = ?
        ''', (task_id,))
        
        task = cursor.fetchone()
        conn.close()
        return dict(task) if task else None
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update task fields"""
        if not kwargs:
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['title', 'description', 'label', 'completion_criteria', 'bounty_amount', 'status']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            conn.close()
            return False
        
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(task_id)
        
        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_task(self, task_id: int) -> bool:
        """Delete task (only if no submissions)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if task has submissions
        cursor.execute('SELECT COUNT(*) FROM task_submissions WHERE task_id = ?', (task_id,))
        submission_count = cursor.fetchone()[0]
        
        if submission_count > 0:
            conn.close()
            return False
        
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # Task submission operations
    def create_submission(self, task_id: int, submitter_id: int, image_url: str, note: str = None) -> Optional[int]:
        """Create a task submission"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO task_submissions (task_id, submitter_id, image_url, note)
            VALUES (?, ?, ?, ?)
        ''', (task_id, submitter_id, image_url, note))
        
        submission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return submission_id
    
    def get_task_submissions(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all submissions for a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ts.*, u.username as submitter_username
            FROM task_submissions ts
            JOIN users u ON ts.submitter_id = u.id
            WHERE ts.task_id = ?
            ORDER BY ts.submitted_at DESC
        ''', (task_id,))
        
        submissions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return submissions
    
    def get_submission_by_id(self, submission_id: int) -> Optional[Dict[str, Any]]:
        """Get submission by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ts.*, u.username as submitter_username, t.creator_id, t.bounty_amount
            FROM task_submissions ts
            JOIN users u ON ts.submitter_id = u.id
            JOIN tasks t ON ts.task_id = t.id
            WHERE ts.id = ?
        ''', (submission_id,))
        
        submission = cursor.fetchone()
        conn.close()
        return dict(submission) if submission else None
    
    def accept_submission(self, submission_id: int) -> bool:
        """Accept a submission and transfer coins"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get submission details
            cursor.execute('''
                SELECT ts.*, t.creator_id, t.bounty_amount
                FROM task_submissions ts
                JOIN tasks t ON ts.task_id = t.id
                WHERE ts.id = ? AND ts.status = 'pending'
            ''', (submission_id,))
            
            submission = cursor.fetchone()
            if not submission:
                conn.close()
                return False
            
            # Get current balances
            cursor.execute('SELECT coin_balance FROM users WHERE id = ?', (submission['creator_id'],))
            creator_balance = cursor.fetchone()[0]
            
            cursor.execute('SELECT coin_balance FROM users WHERE id = ?', (submission['submitter_id'],))
            submitter_balance = cursor.fetchone()[0]
            
            # Check if creator has enough coins
            if creator_balance < submission['bounty_amount']:
                conn.close()
                return False
            
            # Transfer coins
            new_creator_balance = creator_balance - submission['bounty_amount']
            new_submitter_balance = submitter_balance + submission['bounty_amount'] + 10  # 10 base coins
            
            cursor.execute('UPDATE users SET coin_balance = ? WHERE id = ?', 
                         (new_creator_balance, submission['creator_id']))
            cursor.execute('UPDATE users SET coin_balance = ? WHERE id = ?', 
                         (new_submitter_balance, submission['submitter_id']))
            
            # Update submission status
            cursor.execute('''
                UPDATE task_submissions SET status = 'accepted', reviewed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (submission_id,))
            
            # Update task status
            cursor.execute('UPDATE tasks SET status = "completed" WHERE id = ?', (submission['task_id'],))
            
            # Record transactions
            cursor.execute('''
                INSERT INTO transactions (from_user_id, to_user_id, amount, transaction_type, task_id, description)
                VALUES (?, ?, ?, 'task_bounty', ?, 'Task bounty payment')
            ''', (submission['creator_id'], submission['submitter_id'], submission['bounty_amount'], submission['task_id']))
            
            cursor.execute('''
                INSERT INTO transactions (to_user_id, amount, transaction_type, task_id, description)
                VALUES (?, 10, 'task_completion', ?, 'Base task completion reward')
            ''', (submission['submitter_id'], submission['task_id']))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    # Notification operations
    def register_device(self, user_id: int, device_token: str, platform: str) -> bool:
        """Register device for push notifications"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO notifications (user_id, device_token, platform)
            VALUES (?, ?, ?)
        ''', (user_id, device_token, platform))
        
        conn.commit()
        conn.close()
        return True
    
    def get_nearby_tasks(self, latitude: float, longitude: float, radius_km: float = 5.0) -> List[Dict[str, Any]]:
        """Get tasks within a certain radius (simplified distance calculation)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Simplified bounding box calculation (not precise for large distances)
        lat_range = radius_km / 111.0  # Rough km to degrees
        lng_range = radius_km / (111.0 * abs(latitude))
        
        cursor.execute('''
            SELECT t.*, u.username as creator_username
            FROM tasks t
            JOIN users u ON t.creator_id = u.id
            WHERE t.status = 'active'
            AND t.latitude BETWEEN ? AND ?
            AND t.longitude BETWEEN ? AND ?
        ''', (latitude - lat_range, latitude + lat_range,
              longitude - lng_range, longitude + lng_range))
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks
    
    def get_user_tasks(self, user_id: int, task_type: str = 'created') -> List[Dict[str, Any]]:
        """Get tasks created or completed by user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if task_type == 'created':
            query = '''
                SELECT t.*, u.username as creator_username
                FROM tasks t
                JOIN users u ON t.creator_id = u.id
                WHERE t.creator_id = ?
                ORDER BY t.created_at DESC
            '''
            cursor.execute(query, (user_id,))
        else:  # completed
            query = '''
                SELECT t.*, u.username as creator_username, s.submitted_at, s.image_url
                FROM tasks t
                JOIN users u ON t.creator_id = u.id
                JOIN task_submissions s ON t.id = s.task_id
                WHERE s.submitter_id = ? AND s.status = 'accepted'
                ORDER BY s.submitted_at DESC
            '''
            cursor.execute(query, (user_id,))
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user leaderboard ordered by coins, task completions, and username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            WITH user_completions AS (
                SELECT submitter_id, COUNT(*) as completed_tasks
                FROM task_submissions
                WHERE status = 'accepted'
                GROUP BY submitter_id
            )
            SELECT 
                u.id,
                u.username,
                u.coin_balance,
                COALESCE(uc.completed_tasks, 0) as completed_tasks
            FROM users u
            LEFT JOIN user_completions uc ON u.id = uc.submitter_id
            ORDER BY 
                u.coin_balance DESC,
                COALESCE(uc.completed_tasks, 0) DESC,
                u.username ASC
            LIMIT ?
        '''
        
        cursor.execute(query, (limit,))
        leaderboard = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return leaderboard 