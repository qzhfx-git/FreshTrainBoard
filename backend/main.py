from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sqlite3
from contextlib import asynccontextmanager
from models import User, LeaderboardResponse
from database import init_db, get_db_connection

# 初始化应用
app = FastAPI(
    title="排行榜API",
    description="提供排行榜数据接口",
    version="1.0.0"
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时初始化数据库
@asynccontextmanager
def startup_event(app: FastAPI):
    init_db()

@app.get("/")
async def root():
    return {"message": "排行榜API服务已启动", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "leaderboard-api"}

@app.get("/api/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(10, ge=1, le=100, description="每页数量"),
    sortBy: str = Query("score", description="排序字段: score或progress"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    try:
        conn = get_db_connection()
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
        else:
            query += " ORDER BY score DESC"
        
        # 获取总数
        if search:
            c.execute(count_query, [f"%{search}%"])
        else:
            c.execute(count_query)
        total_count = c.fetchone()[0]
        
        # 分页
        offset = (page - 1) * pageSize
        query += " LIMIT ? OFFSET ?"
        params.extend([pageSize, offset])
        
        # 获取数据
        c.execute(query, params)
        rows = c.fetchall()
        
        # 转换为字典列表并添加排名
        users = []
        for i, row in enumerate(rows):
            user = dict(row)
            user['rank'] = (page - 1) * pageSize + i + 1
            users.append(User(**user))
        
        conn.close()
        
        total_pages = (total_count + pageSize - 1) // pageSize
        
        return LeaderboardResponse(
            data=users,
            totalCount=total_count,
            page=page,
            pageSize=pageSize,
            totalPages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@app.get("/api/user/{user_id}", response_model=User)
async def get_user(user_id: int):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        user = dict(row)
        
        # 计算排名
        c.execute("SELECT COUNT(*) FROM users WHERE score > ?", (user['score'],))
        rank = c.fetchone()[0] + 1
        user['rank'] = rank
        
        conn.close()
        
        return User(**user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)