# FreshTrainBoard
## 后端启动方法
``` C++
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 端口1
```
## 前端启动方法
```C++
    cd frontend
    python3 -m http.server 端口2
```
## 部署方案
**使用Systemd方案部署**
- 1. 首先创建服务文件
    创建后端服务文件：
```bash
    sudo nano /etc/systemd/system/fresh-train-backend.service
```
    粘贴以下内容
```bash
    [Unit]
    Description=Fresh Train Backend Service
    After=network.target

    [Service]
    User=root
    WorkingDirectory=/root/FreshTrainBoard/backend #后端代码位置
    ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 9000 #uvicorn安装位置 通过which uvicorn获得
    Restart=always
    RestartSec=10
    Environment=PYTHONUNBUFFERED=1

    [Install]
    WantedBy=multi-user.target
```
    创建前端服务文件
``` bash
    sudo nano /etc/systemd/system/fresh-train-frontend.service
```
    粘贴以下内容
``` bash
    [Unit]
    Description=Fresh Train Frontend Service
    After=network.target

    [Service]
    User=root
    WorkingDirectory=/root/FreshTrainBoard/frontend
    ExecStart=/usr/bin/python3 -m http.server 9001
    Restart=always
    RestartSec=10
    Environment=PYTHONUNBUFFERED=1

    [Install]
    WantedBy=multi-user.target
```
- 2. 重新加载systemd并启动服务
```bash
    # 重新加载systemd配置
    sudo systemctl daemon-reload

    # 启动后端服务
    sudo systemctl start fresh-train-backend

    # 启动前端服务  
    sudo systemctl start fresh-train-frontend

    # 设置开机自启动
    sudo systemctl enable fresh-train-backend
    sudo systemctl enable fresh-train-frontend
```
- 3. 检查服务状态
```bash
    # 查看后端状态
    sudo systemctl status fresh-train-backend

    # 查看前端状态
    sudo systemctl status fresh-train-frontend

    # 查看日志
    sudo journalctl -u fresh-train-backend -f
    sudo journalctl -u fresh-train-frontend -f
```
- 4. 常用管理命令
``` bash
    # 重启服务
    sudo systemctl restart fresh-train-backend
    sudo systemctl restart fresh-train-frontend
    
    # 停止服务
    sudo systemctl stop fresh-train-backend
    sudo systemctl stop fresh-train-frontend
    
    # 查看服务状态
    sudo systemctl status fresh-train-backend
    sudo systemctl status fresh-train-frontend
```