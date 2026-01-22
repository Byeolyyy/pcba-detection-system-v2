# GitHub部署完整指南

## 📋 部署方案

由于GitHub Pages只能托管静态文件，我们需要：
- **前端**：部署到GitHub Pages（免费）
- **后端**：部署到Railway或Render（免费额度）

## 🚀 第一步：创建GitHub仓库

1. 登录GitHub：https://github.com
2. 点击右上角 "+" → "New repository"
3. 仓库名称：`pcba-detection-system`（或你喜欢的名字）
4. 设置为 Public（GitHub Pages需要）
5. 不要勾选 "Initialize with README"
6. 点击 "Create repository"

## 📤 第二步：上传代码到GitHub

### 方法1：使用Git命令行（推荐）

```bash
# 1. 初始化Git仓库
git init

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Initial commit: PCBA检测系统"

# 4. 添加远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/pcba-detection-system.git

# 5. 推送到GitHub
git branch -M main
git push -u origin main
```

### 方法2：使用GitHub Desktop（图形界面）

1. 下载GitHub Desktop：https://desktop.github.com
2. 登录GitHub账号
3. File → Add Local Repository
4. 选择项目文件夹
5. 点击 "Publish repository"

## 🌐 第三步：部署前端到GitHub Pages

1. 进入GitHub仓库页面
2. 点击 "Settings"（设置）
3. 左侧菜单找到 "Pages"
4. Source选择 "Deploy from a branch"
5. Branch选择 "main"，文件夹选择 "/frontend"
6. 点击 "Save"
7. 等待几分钟，GitHub会生成网址：`https://YOUR_USERNAME.github.io/pcba-detection-system/`

## ☁️ 第四步：部署后端到Railway（推荐）

### 为什么选择Railway？
- ✅ 免费额度：$5/月
- ✅ 自动部署
- ✅ 简单易用
- ✅ 支持Python/Flask

### 部署步骤：

1. **注册Railway账号**
   - 访问：https://railway.app
   - 使用GitHub账号登录（推荐）

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库

3. **配置项目**
   - Railway会自动检测Flask项目
   - 如果需要，设置启动命令：`python run.py`
   - 设置端口：Railway会自动分配

4. **获取后端URL**
   - Railway会给你一个URL，例如：`https://your-app.railway.app`
   - 复制这个URL

## 🔧 第五步：修改前端API地址

需要修改前端代码，让它调用Railway的后端API：

1. 打开 `frontend/js/api.js`
2. 修改 `API_BASE_URL` 为你的Railway后端地址

## 📝 详细步骤文件

我已经为你创建了自动化脚本，继续看下面的文件。

