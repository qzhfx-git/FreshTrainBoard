
// API服务配置
// const API_BASE_URL = 'http://localhost:12321';
const API_BASE_URL = 'http://106.13.45.150:9000';

// 全局控制器引用
let controller = null;

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

    showError(message) {
        this.rankingItems.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        ${message}
                        <div class="mt-3">
                            <button class="btn btn-primary me-2" id="retry-btn">
                                <i class="fas fa-sync-alt me-1"></i>重试
                            </button>
                            <button class="btn btn-outline-secondary" id="check-server-btn">
                                <i class="fas fa-server me-1"></i>检查服务器状态
                            </button>
                        </div>
                    </div>
                `;

        // 动态添加事件监听器
        document.getElementById('retry-btn').addEventListener('click', () => {
            if (controller) controller.refreshData();
        });

        document.getElementById('check-server-btn').addEventListener('click', () => {
            if (controller) controller.checkServerStatus();
        });
    }

    showEmpty() {
        this.rankingItems.innerHTML = `
                    <div class="empty-message">
                        <i class="fas fa-info-circle me-2"></i>
                        没有找到相关学生数据
                    </div>
                `;
    }

    renderRankingList(data) {
        if (!data || data.length === 0) {
            this.showEmpty();
            return;
        }

        let html = '';
        data.forEach(item => {
            let rankClass = '';
            if (item.rank === 1) rankClass = 'top-1';
            else if (item.rank === 2) rankClass = 'top-2';
            else if (item.rank === 3) rankClass = 'top-3';

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

            const initials = item.name ? item.name.charAt(0).toUpperCase() : '?';

            html += `
                    <div class="ranking-item">
                    <div class="rank ${rankClass}">${item.rank}</div>
                    <div class="xuehao">${item.id.toLocaleString()}</div>
                    <div class="user-info">
                        <span class="username">${item.name} ${item.rank <= 3 ? '<span class="badge bg-warning">TOP</span>' : ''}</span>
                    </div>
                    <div class="score">${item.score.toLocaleString()}</div>
                    <div class="trend ${trendClass}">${trendIcon}</div>
                </div>
            `;
        });

        this.rankingItems.innerHTML = html;
    }

    renderPagination(currentPage, totalPages, totalCount, itemsPerPage) {
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
                            onclick="window.handlePageChange(${currentPage - 1})">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                `;

        // 添加页码按钮
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, startPage + 4);

        for (let i = startPage; i <= endPage; i++) {
            html += `
                        <button class="btn ${i === currentPage ? 'btn-primary' : 'btn-outline-primary'} mx-1" 
                                onclick="window.handlePageChange(${i})">
                            ${i}
                        </button>
                    `;
        }

        // 添加下一页按钮
        html += `
                    <button class="btn btn-outline-primary ${currentPage === totalPages ? 'disabled' : ''}" 
                            ${currentPage === totalPages ? 'disabled' : ''}
                            onclick="window.handlePageChange(${currentPage + 1})">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                `;

        this.pagination.innerHTML = html;
    }

    showServerStatus(isOnline) {
        const header = document.querySelector('.app-header p');
        if (isOnline) {
            header.innerHTML = '基于Python FastAPI后端 | <span class="badge bg-success">服务器在线</span>';
        } else {
            header.innerHTML = '基于Python FastAPI后端 | <span class="badge bg-danger">服务器离线</span>';
        }
    }

    updateLastRefreshTime(timeString) {
        const refreshInfo = document.getElementById('refresh-info');
        if (refreshInfo) {
            refreshInfo.textContent = `最后更新: ${timeString}`;
        }
    }
}

// 控制器
class LeaderboardController {
    constructor(model, view) {
        this.model = model;
        this.view = view;
        this.initEventListeners();
        this.init();
    }

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


        document.getElementById('items-per-page').addEventListener('change', () => {
            this.handleItemsPerPageChange();
        });
    }

    async init() {
        this.view.showLoading();
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

    async refreshData() {
        this.view.showLoading();
        const result = await this.model.fetchData();

        if (result.success) {
            this.updateView();
            this.updateLastRefreshTime();
        } else {
            this.view.showError(result.error);
        }
    }

    async checkServerStatus() {
        const isOnline = await LeaderboardAPI.healthCheck();
        this.view.showServerStatus(isOnline);

        if (isOnline) {
            await this.refreshData();
        } else {
            alert('服务器仍然离线，请检查后端服务是否启动');
        }
    }

    updateLastRefreshTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        this.view.updateLastRefreshTime(timeString);
    }

    async handleSearch() {
        const searchTerm = document.getElementById('search-input').value;
        this.model.searchTerm = searchTerm;
        this.model.currentPage = 1;

        await this.refreshData();
    }

    async handleReset() {
        document.getElementById('search-input').value = '';
        this.model.searchTerm = '';

        this.model.sortField = 'score';
        this.model.itemsPerPage = 10;
        this.model.currentPage = 1;

        await this.refreshData();
    }



    async handleItemsPerPageChange() {
        const itemsPerPage = parseInt(document.getElementById('items-per-page').value);
        this.model.itemsPerPage = itemsPerPage;
        this.model.currentPage = 1;

        await this.refreshData();
    }

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

// 全局函数供HTML调用
window.handlePageChange = function (page) {
    if (controller) {
        controller.handlePageChange(page);
    }
};

// 初始化应用
document.addEventListener('DOMContentLoaded', function () {
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

    setTimeout(async () => {
        try {
            const model = new LeaderboardModel();
            const view = new LeaderboardView();
            controller = new LeaderboardController(model, view);

            // 存储到全局变量以便调试
            window.leaderboardApp = { model, view, controller };

            // 移除加载动画
            loadingElement.remove();

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