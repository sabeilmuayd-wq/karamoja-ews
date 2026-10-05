# ===================================================================
# نظام الإنذار المبكر لكاراموجا - قاعدة البيانات
# ===================================================================
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path='karamoja.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS villages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                district TEXT NOT NULL,
                population INTEGER NOT NULL,
                food_stock_kg REAL DEFAULT 0,
                days_since_rain INTEGER DEFAULT 0,
                last_aid_date TEXT,
                created_at TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS aid_distributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                village_id INTEGER,
                amount_kg REAL,
                distributed_at TEXT,
                risk_score REAL,
                FOREIGN KEY (village_id) REFERENCES villages(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ تم تهيئة قاعدة البيانات")
    
    def add_village(self, name, district, population, food_stock_kg=0, days_since_rain=0):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO villages (name, district, population, food_stock_kg, days_since_rain, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, district, population, food_stock_kg, days_since_rain, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return {"success": True}
    
    def get_all_villages(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM villages')
        rows = c.fetchall()
        conn.close()
        return rows
    
    def get_village(self, village_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM villages WHERE id = ?', (village_id,))
        row = c.fetchone()
        conn.close()
        return row
    
    def update_village(self, village_id, food_stock_kg=None, days_since_rain=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if food_stock_kg is not None:
            c.execute('UPDATE villages SET food_stock_kg = ? WHERE id = ?', (food_stock_kg, village_id))
        if days_since_rain is not None:
            c.execute('UPDATE villages SET days_since_rain = ? WHERE id = ?', (days_since_rain, village_id))
        conn.commit()
        conn.close()
        return {"success": True}
    
    def record_distribution(self, village_id, amount_kg, risk_score):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO aid_distributions (village_id, amount_kg, distributed_at, risk_score)
            VALUES (?, ?, ?, ?)
        ''', (village_id, amount_kg, datetime.now().isoformat(), risk_score))
        conn.commit()
        conn.close()
    
    def get_distributions(self, limit=50):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT d.id, v.name, d.amount_kg, d.risk_score, d.distributed_at
            FROM aid_distributions d
            JOIN villages v ON d.village_id = v.id
            ORDER BY d.distributed_at DESC LIMIT ?
        ''', (limit,))
        rows = c.fetchall()
        conn.close()
        return rows
