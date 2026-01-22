/**
 * 主页面逻辑
 */

// 上传图片
async function uploadImage() {
    const fileInput = document.getElementById('imageInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('请先选择图片文件');
        return;
    }
    
    // 显示预览
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('originalPreview');
        preview.innerHTML = `<img src="${e.target.result}" class="img-fluid" alt="原始图片">`;
    };
    reader.readAsDataURL(file);
    
    // 显示加载状态
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadBtnText = document.getElementById('uploadBtnText');
    const uploadSpinner = document.getElementById('uploadSpinner');
    
    uploadBtn.disabled = true;
    uploadBtnText.textContent = '检测中...';
    uploadSpinner.classList.remove('d-none');
    
    const resultPreview = document.getElementById('resultPreview');
    resultPreview.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">正在检测...</p></div>';
    
    try {
        const result = await API.detectImage(file);
        
        if (result.success) {
            // 显示检测结果图
            if (result.data.result_image_url) {
                resultPreview.innerHTML = `<img src="${result.data.result_image_url}" class="img-fluid" alt="检测结果">`;
            }
            
            // 显示检测详情
            displayDetectionDetails(result.data.detections);
            
            alert('检测完成！');
        } else {
            alert(`检测失败: ${result.message}`);
            resultPreview.innerHTML = '<p class="text-danger text-center">检测失败</p>';
        }
    } catch (error) {
        console.error('检测错误:', error);
        alert('检测过程中发生错误，请稍后重试');
        resultPreview.innerHTML = '<p class="text-danger text-center">检测出错</p>';
    } finally {
        uploadBtn.disabled = false;
        uploadBtnText.textContent = '开始检测';
        uploadSpinner.classList.add('d-none');
    }
}

// 显示检测详情
function displayDetectionDetails(detections) {
    const detailsCard = document.getElementById('detectionDetails');
    const tableBody = document.getElementById('detectionTableBody');
    
    if (!detections || detections.length === 0) {
        detailsCard.style.display = 'none';
        return;
    }
    
    detailsCard.style.display = 'block';
    tableBody.innerHTML = '';
    
    detections.forEach((detection, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${detection.defect_name}</td>
            <td>${detection.defect_code}</td>
            <td>${detection.confidence}%</td>
            <td>(${detection.x1}, ${detection.y1}) - (${detection.x2}, ${detection.y2})</td>
        `;
        tableBody.appendChild(row);
    });
}

// 页面加载完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('PCBA检测系统已加载');
});

