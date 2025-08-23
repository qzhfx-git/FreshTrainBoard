import sqlite3
import random

def init_db():
    """初始化数据库和示例数据"""
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    
    # 创建表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            progress INTEGER DEFAULT 0,
            trend TEXT DEFAULT 'neutral',
            avatar TEXT
        )
    ''')
    
    # 检查是否已有数据
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    
    if count == 0:
        # 插入示例数据
        names = ['小明', '小红', '小刚', '小李', '小张', '小王', '小陈', '小杨', '小赵', '小钱', 
                '小孙', '小周', '小吴', '小郑', '小冯', '小褚', '小卫', '小蒋', '小沈', '小韩']
        
        for i in range(100):
            name_index = i % len(names)
            suffix = f"_{i//len(names)+1}" if i >= len(names) else ""
            name = names[name_index] + suffix
            
            score = random.randint(100, 10000)
            progress = random.randint(0, 100)
            trend = random.choice(['up', 'down', 'neutral'])
            avatar = f"https://i.pravatar.cc/150?u={i+1000}"
            
            c.execute(
                "INSERT INTO users (id, name, score, progress, trend, avatar) VALUES (?, ?, ?, ?, ?, ?)",
                (i+1, name, score, progress, trend, avatar)
            )
    
    conn.commit()
    conn.close()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('leaderboard.db')
    conn.row_factory = sqlite3.Row
    return conn