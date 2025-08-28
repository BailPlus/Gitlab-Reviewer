# Gitlab-Reviewer

深圳共进电子出题：基于 AI 的 GitLab 自动代码评审系统

## 项目摘要

### 设计思路

- 借鉴 codex 和 deepwiki
- 可以绑定仓库，绑定之后可以由 AI 对项目进行在整体分析
- 对每次 git 推送进行评估，给出修改建议，可以一键发起 PR

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
  Cookie: token=...
  ```
  ```http
  Set-Cookie: token=; expires=Thu, 01 Jan 1970 00:00:00 GMT
  Location: /login

  ```
  
  - 获取用户信息
  ```http
  GET /_/auth/profile
  Cookie: token=...
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
  Cookie: token=...
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
  Cookie: token=...
  
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
  - 解绑仓库
  ```http
  DELETE /api/repositories/{repo_id}
  Cookie: token=...
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
  Cookie: token=...

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
  Cookie: token=...
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
  Cookie: token=...
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
  - GitLab Webhook 接收端点
  ```http
  POST /api/webhooks/gitlab
  X-Gitlab-Token: ...

  {
    "object_kind": "push",
    "event_name": "push",
    "before": "95790bf891e76fee5e1747ab589903a6a1f80f22",
    "after": "da1560886d4f094c3e6c9ef40349f7d38b5d27d7",
    "ref": "refs/heads/master",
    "ref_protected": true,
    "checkout_sha": "da1560886d4f094c3e6c9ef40349f7d38b5d27d7",
    "message": "Hello World",
    "user_id": 4,
    "user_name": "John Smith",
    "user_email": "john@example.com",
    "user_avatar": "https://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=8://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=80",
    "project_id": 15,
    "project": {
      "id": 15,
      "name": "gitlab",
      "description": "",
      "web_url": "http://test.example.com/gitlab/gitlab",
      "avatar_url": "https://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=8://s.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?s=80",
      "git_ssh_url": "git@test.example.com:gitlab/gitlab.git",
      "git_http_url": "http://test.example.com/gitlab/gitlab.git",
      "namespace": "gitlab",
      "visibility_level": 0,
      "path_with_namespace": "gitlab/gitlab",
      "default_branch": "master"
    },
    "commits": [
      {
        "id": "c5feabde2d8cd023215af4d2ceeb7a64839fc428",
        "message": "Add simple search to projects in public area\n\ncommit message body",
        "title": "Add simple search to projects in public area",
        "timestamp": "2013-05-13T18:18:08+00:00",
        "url": "https://test.example.com/gitlab/gitlab/-/commit/c5feabde2d8cd023215af4d2ceeb7a64839fc428",
        "author": {
          "name": "Test User",
          "email": "test@example.com"
        }
      }
    ],
    "total_commits_count": 1,
    "push_options": {
      "ci": {
        "skip": true
      }
    }
  }
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {}
  }
  ```
  - 获取提交的 AI 评审结果
  ```http
  GET /api/commits/{commit_id}/review 
  Cookie: token=...
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {
      "review": "AI 评审结果",
      "created_at": 17xxxxxxxx
    }
  }
  ```
  - 一键应用修改建议
  ```http
  POST /api/commits/{commit_id}/apply-suggestions
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {}
  }
  ```

- 通知推送相关：
  - 获取通知设置
  ```http
  GET /api/notifications/settings
  Cookie: token=...
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {
      "notify_level": 1,
      "email": {
        "enabled": true,
      },
      "webhook": {
        "enabled": true,
        "url": "https://example.com/webhook",
        "secret": "..."
      }
    }
  }
  ```
  - 配置通知设置
  ```http
  POST /api/notifications/settings
  Cookie: token=...
  
  {
    "notify_level": 1,
    "email": {
      "enabled": true,
    },
    "webhook": {
      "enabled": true,
      "url": "https://example.com/webhook",
      "secret": "..."
    }
  }
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {
      "notify_level": 1,
      "email": {
        "enabled": true,
      },
      "webhook": {
        "enabled": true,
        "url": "https://example.com/webhook",
        "secret": "..."
      }
    }
  }
  ```

  - 测试通知配置
  ```http
  POST /api/notifications/test
  Cookie: token=...
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {}
  }
  ```

- Merge Request 评审相关
  - 获取 Merge Request 评审结果
  ```http
  GET /api/merge_requests/{merge_request_id}/review
  Cookie: token=...
  ```
  ```json
  {
    "status": 0,
    "info": "ok",
    "data": {
      "review": "Merge Request 评审结果",
      "created_at": 17xxxxxxxx
    }
  }
  ```

## 后端

- 技术栈：FastAPI, SQLModel

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

| 列名           | 类型                                    | 可否为空 | 键       | 默认值               | 额外                           |
| ------------ | ------------------------------------- | ---- | ------- | ------------------ | ---------------------------- |
| id           | BIGINT UNSIGNED                       | NO   | PRI     |                    | AUTO\_INCREMENT              |
| repo\_id       | BIGINT UNSIGNED                     | NO   | MUL(FK) |                    |
| before\_commit | VARCHAR(64)                         | NO   | UNI |                    |                              |
| after\_commit  | VARCHAR(64)                         | NO   | UNI |                    |                              |
| review\_json | JSON                                  | NO   |         |                    |                              |
| status       | ENUM('pending','completed','failed')  | NO   |         | pending            |                              |
| reviewed\_at | DATETIME                              | YES  |         |                    |                              |
| updated\_at  | DATETIME                              | NO   |         | CURRENT\_TIMESTAMP | ON UPDATE CURRENT\_TIMESTAMP |

#### `commit_review_bindings` 表

| 列名          | 类型              | 可否为空 | 键       | 默认值 | 额外              |
| ------------ | --------------- | ---- | ------- | --- | --------------- |
| id           | BIGINT UNSIGNED | NO   | PRI     |                    | AUTO\_INCREMENT |
| commit\_id     | VARCHAR(64) | NO   | UNI      |                    |
| review\_id    | BIGINT UNSIGNED | NO   | MUL(FK) |                    |
| created\_at  | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                 |

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

| 列名            | 类型              | 可否为空 | 键       | 默认值                | 额外                           |
| ---------------- | --------------- | ---- | ------- | ------------------ | ---------------------------- |
| id               | BIGINT UNSIGNED | NO   | PRI     |                    | AUTO\_INCREMENT              |
| user\_id         | BIGINT UNSIGNED | NO   | UNI(FK) |                    |                              |
| notify\_level    | INTEGER ∈ [0,3] | NO   |         | 0                  |                              |
| email\_enabled   | TINYINT(1)      | NO   |         | 0                  |                              |
| webhook\_enabled | TINYINT(1)      | NO   |         | 0                  |                              |
| webhook\_url     | VARCHAR(100)    | YES  |         | NULL               |                              |
| webhook\_secret  | VARCHAR(100)    | YES  |         | NULL               |                              |
| created\_at      | DATETIME        | NO   |         | CURRENT\_TIMESTAMP |                              |
| updated\_at      | DATETIME        | NO   |         | CURRENT\_TIMESTAMP | ON UPDATE CURRENT\_TIMESTAMP |

#### `mr_reviews` 表

| 列名           | 类型                                    | 可否为空 | 键       | 默认值               | 额外                           |
| ------------ | ------------------------------------- | ---- | ------- | ------------------ | ---------------------------- |
| id           | BIGINT UNSIGNED                       | NO   | PRI     |                    | AUTO\_INCREMENT              |
| repo\_id       | BIGINT UNSIGNED                     | NO   | MUL(FK) |                    |
| mr\_iid        | BIGINT UNSIGNED                     | NO   |         |                    |         
| review\_json | JSON                                  | NO   |         |                    |                              |
| status       | ENUM('pending','completed','failed')  | NO   |         | pending            |                              |
| created\_at  | DATETIME                              | NO   |         |                    |                              |
| updated\_at  | DATETIME                              | NO   |         | CURRENT\_TIMESTAMP | ON UPDATE CURRENT\_TIMESTAMP |


#### `webhook_logs` 表

| 列名          | 类型              | 可否为空 | 键       | 默认值 | 额外              |
| ------------ | --------------- | ---- | ------- | --- | --------------- |
| id           | BIGINT UNSIGNED | NO   | PRI     |     | AUTO\_INCREMENT |
| data         | TEXT            | NO   |         |     |                 |
| created\_at  | DATETIME        | NO   |         |     |                 |

## 前端

- 技术栈: React + Next.js

### 安装

```shell
sudo apt install -y nodejs npm
```

```shell
npm install
```
