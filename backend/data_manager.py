import json
import asyncio
import aiofiles
import os
from typing import List, Dict, Any
from pathlib import Path
from models import User
import datetime
import threading
from get_url import get_info
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
# from datetime import datetime
import pytz
lock = threading.Lock()
cont_list = [1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1011,1012]
Friday = []
class JSONDataManager:
    def __init__(self, data_file: str = "data/leaderboard.json"):
        self.data_file = data_file
        self.data_dir = Path("data")
        self.ensure_data_directory()
        import uvicorn
        scheduler = AsyncIOScheduler()
        
        # 使用上海时区（UTC+8）
        scheduler.add_job(
            self.update_data,
            trigger=CronTrigger(hour=12, minute=00, timezone='Asia/Shanghai'),
            id='daily_task',
            replace_existing=True
        )
        scheduler.start()
        print("调度器已启动，将在每天21:30执行任务")
        
    def ensure_data_directory(self):
        """确保数据目录存在"""
        self.data_dir.mkdir(exist_ok=True)
        

    async def read_data(self) -> List[Dict[str, Any]]:
        # with lock:
        if not os.path.exists(self.data_file):
            # lock.release()
            # print("11111")
            await self.update_data()
    #     # 如果文件不存在，创建默认数据
    #     default_data = await self.generate_sample_data()
    #     await self.write_data(default_data)
    #     return default_data
        try:
            async with aiofiles.open(self.data_file, 'r', encoding='utf-8') as f:
                # lock.acquire()
                # update_data()
                content = await f.read()
                result = json.loads(content) if content else []
                # lock.release()
                return result
        except (json.JSONDecodeError, FileNotFoundError):
            lock.release()
            return []
    
    async def write_data(self, data: List[Dict[str, Any]]) -> bool:
        with lock:
            try:
                if os.path.exists(self.data_file):
                    os.rename(self.data_file,"data/leaderboard" + str(datetime.date.today()) + ".json" )

                async with aiofiles.open(self.data_file, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=2))
                return True
            except Exception as e:
                print(f"写入数据失败: {e}")
                return False
    
    async def update_data(self):
        # 将字符串转换为datetime对象
        # contest_list = [(1001,0),(1002,0),(1003,0),(1004,0),(1005,0),(1006,0),(1007,0),(1008,0)]
        d1 = datetime.datetime.strptime('2025-08-23', '%Y-%m-%d')
        d2 = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
        print(str(datetime.date.today()))
        # 计算两个日期之间的差值
        delta = int(str(d2 - d1).split()[0]) - 1
        # print(delta)
        users = []
        if os.path.exists(self.data_file):
            users = await self.read_data()
        uid = cont_list[delta]
        # print(user)
        # print(uid)
        info = get_info(uid)
        # print(info)
        if uid not in Friday:
            At = ""
            Bt = ""
            Ct = ""
            print(uid)
            for role in info:
                if (role['A'] != "" and role['A'] != "-" and At == "") or (role['A'] != "" and role['A'] != "-" and At > role['A']):
                    At = role['A']
                if (role['B'] != "" and role['B'] != "-" and Bt == "") or (role['B'] != "" and role['B'] != "-" and Bt > role['B']):
                    Bt = role['B']
                if (role['C'] != "" and role['C'] != "-" and Ct == "") or (role['C'] != "" and role['C'] != "-" and Ct >  role['C']):
                    # print(role)
                    Ct = role['C']
            print(At)
            print(Bt)
            print(Ct)
            for role in info:
                
                
                fenshu = 0
                ok = 0
                tishu = 0
                if role['A'] == '-':
                    fenshu += 1
                elif role['A'] != "":
                    fenshu += 5
                    tishu += 1

                if role['A'] == At:
                    fenshu += 5

                if role['B'] == '-':
                    fenshu += 1
                elif role['B'] != "":
                    fenshu += 5
                    tishu += 1
                if role['B'] == Bt:
                    fenshu += 5

                if role['C'] == '-':
                    fenshu += 1
                elif role['C'] != "":
                    fenshu += 10
                    tishu += 1
                if role['C'] == Ct:
                    fenshu += 5    
            
                for user in users:
                    if user['id'] == role['用户']:
                        ok = 1
                        user['basescore'] += fenshu
                        if tishu == 3:
                            user['DayInfo'] += '1'
                        else:
                            user['DayInfo'] += '0'
                        break;
                if ok == 0:
                    user = {
                        "id":role['用户'],
                        "name":role['昵称'],
                        "score": 0,
                        "trend": 'up',
                        "contestsocre":0,
                        "ishaveseven":False,
                        "basescore":0,
                        "DayInfo":"",
                        "rank":-1
                    }
                    user['basescore'] = fenshu
                    if tishu == 3:
                        user['DayInfo'] = '1'
                    else :
                        user['DayInfo'] = '0'
                    users.append(user)
            for user in users:
                user['score'] = user['contestsocre'] + user['basescore']
                if user['ishaveseven'] == True:
                    user['score'] += 20
                # print(user) 
                elif len(user['DayInfo'])>=7 and str(user['DayInfo']).find("1111111") != -1:
                    user['ishaveseven'] = True
                    user['score'] += 20
            users.sort(key=lambda x: x['score'], reverse=True)
            idx = 0
            pre = 0
            prerank = 0
            for i, user in enumerate(users):
                idx += 1
                prefab = int(user['rank'])
                if user['score'] == pre:
                    user['rank'] = prerank   
                else :
                    user['rank'] = idx
                pre = user['score']
                prerank = user['rank']
                if prefab > user['rank']:
                    user['trend'] = 'up'
                elif prefab < user['rank']:
                    user['trend'] = 'down'
                else:
                    user['trend'] = 'neutral'
            
            await self.write_data(users)
            return
        else:
            return
        


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
    
    
    async def search_users(self, search_term: str) -> List[Dict[str, Any]]:
        """搜索用户"""
        users = await self.read_data()
        if not search_term:
            return users
            
        return [user for user in users if search_term.lower() in user['id'].lower()]
    
    async def get_paginated_users(self, page: int, page_size: int, sort_by: str, search: str = None) -> Dict[str, Any]:
        """获取分页用户数据"""
        # await data_manager.update_data()
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
# asyncio.run(data_manager.update_data())
