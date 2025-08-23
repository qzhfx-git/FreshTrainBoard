import requests
from bs4 import BeautifulSoup
import re
import time
import json
from typing import List, Dict, Any
from collections import defaultdict

def advanced_acm_scraper_to_dict(contest_url: str) -> Dict[str, Any]:
    """
    高级版ACM竞赛榜单爬虫，返回结构化的字典数据
    
    返回格式:
    {
        "contest_info": {
            "url": "...",
            "cid": "...",
            "scrape_time": "..."
        },
        "headers": ["排名", "队伍", "解题数", ...],
        "teams": [
            {
                "rank": "1",
                "team": "Team A",
                "solved": "5",
                "total_time": "300",
                "problems": {
                    "A": {"attempts": "1", "time": "50", "solved": True},
                    "B": {"attempts": "2", "time": "100", "solved": True},
                    ...
                }
            },
            ...
        ],
        "statistics": {
            "total_teams": 50,
            "average_solved": 3.2,
            ...
        }
    }
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"正在获取 {contest_url} ...")
        response = requests.get(contest_url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找排名表格
        table = soup.find('table', {'id': 'rank-table'})
        if not table:
            tables = soup.find_all('table')
            table = tables[0] if tables else None
        
        if not table:
            raise Exception("无法找到排名表格")
        
            # 查找表头行
        header_row = table.find('thead').find('tr') if table.find('thead') else table.find('tr')
        
        # 提取表头文本
        headers = []
        if header_row:
            # 提取所有<th>元素
            td_headers = [td.text.strip() for td in header_row.find_all('td')]
            th_headers = [th.text.strip() for th in header_row.find_all('th')]
            # 提取所有<td>元素（如果存在）
            # 合并结果
            headers = td_headers + th_headers
            # 清理多余空格
            headers = [re.sub(r'\s+', ' ', h) for h in headers]
        print(headers)
        # 构建结果字典
        result = {
            "contest_info": {
                "url": contest_url,
                "scrape_time": time.strftime('%Y-%m-%d %H:%M:%S')
            },
            "headers": headers,
            "teams": [],
            "statistics": defaultdict(int)
        }
        
        # 提取CID
        cid_match = re.search(r'cid=(\d+)', contest_url)
        if cid_match:
            result["contest_info"]["cid"] = cid_match.group(1)
        
        # 处理数据行
        rows = table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr')[1:]
        
        for row in rows:
            cells = [td.text.strip() for td in row.find_all('td')]
            cells = [re.sub(r'\s+', ' ', cell) for cell in cells]
            
            if not any(cells):
                continue
            
            # 创建队伍字典
            team_dict = {}
            for i, header in enumerate(headers):
                if i < len(cells):
                    team_dict[header] = cells[i]
                else:
                    team_dict[header] = ""
            
            # 添加到结果中
            result["teams"].append(team_dict)
        
        # 计算统计信息
        result["statistics"]["total_teams"] = len(result["teams"])
        
        
        return result
        
    except Exception as e:
        print(f"爬取失败: {str(e)}")
        return {"error": str(e)}



zmb = ['A','B','C']
def process_team_data(team_dict: Dict[str, Any],result_list) -> Dict[str, Any]:
    """
    处理单个队伍的数据，提取更详细的信息
    """
    processed = team_dict.copy()
    
    s = str(processed['用户'])
    if s.find('2510') == -1 or len(s) != 10:
        return
    for key in zmb:
        if len(str(processed[key])) == 0:
            processed[key] = '-'
        elif str(processed[key])[0] == '-':
            processed[key] = '-'
        else :
            processed[key] = str(processed[key])[len(str(processed[key])) - 8:len(str(processed[key]))]
    result_list.append(processed.copy())
    # # 尝试解析解题详情（如果有的话）
    # # 这里需要根据实际网页结构调整解析逻辑
    # for key, value in team_dict.items():

    #     if key in ["排名", "Rank"]:
    #         processed["rank_int"] = int(value) if value.isdigit() else -1
    #     elif key in ["解题数", "Solved"]:
    #         processed["solved_int"] = int(value) if value.isdigit() else 0
    #     elif key in ["用时", "Time", "总用时"]:
    #         # 尝试解析时间
    #         time_match = re.search(r'(\d+)', value)
    #         if time_match:
    #             processed["time_int"] = int(time_match.group(1))
    
    # return processed

# 使用示例
def get_info(id:int):
    contest_url = "http://106.13.45.150/contestrank.php?cid="
    contest_url += str(id)
    result_list = []
    # 使用高级版爬虫
    contest_data = advanced_acm_scraper_to_dict(contest_url)
    
    if "error" not in contest_data:
        print("爬取成功!")
        print(f"竞赛ID: {contest_data['contest_info'].get('cid', '未知')}")
        print(f"队伍数量: {contest_data['statistics']['total_teams']}")
        
        if 'average_solved' in contest_data['statistics']:
            print(f"平均解题数: {contest_data['statistics']['average_solved']:.2f}")

        
        # 处理每支队伍的数据
        processed_teams = [process_team_data(team,result_list) for team in contest_data['teams']]
        print(result_list[0])
        print(result_list[1])
        print(result_list[2])
        print(result_list[91])
        # print(f"已处理 {len(processed_teams)} 支队伍的数据")
        return result_list
    else:
        print(f"爬取失败: {contest_data['error']}")
