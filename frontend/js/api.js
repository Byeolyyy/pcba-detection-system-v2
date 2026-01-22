/**
 * API调用封装
 * 
 * 部署说明：
 * - 本地开发：使用 '/api'
 * - 生产环境：修改为你的Railway后端地址，例如：'https://your-app.railway.app/api'
 */
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? '/api'  // 本地开发
    : 'https://YOUR_RAILWAY_APP.railway.app/api';  // 生产环境 - 需要替换为你的Railway地址

class API {
    /**
     * 上传图片进行检测
     */
    static async detectImage(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/detect`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    }
    
    /**
     * 获取检测记录列表
     */
    static async getRecords(page = 1, perPage = 20, filters = {}) {
        const params = new URLSearchParams({
            page: page,
            per_page: perPage,
            ...filters
        });
        
        const response = await fetch(`${API_BASE_URL}/records?${params}`);
        return await response.json();
    }
    
    /**
     * 获取单条记录
     */
    static async getRecord(recordId) {
        const response = await fetch(`${API_BASE_URL}/records/${recordId}`);
        return await response.json();
    }
    
    /**
     * 删除记录
     */
    static async deleteRecord(recordId) {
        const response = await fetch(`${API_BASE_URL}/records/${recordId}`, {
            method: 'DELETE'
        });
        return await response.json();
    }
    
    /**
     * 获取统计信息
     */
    static async getStatistics() {
        const response = await fetch(`${API_BASE_URL}/statistics`);
        return await response.json();
    }
    
    /**
     * 获取结果图片URL
     */
    static getResultImageUrl(filename) {
        return `${API_BASE_URL}/result/${filename}`;
    }
    
    /**
     * 获取原图URL
     */
    static getOriginalImageUrl(filename) {
        return `${API_BASE_URL}/image/${filename}`;
    }
}
