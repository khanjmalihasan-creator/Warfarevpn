import sqlite3
import datetime

class Database:
    def __init__(self, db_name='vpn_shop.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # جدول کاربران
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    joined_date TEXT,
                    balance INTEGER DEFAULT 0,
                    is_admin INTEGER DEFAULT 0
                )
            ''')
            
            # جدول سفارشات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    plan TEXT,
                    amount INTEGER,
                    status TEXT DEFAULT 'pending',
                    payment_id TEXT,
                    created_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # جدول اکانت‌های VPN
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vpn_accounts (
                    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    config TEXT,
                    expiry_date TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
    
    def add_user(self, user_id, username, first_name):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, datetime.datetime.now()))
            conn.commit()
    
    def get_user(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()
    
    def create_order(self, user_id, plan, amount):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (user_id, plan, amount, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, plan, amount, datetime.datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def update_order_status(self, order_id, status, payment_id=None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if payment_id:
                cursor.execute('''
                    UPDATE orders SET status = ?, payment_id = ? WHERE order_id = ?
                ''', (status, payment_id, order_id))
            else:
                cursor.execute('''
                    UPDATE orders SET status = ? WHERE order_id = ?
                ''', (status, order_id))
            conn.commit()
    
    def add_vpn_account(self, user_id, config, days):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            expiry = datetime.datetime.now() + datetime.timedelta(days=days)
            cursor.execute('''
                INSERT INTO vpn_accounts (user_id, config, expiry_date)
                VALUES (?, ?, ?)
            ''', (user_id, config, expiry))
            conn.commit()
    
    def get_user_accounts(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM vpn_accounts 
                WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
            return cursor.fetchall()
