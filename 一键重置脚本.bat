@echo off
chcp 65001 >nul
echo ========================================
echo 重置Git历史 - 移除大文件
echo ========================================
echo.
echo ⚠️  警告：这将删除所有Git历史记录
echo 但会保留你的所有文件
echo.
pause

echo [1/5] 删除Git历史...
if exist .git (
    rmdir /s /q .git
    echo ✅ Git历史已删除
) else (
    echo ✅ 没有Git历史
)
echo.

echo [2/5] 重新初始化Git...
git init
echo ✅ Git已重新初始化
echo.

echo [3/5] 配置Git用户信息...
git config user.name "Byeolyyy"
echo ✅ 用户名已设置
echo 请手动设置邮箱：git config user.email "your-email@example.com"
echo.

echo [4/5] 检查.gitignore文件...
if exist .gitignore (
    echo ✅ .gitignore文件存在
) else (
    echo ⚠️  .gitignore文件不存在
)
echo.

echo [5/5] 准备添加文件...
echo.
echo 下一步操作：
echo 1. 设置邮箱：git config user.email "your-email@example.com"
echo 2. 添加文件：git add .
echo 3. 检查文件：git status （确认没有exe文件）
echo 4. 提交：git commit -m "Initial commit: PCBA检测系统"
echo 5. 添加远程：git remote add origin https://github.com/Byeolyyy/pcba-detection-system.git
echo 6. 推送：git branch -M main ^&^& git push -u origin main
echo.
pause

