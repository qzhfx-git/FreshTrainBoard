from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime

from models import User, LeaderboardResponse, UserCreate, UserUpdate
from data_manager import data_manager
from get_url import get_info

Day_List = ["1001","1002","1003","1004"]
Constest_List = []

# 初始化应用
app = FastAPI(
    title="排行榜API - JSON版本",
    description="使用JSON文件存储数据的排行榜API",
    version="1.0.0"
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "排行榜API服务已启动 (JSON版本)",
        "version": "1.0.0",
        "storage": "JSON文件",
        "data_file": data_manager.data_file
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "leaderboard-api", "storage": "json"}

@app.get("/api/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(10, ge=1, le=100, description="每页数量"),
    sortBy: str = Query("score", description="排序字段: score或progress"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    try:
        get_userinfo()
        result = await data_manager.get_paginated_users(page, pageSize, sortBy, search)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")

@app.get("/api/users", response_model=List[User])
async def get_all_users():
    """获取所有用户"""
    try:
        users = await data_manager.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")

@app.get("/api/user/{user_id}", response_model=User)
async def get_user(user_id: int):
    """获取单个用户信息"""
    try:
        user = await data_manager.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

@app.post("/api/user", response_model=User)
async def create_user(user_data: UserCreate):
    """创建新用户"""
    try:
        user_dict = user_data.dict()
        user = await data_manager.create_user(user_dict)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@app.put("/api/user/{user_id}", response_model=User)
async def update_user(user_id: int, user_data: UserUpdate):
    """更新用户信息"""
    try:
        # 检查用户是否存在
        existing_user = await data_manager.get_user(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        update_dict = {k: v for k, v in user_data.dict().items() if v is not None}
        user = await data_manager.update_user(user_id, update_dict)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户失败: {str(e)}")

def get_userinfo():
    now_list = get_info(1001)
    print(now_list[0])
    print(now_list[1])
    print(now_list[2])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=12321, reload=True)