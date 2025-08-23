# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import random

app = FastAPI(title="排行榜API", description="提供排行榜数据接口")

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class User(BaseModel):
    id: int
    name: str
    score: int
    progress: int
    trend: str
    avatar: str
    rank: int

class LeaderboardResponse(BaseModel):
    data: List[User]
    totalCount: int
    page: int
    pageSize: int

# 初始化数据库
def init_db():
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
    
    # 插入示例数据
    names = ['小明', '小红', '小刚', '小李', '小张', '小王', '小陈', '小杨', '小赵', '小钱']
    
    for i in range(50):
        name_index = i % len(names)
        name = names[name_index] + (f"_{i//len(names)+1}" if i >= len(names) else "")
        
        c.execute(
            "INSERT OR IGNORE INTO users (id, name, score, progress, trend, avatar) VALUES (?, ?, ?, ?, ?, ?)",
            (i+1, name, random.randint(100, 10000), random.randint(0, 100), 
             random.choice(['up', 'down', 'neutral']), f"https://i.pravatar.cc/150?u={i}")
        )
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

@app.get("/api/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    sortBy: str = Query("score"),
    search: Optional[str] = Query(None)
):
    try:
        conn = sqlite3.connect('leaderboard.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # 构建查询
        query = "SELECT * FROM users"
        count_query = "SELECT COUNT(*) FROM users"
        params = []
        
        if search:
            query += " WHERE name LIKE ?"
            count_query += " WHERE name LIKE ?"
            params.append(f"%{search}%")
        
        # 排序
        if sortBy == "score":
            query += " ORDER BY score DESC"
        elif sortBy == "progress":
            query += " ORDER BY progress DESC"
        
        # 分页
        offset = (page - 1) * pageSize
        query += " LIMIT ? OFFSET ?"
        params.extend([pageSize, offset])
        
        # 获取总数
        if search:
            c.execute(count_query, [f"%{search}%"])
        else:
            c.execute(count_query)
        total_count = c.fetchone()[0]
        
        # 获取数据
        c.execute(query, params)
        rows = c.fetchall()
        
        # 转换为字典列表并添加排名
        users = []
        for i, row in enumerate(rows):
            user = dict(row)
            user['rank'] = (page - 1) * pageSize + i + 1
            users.append(user)
        
        conn.close()
        
        return LeaderboardResponse(
            data=users,
            totalCount=total_count,
            page=page,
            pageSize=pageSize
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)