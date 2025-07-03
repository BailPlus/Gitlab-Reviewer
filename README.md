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
  - POST /_/auth/login - 用户登录
  - POST /_/auth/logout - 用户登出
  - POST /_/auth/register - 用户注册
  - GET /_/auth/profile - 获取用户信息
  - PUT /_/auth/profile - 更新用户信息

- 仓库管理相关：
  - GET /api/repositories - 获取用户绑定的仓库列表
  - POST /api/repositories - 绑定新仓库
  - DELETE /api/repositories/{repo_id} - 解绑仓库
  - GET /api/repositories/{repo_id} - 获取仓库详情

- 仓库分析相关：
  - POST /api/repositories/{repo_id}/analyze - 对仓库进行宏观分析
  - GET /api/repositories/{repo_id}/analysis - 获取仓库分析结果
  - GET /api/repositories/{repo_id}/metrics - 获取仓库代码质量指标

- 提交评审相关：
  - POST /api/webhooks/gitlab - GitLab Webhook 接收端点
  - GET /api/commits/{commit_id}/review - 获取提交的 AI 评审结果
  - POST /api/commits/{commit_id}/review - 手动触发提交评审
  - PUT /api/commits/{commit_id}/review - 更新评审状态
  - POST /api/commits/{commit_id}/apply-suggestions - 一键应用修改建议

- 通知推送相关：
  - GET /api/notifications - 获取通知列表
  - POST /api/notifications/settings - 配置通知设置
  - PUT /api/notifications/settings - 更新通知设置
  - POST /api/notifications/test - 测试通知配置

- 系统管理相关：
  - GET /api/system/health - 系统健康检查
  - GET /api/system/stats - 系统统计信息

## 后端

- 技术栈：FastAPI
  
### 安装

```shell
conda create --name Gitlab-Reviewer python=3.12
```

```shell
conda activate Gitlab-Reviewer
```

```shell
pip install -r requirements.txt
```

### 数据库配置

数据库：MariaDB

#### `users` 表

| 列名             | 类型              | 可否为空 | 键   | 默认值                | 额外                           |
| -------------- | --------------- | ---- | --- | ------------------ | ---------------------------- |
| id             | BIGINT UNSIGNED | NO   | PRI |                    | AUTO\_INCREMENT              |
| username       | VARCHAR(50)     | NO   | UNI |                    |                              |
| password\_hash | VARCHAR(255)    | NO   |     |                    |                              |
| email          | VARCHAR(100)    | NO   | UNI |                    |                              |
| created\_at    | DATETIME        | NO   |     | CURRENT\_TIMESTAMP |                              |
| updated\_at    | DATETIME        | NO   |     | CURRENT\_TIMESTAMP | ON UPDATE CURRENT\_TIMESTAMP |

#### `repositories` 表

| 列名          | 类型              | 可否为空 | 键       | 默认值                | 额外              |
| ----------- | --------------- | ---- | ------- | ------------------ | --------------- |
| id          | BIGINT UNSIGNED | NO   | PRI     |                    | AUTO\_INCREMENT |
| user\_id    | BIGINT UNSIGNED | NO   | MUL(FK) |                    |                 |
| name        | VARCHAR(200)    | NO   |         |                    |                 |
| url         | VARCHAR(500)    | NO   |         |                    |                 |
| created\_at | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                 |
| bound\_at   | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                 |

#### `repository_analysis` 表

| 列名             | 类型              | 可否为空 | 键       | 默认值                | 额外              |
| -------------- | --------------- | ---- | ------- | ------------------ | --------------- |
| id             | BIGINT UNSIGNED | NO   | PRI     |                    | AUTO\_INCREMENT |
| repo\_id       | BIGINT UNSIGNED | NO   | MUL(FK) |                    |                 |
| analysis\_json | JSON            | NO   |         |                    |                 |
| created\_at    | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                 |

#### `repository_metrics` 表

| 列名             | 类型              | 可否为空 | 键       | 默认值 | 额外              |
| -------------- | --------------- | ---- | ------- | --- | --------------- |
| id             | BIGINT UNSIGNED | NO   | PRI     |     | AUTO\_INCREMENT |
| repo\_id       | BIGINT UNSIGNED | NO   | MUL(FK) |     |                 |
| metric\_date   | DATE            | NO   | UNI(复合) |     |                 |
| quality\_score | DECIMAL(5,2)    | YES  |         |     |                 |
| metrics\_json  | JSON            | YES  |         |     |                 |

#### `commits` 表

| 列名            | 类型              | 可否为空 | 键       | 默认值                | 额外              |
| ------------- | --------------- | ---- | ------- | ------------------ | --------------- |
| id            | BIGINT UNSIGNED | NO   | PRI     |                    | AUTO\_INCREMENT |
| repo\_id      | BIGINT UNSIGNED | NO   | MUL(FK) |                    |                 |
| commit\_hash  | VARCHAR(64)     | NO   | UNI(复合) |                    |                 |
| author\_name  | VARCHAR(100)    | YES  |         |                    |                 |
| author\_email | VARCHAR(100)    | YES  |         |                    |                 |
| message       | TEXT            | YES  |         |                    |                 |
| committed\_at | DATETIME        | YES  |         |                    |                 |
| created\_at   | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                 |

#### `commit_reviews` 表

| 列名           | 类型                                    | 可否为空 | 键       | 默认值                | 额外                           |
| ------------ | ------------------------------------- | ---- | ------- | ------------------ | ---------------------------- |
| id           | BIGINT UNSIGNED                       | NO   | PRI     |                    | AUTO\_INCREMENT              |
| commit\_id   | BIGINT UNSIGNED                       | NO   | UNI(FK) |                    |                              |
| review\_json | JSON                                  | NO   |         |                    |                              |
| status       | ENUM('pending','completed','applied') | NO   |         | pending            |                              |
| reviewed\_at | DATETIME                              | YES  |         |                    |                              |
| updated\_at  | DATETIME                              | NO   |         | CURRENT\_TIMESTAMP | ON UPDATE CURRENT\_TIMESTAMP |

#### `suggestions` 表

| 列名               | 类型              | 可否为空 | 键       | 默认值 | 额外              |
| ---------------- | --------------- | ---- | ------- | --- | --------------- |
| id               | BIGINT UNSIGNED | NO   | PRI     |     | AUTO\_INCREMENT |
| review\_id       | BIGINT UNSIGNED | NO   | MUL(FK) |     |                 |
| file\_path       | VARCHAR(500)    | YES  |         |     |                 |
| line\_number     | INT             | YES  |         |     |                 |
| suggestion\_text | TEXT            | NO   |         |     |                 |
| applied          | TINYINT(1)      | NO   |         | 0   |                 |
| applied\_at      | DATETIME        | YES  |         |     |                 |

#### `notification_settings` 表

| 列名                 | 类型              | 可否为空 | 键       | 默认值                | 额外                           |
| ------------------ | --------------- | ---- | ------- | ------------------ | ---------------------------- |
| id                 | BIGINT UNSIGNED | NO   | PRI     |                    | AUTO\_INCREMENT              |
| user\_id           | BIGINT UNSIGNED | NO   | UNI(FK) |                    |                              |
| via\_email         | TINYINT(1)      | NO   |         | 1                  |                              |
| email\_address     | VARCHAR(100)    | YES  |         |                    |                              |
| via\_telegram      | TINYINT(1)      | NO   |         | 0                  |                              |
| telegram\_chat\_id | VARCHAR(100)    | YES  |         |                    |                              |
| created\_at        | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                              |
| updated\_at        | DATETIME        | NO   |         | CURRENT\_TIMESTAMP | ON UPDATE CURRENT\_TIMESTAMP |

#### `notifications` 表

| 列名            | 类型              | 可否为空 | 键       | 默认值                | 额外              |
| ------------- | --------------- | ---- | ------- | ------------------ | --------------- |
| id            | BIGINT UNSIGNED | NO   | PRI     |                    | AUTO\_INCREMENT |
| user\_id      | BIGINT UNSIGNED | NO   | MUL(FK) |                    |                 |
| type          | VARCHAR(50)     | NO   |         |                    |                 |
| payload\_json | JSON            | NO   |         |                    |                 |
| is\_read      | TINYINT(1)      | NO   |         | 0                  |                 |
| created\_at   | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                 |

## 前端

- 技术栈: React + Next.js

### 安装

```shell
sudo apt install -y nodejs npm
```

```shell
npm install
```
