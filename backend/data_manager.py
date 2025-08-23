import json
import aiofiles
import os
from typing import List, Dict, Any
from pathlib import Path
from models import User

class JSONDataManager:
    def __init__(self, data_file: str = "data/leaderboard.json"):
        self.data_file = data_file
        self.data_dir = Path("data")
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        """确保数据目录存在"""
        self.data_dir.mkdir(exist_ok=True)
        
    async def read_data(self) -> List[Dict[str, Any]]:
        """读取JSON数据"""
        if not os.path.exists(self.data_file):
            # 如果文件不存在，创建默认数据
            default_data = await self.generate_sample_data()
            await self.write_data(default_data)
            return default_data
            
        try:
            async with aiofiles.open(self.data_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content) if content else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    async def write_data(self, data: List[Dict[str, Any]]) -> bool:
        """写入JSON数据"""
        try:
            async with aiofiles.open(self.data_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            return True
        except Exception as e:
            print(f"写入数据失败: {e}")
            return False
    
    async def generate_sample_data(self) -> List[Dict[str, Any]]:
        """生成示例数据"""
        import random
        from datetime import datetime, timedelta
        
        names = ['小明', '小红', '小刚', '小李', '小张', '小王', '小陈', '小杨', 
                '小赵', '小钱', '小孙', '小周', '小吴', '小郑', '小冯']
        
        users = []
        for i in range(50):
            name_index = i % len(names)
            suffix = f"_{i//len(names)+1}" if i >= len(names) else ""
            name = names[name_index] + suffix
            
            user = {
                "id": str("2510" + str(random.randint(10000000,999999999))),
                "name": name,
                "score": random.randint(100, 10000),
                "progress": random.randint(0, 100),
                "trend": random.choice(['up', 'down', 'neutral']),
                "avatar": f"https://i.pravatar.cc/150?u={i+1000}",
                "last_updated": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
            }
            users.append(user)
        
        # 按分数排序
        users.sort(key=lambda x: x['score'], reverse=True)
        
        # 添加排名
        for i, user in enumerate(users):
            user['rank'] = i + 1
            
        return users
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        return await self.read_data()
    
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """获取单个用户"""
        users = await self.read_data()
        for user in users:
            if user['id'] == user_id:
                return user
        return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新用户"""
        users = await self.read_data()
        
        # 生成新ID
        new_id = max((user['id'] for user in users), default=0) + 1
        
        user = {
            "id": new_id,
            "name": user_data['name'],
            "score": user_data['score'],
            "progress": user_data['progress'],
            "trend": user_data.get('trend', 'neutral'),
            "avatar": user_data.get('avatar', f"https://i.pravatar.cc/150?u={new_id}"),
            "last_updated": datetime.now().isoformat(),
            "rank": None  # 将在排序后计算
        }
        
        users.append(user)
        # 重新排序并计算排名
        users.sort(key=lambda x: x['score'], reverse=True)
        for i, u in enumerate(users):
            u['rank'] = i + 1
        
        await self.write_data(users)
        return user
    
    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户"""
        users = await self.read_data()
        
        for user in users:
            if user['id'] == user_id:
                for key, value in update_data.items():
                    if value is not None and key in user:
                        user[key] = value
                user['last_updated'] = datetime.now().isoformat()
                break
        
        # 重新排序并计算排名
        users.sort(key=lambda x: x['score'], reverse=True)
        for i, user in enumerate(users):
            user['rank'] = i + 1
        
        await self.write_data(users)
        return await self.get_user(user_id)
    
    async def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        users = await self.read_data()
        users = [user for user in users if user['id'] != user_id]
        
        # 重新计算排名
        users.sort(key=lambda x: x['score'], reverse=True)
        for i, user in enumerate(users):
            user['rank'] = i + 1
        
        return await self.write_data(users)
    
    async def search_users(self, search_term: str) -> List[Dict[str, Any]]:
        """搜索用户"""
        users = await self.read_data()
        if not search_term:
            return users
            
        return [user for user in users if search_term.lower() in user['name'].lower()]
    
    async def get_paginated_users(self, page: int, page_size: int, sort_by: str, search: str = None) -> Dict[str, Any]:
        """获取分页用户数据"""
        users = await self.search_users(search) if search else await self.read_data()
        
        # 排序
        if sort_by == "progress":
            users.sort(key=lambda x: x['progress'], reverse=True)
        else:  # 默认按分数排序
            users.sort(key=lambda x: x['score'], reverse=True)
        
        total_count = len(users)
        total_pages = (total_count + page_size - 1) // page_size
        
        # 分页
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_users = users[start_index:end_index]
        
        return {
            "data": paginated_users,
            "totalCount": total_count,
            "page": page,
            "pageSize": page_size,
            "totalPages": total_pages
        }

# 创建全局数据管理器实例
data_manager = JSONDataManager()