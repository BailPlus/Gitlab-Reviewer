# Gitlab-Reviewer

深圳共进电子出题：基于 AI 的 GitLab 自动代码评审系统

## 项目摘要

### 设计思路

- 借鉴 codex 和 deepwiki
- 可以绑定仓库，绑定之后可以由 AI 对项目进行在整体分析
- 对每次 git 提交评估，给出修改建议，可以一键发起 PR

### 基本功能

- 用户登陆
- 绑定仓库
- 宏观分析仓库
- 实时捕获 Gitlab 提交信息
- AI 分析提交，给出修改建议
- 消息推送，如 Telegram Bot，Email
- 一键应用修改建议

### API 设计

> 返回总体格式
```json
{
  "status": 0,
  "info": "ok",
  "data": {...}
}
```

- 用户认证相关：
  - Gitlab oauth login redirect
  ```http
  GET /_/auth/login
  ```
  ```
  Location: https://gitlab.com/oauth/authorize?client_id=???&redirect_uri=???&response_type=code&state=???
  ```
  - Gitlab oauth callback
  ```http
  GET /_/auth/callback?code=???
  ```
  ```http
  Set-Cookie: token=string
  Location: /
  ```
  - 用户登出
  ```http
  POST /_/auth/logout
  ```
  ```http
  Set-Cookie: token=; expires=Thu, 01 Jan 1970 00:00:00 GMT
  Location: /login

  ```
  
  - 获取用户信息
  ```http
  GET /_/auth/profile
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {
      "username": "string",
      "email": "string"
    }
  }
  ```

- 仓库管理相关：
  - 获取用户绑定的仓库列表
  ```http
  GET /api/repositories
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {
      "repositories": [{
        "id": 1,
        "name": "user1/repo1"
      }, ...]
    }
  }
  ```
  - 绑定新仓库
  ```http
  POST /api/repositories
  
  {
    "repo_name": "user1/repo1"
  }
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {}
  }
  ```
  - 解绑仓库
  ```http
  DELETE /api/repositories/{repo_id}
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {}
  }
  ```
- 仓库分析相关：
  - 对仓库进行宏观分析（异步请求）
  ```http
  POST /api/analysis

  {
    "repo_id": 1
  }
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {}
  }
  ```
  - 获取仓库分析结果以及仓库代码质量指标
  ```http
  GET /api/analysis/{analysis_id}
  ```
  ```json
  {
    "status": 0/301/302,
    "info": "ok/pending/failed",
    "data": {
      "result": "分析结果",
      "score": 0,
      "analize_time": 17xxxxxxxx
    }
  }
  ```
  - 获取分析结果历史
  ```http
  GET /api/analysis/history?repo_id=1' UNION SELECT flag FROM flag; -- -
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {
      "analisis_history": [3, 2, 1, ...] // 返回一组 analysis_id，按时间逆序排列
    }
  }
  ```

- commit评审相关：
  - POST /api/webhooks/gitlab - GitLab Webhook 接收端点
  - GET /api/commits/{commit_id}/review - 获取提交的 AI 评审结果
  - POST /api/commits/{commit_id}/review - 手动触发提交评审
  - PUT /api/commits/{commit_id}/review - 更新评审状态
  - POST /api/commits/{commit_id}/apply-suggestions - 一键应用修改建议

- 通知推送相关：
  - 获取通知设置
  ```http
  GET /api/notifications/settings
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {
      "notifications": {
      "email": {
        "enabled": true,
        "address": "user@example.com"
      },
      "telegram": {
        "enabled": true,
        "chat_id": "string"
      }
    }
  }
  ```
  - 配置通知设置
  ```http
  POST /api/notifications/settings
  
  {
    "notifications": {
      "email": {
        "enabled": true,
        "address": "user@example.com"
      },
      "telegram": {
        "enabled": true,
        "chat_id": "string"
      }
    }
  }
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {
        "notifications": {
        "email": {
          "enabled": true,
          "address": "user@example.com"
        },
        "telegram": {
          "enabled": true,
          "chat_id": "string"
        }
      }
    }
  }
  ```

  - 测试通知配置
  ```http
  POST /api/notifications/test
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {}
  }
  ```


## 后端

- 技术栈：FastAPI, MariaDB

### 安装

- anaconda
```shell
conda create --name Gitlab-Reviewer python=3.12
```

```shell
conda activate Gitlab-Reviewer
```

```shell
pip install -r requirements.txt
```

- uv
```shell
uv sync
uv run run.py
```

### 数据库配置

数据库：MariaDB

#### `tokens` 表

| 列名          | 类型             | 可否为空 | 键    | 默认值              | 额外                          |
| ------------ | ---------------- | ---- | ------- | ------------------ | ---------------------------- |
| token        | VARCHAR(64)      | NO   | PRI     |                    |                              |
| user\_id     | BIGINT UNSIGNED  | NO   | MUL(FK) |                    |                              |
| exp          | INTEGER          | NO   |         |                    |                              |
| created\_at   | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                              |
| updated\_at   | DATETIME        | NO   |         | CURRENT\_TIMESTAMP | ON UPDATE CURRENT\_TIMESTAMP |

#### `users` 表

| 列名             | 类型              | 可否为空 | 键   | 默认值                | 额外                           |
| -------------- | --------------- | ---- | --- | ------------------ | ---------------------------- |
| id             | BIGINT UNSIGNED | NO   | PRI |                    |                              |
| username       | VARCHAR(50)     | NO   | UNI |                    |                              |
| email          | VARCHAR(100)    | NO   | UNI |                    |                              |
| created\_at    | DATETIME        | NO   |     | CURRENT\_TIMESTAMP |                              |
| updated\_at    | DATETIME        | NO   |     | CURRENT\_TIMESTAMP | ON UPDATE CURRENT\_TIMESTAMP |

#### `repositories` 表

| 列名          | 类型              | 可否为空 | 键       | 默认值                | 额外              |
| ----------- | --------------- | ---- | ------- | ------------------ | --------------- |
| id          | BIGINT UNSIGNED | NO   | PRI     |                    | AUTO\_INCREMENT |
| analysis\_id | BIGINT UNSIGNED | YES（双向外键不能同时为非空）  | MUL(FK) |                    |                 |
| created\_at | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                 |

#### `repository_bindings` 表

| 列名          | 类型              | 可否为空 | 键       | 默认值                | 额外              |
| ----------- | --------------- | ---- | ------- | ------------------ | --------------- |
| id          | BIGINT UNSIGNED | NO   | PRI     |                    | AUTO\_INCREMENT |
| repo\_id | BIGINT UNSIGNED | NO  | MUL(FK) |                    |
| user\_id    | BIGINT UNSIGNED | NO  | MUL(FK) |                    |
| created\_at | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                 |

#### `repository_analyses` 表

| 列名             | 类型              | 可否为空 | 键       | 默认值                | 额外              |
| -------------- | --------------- | ---- | ------- | ------------------ | --------------- |
| id             | BIGINT UNSIGNED | NO   | PRI     |                    | AUTO\_INCREMENT |
| repo\_id       | BIGINT UNSIGNED | NO   | MUL(FK) |                    |                 |
| status       | ENUM('pending','completed','failed')           | NO   |         | pending            |                              |
| analysis\_json | JSON            | YES   |         |                    |                 |
| created\_at    | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                 |

#### `repository_metrics` 表

| 列名             | 类型              | 可否为空 | 键       | 默认值 | 额外              |
| -------------- | --------------- | ---- | ------- | --- | --------------- |
| id             | BIGINT UNSIGNED | NO   | PRI     |     | AUTO\_INCREMENT |
| repo\_id       | BIGINT UNSIGNED | NO   | MUL(FK) |     |                 |
| metric\_date   | DATE            | NO   | UNI(复合) |     |                 |
| quality\_score | DECIMAL(5,2)    | YES  |         |     |                 |


#### `commit_reviews` 表

| 列名           | 类型                                    | 可否为空 | 键       | 默认值                | 额外                           |
| ------------ | ------------------------------------- | ---- | ------- | ------------------ | ---------------------------- |
| id           | BIGINT UNSIGNED                       | NO   | PRI     |                    | AUTO\_INCREMENT              |
| commit\_id   | BIGINT UNSIGNED                       | NO   | UNI(FK) |                    |                              |
| review\_json | JSON                                  | NO   |         |                    |                              |
| status       | ENUM('pending','completed','failed')           | NO   |         | pending            |                              |
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

## 前端

- 技术栈: React + Next.js

### 安装

```shell
sudo apt install -y nodejs npm
```

```shell
npm install
```
