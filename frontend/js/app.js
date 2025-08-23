// API服务配置
const API_BASE_URL = 'http://localhost:8000';

// API服务类
class LeaderboardAPI {
    static async getLeaderboard(page = 1, pageSize = 10, sortBy = 'score', searchTerm = '') {
        try {
            const params = new URLSearchParams({
                page: page,
                pageSize: pageSize,
                sortBy: sortBy,
                search: searchTerm
            });

            const response = await fetch(`${API_BASE_URL}/api/leaderboard?${params}`);

            if (!response.ok) {
                throw new Error(`HTTP错误! 状态码: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('获取排行榜数据失败:', error);
            throw error;
        }
    }

    static async healthCheck() {
        try {
            // 添加超时控制
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);

            const response = await fetch(`${API_BASE_URL}/api/health`, {
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            return response.ok;
        } catch (error) {
            console.warn('健康检查失败:', error);
            return false;
        }
    }
    static async fetchWithRetry(url, options = {}, retries = 3, delay = 1000) {
        for (let attempt = 1; attempt <= retries; attempt++) {
            try {
                const response = await fetch(url, options);
                if (response.ok) return response;

                if (attempt === retries) {
                    throw new Error(`HTTP错误: ${response.status}`);
                }
            } catch (error) {
                if (attempt === retries) {
                    throw error;
                }
                // 等待后重试
                await new Promise(resolve => setTimeout(resolve, delay * attempt));
            }
        }
    }

}

// 数据模型
class LeaderboardModel {
    constructor() {
        this.data = [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.sortField = 'score';
        this.searchTerm = '';
        this.totalCount = 0;
        this.totalPages = 0;
    }

    // 从API获取数据
    async fetchData() {
        try {
            const response = await LeaderboardAPI.getLeaderboard(
                this.currentPage,
                this.itemsPerPage,
                this.sortField,
                this.searchTerm
            );

            this.data = response.data;
            this.totalCount = response.totalCount;
            this.totalPages = response.totalPages;
            return { success: true };
        } catch (error) {
            console.error('数据获取失败:', error);
            return {
                success: false,
                error: error.message || '无法连接到服务器'
            };
        }
    }
}

// 视图渲染
class LeaderboardView {
    constructor() {
        this.rankingItems = document.getElementById('ranking-items');
        this.pagination = document.getElementById('pagination');
        this.paginationInfo = document.getElementById('pagination-info');
    }

    // 显示加载状态
    showLoading() {
        this.rankingItems.innerHTML = `
            <div class="loading">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
                <span class="ms-2">正在从Python后端加载数据...</span>
            </div>
        `;
    }

    // 显示错误信息
    showError(message) {
        this.rankingItems.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
                <div class="mt-3">
                    <button class="btn btn-primary me-2" onclick="controller.refreshData()">
                        <i class="fas fa-sync-alt me-1"></i>重试
                    </button>
                    <button class="btn btn-outline-secondary" onclick="controller.checkServerStatus()">
                        <i class="fas fa-server me-1"></i>检查服务器状态
                    </button>
                </div>
            </div>
        `;
    }

    // 显示空状态
    showEmpty() {
        this.rankingItems.innerHTML = `
            <div class="empty-message">
                <i class="fas fa-info-circle me-2"></i>
                没有找到相关数据
            </div>
        `;
    }

    // 渲染榜单
    renderRankingList(data) {
        if (!data || data.length === 0) {
            this.showEmpty();
            return;
        }

        let html = '';
        data.forEach(item => {
            // 根据排名设置样式
            let rankClass = '';
            if (item.rank === 1) rankClass = 'top-1';
            else if (item.rank === 2) rankClass = 'top-2';
            else if (item.rank === 3) rankClass = 'top-3';

            // 趋势图标
            let trendIcon = '';
            let trendClass = '';
            if (item.trend === 'up') {
                trendIcon = '<i class="fas fa-caret-up"></i>';
                trendClass = 'up';
            } else if (item.trend === 'down') {
                trendIcon = '<i class="fas fa-caret-down"></i>';
                trendClass = 'down';
            } else {
                trendIcon = '<i class="fas fa-minus"></i>';
                trendClass = 'neutral';
            }

            html += `
                <div class="ranking-item">
                    <div class="rank ${rankClass}">${item.rank}</div>
                    <div class="user-info">
                        <span class="username">${item.name} ${item.rank <= 3 ? '<span class="badge bg-warning">TOP</span>' : ''}</span>
                    </div>
                    <div class="id">${item.id.toLocaleString()}</div>
                    <div class="score">${item.score.toLocaleString()}</div>
                    <div class="trend ${trendClass}">${trendIcon}</div>
                </div>
            `;
        });

        this.rankingItems.innerHTML = html;
    }

    // 渲染分页信息和控件
    renderPagination(currentPage, totalPages, totalCount, itemsPerPage) {
        // 更新分页信息
        const startItem = (currentPage - 1) * itemsPerPage + 1;
        const endItem = Math.min(currentPage * itemsPerPage, totalCount);
        this.paginationInfo.textContent = `显示 ${startItem}-${endItem} 条，共 ${totalCount} 条`;

        if (totalPages <= 1) {
            this.pagination.innerHTML = '';
            return;
        }

        let html = '';

        // 添加上一页按钮
        html += `
            <button class="btn btn-outline-primary ${currentPage === 1 ? 'disabled' : ''}" 
                    ${currentPage === 1 ? 'disabled' : ''}
                    onclick="controller.handlePageChange(${currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;

        // 添加页码按钮
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, startPage + 4);

        for (let i = startPage; i <= endPage; i++) {
            html += `
                <button class="btn ${i === currentPage ? 'btn-primary' : 'btn-outline-primary'} mx-1" 
                        onclick="controller.handlePageChange(${i})">
                    ${i}
                </button>
            `;
        }

        // 添加下一页按钮
        html += `
            <button class="btn btn-outline-primary ${currentPage === totalPages ? 'disabled' : ''}" 
                    ${currentPage === totalPages ? 'disabled' : ''}
                    onclick="controller.handlePageChange(${currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;

        this.pagination.innerHTML = html;
    }

    // 显示服务器状态提示
    showServerStatus(isOnline) {
        const header = document.querySelector('.app-header p');
        if (isOnline) {
            header.innerHTML = '基于Python FastAPI后端 | <span class="badge bg-success">服务器在线</span>';
        } else {
            header.innerHTML = '基于Python FastAPI后端 | <span class="badge bg-danger">服务器离线</span>';
        }
    }
}

// 控制器
class LeaderboardController {
    constructor(model, view) {
        this.model = model;
        this.view = view;

        // 初始化事件监听
        this.initEventListeners();

        // 初始化数据
        this.init();
    }

    // 初始化事件监听
    initEventListeners() {
        document.getElementById('search-btn').addEventListener('click', () => {
            this.handleSearch();
        });

        document.getElementById('reset-btn').addEventListener('click', () => {
            this.handleReset();
        });

        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.refreshData();
        });

        document.getElementById('search-input').addEventListener('keyup', (e) => {
            if (e.key === 'Enter') {
                this.handleSearch();
            }
        });

        // document.getElementById('sort-by').addEventListener('change', () => {
        //     this.handleSort();
        // });

        document.getElementById('items-per-page').addEventListener('change', () => {
            this.handleItemsPerPageChange();
        });
    }

    // 初始化应用
    async init() {
        this.view.showLoading();

        // 清除API缓存
        await this.clearCache();

        const isOnline = await LeaderboardAPI.healthCheck();
        this.view.showServerStatus(isOnline);

        if (isOnline) {
            setTimeout(() => {
                this.refreshData();
            }, 500);
        } else {
            this.view.showError('无法连接到Python后端服务器，请确保服务器已启动');
        }
    }

    // 添加缓存清除方法
    async clearCache() {
        // 强制浏览器不使用缓存
        if ('caches' in window) {
            try {
                const cacheNames = await caches.keys();
                for (const name of cacheNames) {
                    await caches.delete(name);
                }
            } catch (error) {
                console.log('缓存清除失败:', error);
            }
        }
    }
    async refreshDataWithRetry(retries = 3, delay = 1000) {
        for (let attempt = 1; attempt <= retries; attempt++) {
            try {
                await this.refreshData();
                return true;
            } catch (error) {
                if (attempt === retries) {
                    this.view.showError(`数据加载失败: ${error.message}`);
                    return false;
                }
                // 等待后重试
                await new Promise(resolve => setTimeout(resolve, delay * attempt));
            }
        }
    }

    // 刷新数据
    async refreshData() {
        this.view.showLoading();
        const result = await this.model.fetchData();

        if (result.success) {
            this.updateView();

            // 更新最后刷新时间
            this.updateLastRefreshTime();
        } else {
            this.view.showError(result.error);
        }
    }

    // 检查服务器状态
    async checkServerStatus() {
        const isOnline = await LeaderboardAPI.healthCheck();
        this.view.showServerStatus(isOnline);

        if (isOnline) {
            await this.refreshData();
        } else {
            alert('服务器仍然离线，请检查后端服务是否启动');
        }
    }
    // 添加最后刷新时间显示
    updateLastRefreshTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();

        // 在页面某处显示刷新时间
        const refreshInfo = document.getElementById('refresh-info');
        if (refreshInfo) {
            refreshInfo.textContent = `最后更新: ${timeString}`;
        }
    }

    // 处理搜索
    async handleSearch() {
        const searchTerm = document.getElementById('search-input').value;
        this.model.searchTerm = searchTerm;
        this.model.currentPage = 1;

        await this.refreshData();
    }

    // 处理重置
    async handleReset() {
        document.getElementById('search-input').value = '';
        // document.getElementById('sort-by').value = 'score';
        document.getElementById('items-per-page').value = '10';

        this.model.searchTerm = '';
        this.model.sortField = 'score';
        this.model.itemsPerPage = 10;
        this.model.currentPage = 1;

        await this.refreshData();
    }

    // 处理排序
    // async handleSort() {
    //     const sortBy = document.getElementById('sort-by').value;
    //     this.model.sortField = sortBy;
    //     this.model.currentPage = 1;

    //     await this.refreshData();
    // }

    // 处理每页显示数量变化
    async handleItemsPerPageChange() {
        const itemsPerPage = parseInt(document.getElementById('items-per-page').value);
        this.model.itemsPerPage = itemsPerPage;
        this.model.currentPage = 1;

        await this.refreshData();
    }

    // 处理页码变化
    async handlePageChange(page) {
        this.model.currentPage = page;

        this.view.showLoading();
        const result = await this.model.fetchData();

        if (result.success) {
            this.updateView();
            window.scrollTo(0, 0);
        } else {
            this.view.showError(result.error);
        }
    }

    // 更新视图
    updateView() {
        this.view.renderRankingList(this.model.data);
        this.view.renderPagination(
            this.model.currentPage,
            this.model.totalPages,
            this.model.totalCount,
            this.model.itemsPerPage
        );
    }
}

// // 初始化应用
// const model = new LeaderboardModel();
// const view = new LeaderboardView();
// const controller = new LeaderboardController(model, view);
// 修改初始化代码，确保DOM完全加载后再执行
document.addEventListener('DOMContentLoaded', function () {
    // 添加加载动画
    const loadingElement = document.createElement('div');
    loadingElement.className = 'loading-overlay';
    loadingElement.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <p class="mt-2">正在初始化应用...</p>
        </div>
    `;
    document.body.appendChild(loadingElement);

    // 添加CSS样式
    const style = document.createElement('style');
    style.textContent = `
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        .loading-spinner {
            text-align: center;
        }
    `;
    document.head.appendChild(style);

    // 延迟初始化以确保一切就绪
    setTimeout(async () => {
        try {
            const model = new LeaderboardModel();
            const view = new LeaderboardView();
            const controller = new LeaderboardController(model, view);

            // 存储到全局变量以便调试
            window.leaderboardApp = { model, view, controller };

            // 移除加载动画
            loadingElement.remove();
            style.remove();

        } catch (error) {
            console.error('应用初始化失败:', error);
            loadingElement.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <h4>应用初始化失败</h4>
                    <p>${error.message}</p>
                    <button class="btn btn-primary mt-2" onclick="location.reload()">
                        重新加载页面
                    </button>
                </div>
            `;
        }
    }, 100);
});

// 添加页面可见性检测，当页面重新获得焦点时自动刷新
document.addEventListener('visibilitychange', function () {
    if (!document.hidden && window.leaderboardApp) {
        // 页面从后台切换到前台时自动刷新
        window.leaderboardApp.controller.refreshData();
    }
});

// 添加离线/在线检测
window.addEventListener('online', function () {
    if (window.leaderboardApp) {
        window.leaderboardApp.controller.view.showServerStatus(true);
        window.leaderboardApp.controller.refreshData();
    }
});

window.addEventListener('offline', function () {
    if (window.leaderboardApp) {
        window.leaderboardApp.controller.view.showServerStatus(false);
        window.leaderboardApp.controller.view.showError('网络连接已断开');
    }
});