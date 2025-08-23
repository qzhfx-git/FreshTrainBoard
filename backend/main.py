from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime

from models import User, LeaderboardResponse, UserCreate, UserUpdate
from data_manager import data_manager

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

@app.delete("/api/user/{user_id}")
async def delete_user(user_id: int):
    """删除用户"""
    try:
        # 检查用户是否存在
        existing_user = await data_manager.get_user(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        success = await data_manager.delete_user(user_id)
        if success:
            return {"message": "用户删除成功", "user_id": user_id}
        else:
            raise HTTPException(status_code=500, detail="删除用户失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")

@app.post("/api/reset-data")
async def reset_data():
    """重置为示例数据（开发用）"""
    try:
        sample_data = await data_manager.generate_sample_data()
        success = await data_manager.write_data(sample_data)
        if success:
            return {"message": "数据重置成功", "count": len(sample_data)}
        else:
            raise HTTPException(status_code=500, detail="重置数据失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置数据失败: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """获取统计信息"""
    try:
        users = await data_manager.get_all_users()
        total_users = len(users)
        avg_score = sum(user['score'] for user in users) / total_users if total_users > 0 else 0
        avg_progress = sum(user['progress'] for user in users) / total_users if total_users > 0 else 0
        
        return {
            "total_users": total_users,
            "average_score": round(avg_score, 2),
            "average_progress": round(avg_progress, 2),
            "data_file": data_manager.data_file,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)