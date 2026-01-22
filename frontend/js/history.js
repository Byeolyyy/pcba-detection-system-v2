/**
 * 历史记录页面逻辑
 */

let currentPage = 1;
const perPage = 20;

// 加载记录
async function loadRecords() {
    const defectName = document.getElementById('filterDefectName').value;
    const defectCode = document.getElementById('filterDefectCode').value;
    
    const filters = {};
    if (defectName) filters.defect_name = defectName;
    if (defectCode) filters.defect_code = defectCode;
    
    try {
        const result = await API.getRecords(currentPage, perPage, filters);
        
        if (result.success) {
            displayRecords(result.data.records);
            displayPagination(result.data);
            updateStatistics();
        } else {
            alert(`加载失败: ${result.message}`);
        }
    } catch (error) {
        console.error('加载记录错误:', error);
        alert('加载记录时发生错误');
    }
}

// 显示记录
function displayRecords(records) {
    const tableBody = document.getElementById('recordsTableBody');
    
    if (!records || records.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center">暂无记录</td></tr>';
        return;
    }
    
    tableBody.innerHTML = '';
    
    records.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.id}</td>
            <td>${record.defect_name}</td>
            <td>${record.defect_code || '-'}</td>
            <td>${record.confidence}%</td>
            <td>(${record.x1}, ${record.y1}) - (${record.x2}, ${record.y2})</td>
            <td>${record.created_at}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteRecord(${record.id})">删除</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// 显示分页
function displayPagination(data) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    if (data.pages <= 1) return;
    
    // 上一页
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${data.page === 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#" onclick="changePage(${data.page - 1}); return false;">上一页</a>`;
    pagination.appendChild(prevLi);
    
    // 页码
    for (let i = 1; i <= data.pages; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === data.page ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" onclick="changePage(${i}); return false;">${i}</a>`;
        pagination.appendChild(li);
    }
    
    // 下一页
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${data.page === data.pages ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#" onclick="changePage(${data.page + 1}); return false;">下一页</a>`;
    pagination.appendChild(nextLi);
}

// 切换页码
function changePage(page) {
    currentPage = page;
    loadRecords();
}

// 删除记录
async function deleteRecord(recordId) {
    if (!confirm('确定要删除这条记录吗？')) {
        return;
    }
    
    try {
        const result = await API.deleteRecord(recordId);
        
        if (result.success) {
            alert('删除成功');
            loadRecords();
        } else {
            alert(`删除失败: ${result.message}`);
        }
    } catch (error) {
        console.error('删除错误:', error);
        alert('删除时发生错误');
    }
}

// 更新统计信息
async function updateStatistics() {
    try {
        const result = await API.getStatistics();
        
        if (result.success) {
            const data = result.data;
            document.getElementById('totalRecords').textContent = data.total_records;
            document.getElementById('avgConfidence').textContent = data.avg_confidence + '%';
            document.getElementById('defectTypes').textContent = Object.keys(data.defect_types).length;
        }
    } catch (error) {
        console.error('加载统计信息错误:', error);
    }
}

// 重置筛选
function resetFilters() {
    document.getElementById('filterDefectName').value = '';
    document.getElementById('filterDefectCode').value = '';
    currentPage = 1;
    loadRecords();
}

// 页面加载完成
document.addEventListener('DOMContentLoaded', function() {
    loadRecords();
    updateStatistics();
});

