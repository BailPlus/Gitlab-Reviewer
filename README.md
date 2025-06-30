# Gitlab-Reviewer
深圳共进电子出题：基于 AI 的 GitLab 自动代码评审系统
## 项目摘要

### 设计思路
- 借鉴 codex 和 deepwiki
- 可以绑定仓库，绑定之后可以由 AI 对项目进行在整体分析
- 对每次 git 提交评估，给出修改建业，可以一键发起 PR

### 基本功能
- 用户登陆
- 绑定仓库
- 宏观分析仓库
- 实时捕获 Gitlab 提交信息
- AI 分析提交，给出修改建议
- 消息推送，如 Telegram Bot，Email
- 一键应用修改建议

### API 设计
- 用户认证相关：
    - POST /_/auth/login
    - POST /_/auth/logout
    - 

## 后端
- 技术栈：FastAPI
### 安装
```
conda create --name Gitlab-Reviewer python=3.12
```
```
conda activate Gitlab-Reviewer
```
```
pip install -r requirements.txt
```

## 前端
- 技术栈: React
### 安装
```
sudo apt install -y nodejs npm
```
```
npm install
```