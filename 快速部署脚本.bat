@echo off
chcp 65001 >nul
echo ========================================
echo PCBA检测系统 - GitHub部署脚本
echo ========================================
echo.

echo [1/4] 检查Git是否安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git未安装，请先安装Git: https://git-scm.com
    pause
    exit /b 1
)
echo ✅ Git已安装
echo.

echo [2/4] 检查是否已初始化Git仓库...
if not exist .git (
    echo 初始化Git仓库...
    git init
    echo ✅ Git仓库已初始化
) else (
    echo ✅ Git仓库已存在
)
echo.

echo [3/4] 添加文件到Git...
git add .
echo ✅ 文件已添加
echo.

echo [4/4] 提交更改...
git commit -m "Initial commit: PCBA检测系统" 2>nul
if errorlevel 1 (
    echo ⚠️  没有新文件需要提交，或已经提交过
) else (
    echo ✅ 文件已提交
)
echo.

echo ========================================
echo ✅ 本地Git准备完成！
echo ========================================
echo.
echo 下一步操作：
echo 1. 在GitHub创建新仓库
echo 2. 执行以下命令连接远程仓库：
echo    git remote add origin https://github.com/YOUR_USERNAME/pcba-detection-system.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. 在GitHub仓库设置中启用Pages（选择/frontend文件夹）
echo 4. 在Railway部署后端
echo.
echo 详细步骤请查看：部署步骤详细版.md
echo.
pause

