# Gitlab-Reviewer

深圳共进电子出题：基于 AI 的 GitLab 自动代码评审系统


## 项目介绍
Gitlab-Reviewer 是一个基于人工智能的 GitLab 代码自动评审系统。该系统能够自动分析 GitLab 项目中的代码变更，提供智能化的代码评审建议，帮助开发团队提高代码质量和评审效率。

Gitlab-Reviewer 的主要功能是：

1. 绑定 Gitlab 仓库并进行综合评析。
2. 接收所绑定仓库的 push （代码推送）事件，并对一次 push 中的代码变动进行评审。
3. 接收所绑定仓库的 Merge Request 事件，自动启动流水线进行动态分析测试，然后交给 AI 模型进行评判，帮助评审员高效评审代码。
4. 将评审结果通过邮件或 webhook 进行推送


## 快速开始
### 准备
你需要：
- 一个私有化部署的 GitLab 服务
- 一个待部署的服务器，要求能与 GitLab 服务器进行双向通信
- （可选）邮箱 smtp 账号密码

### 下载和安装

1. 安装 `uv` 和 `node.js` 运行环境
2. 将 `back/.env.example` 复制为 `.env` ，并填写相关字段（详见下文）
3. 在 `back` 目录下执行 `uv run run.py` 即可启动后端服务。
4. 在 `front` 目录下创建 `.env.local` 文件，并填写相关字段（详见下文）
5. 在 `front` 目录下执行 `npm install` 和 `npm run dev` 启动前端服务。

### 容器化

???

### 配置说明

#### 后端配置说明
配置文件：`back/.env`
```bash
# Gitlab Reviewer部署URL
self_url="https://gr.example.com/"

# 数据库相关配置
# 数据库URL，可换用其他数据库，但要先安装响应的库
DATABASE_URL="mysql+pymysql://gitlab_reviewer:password@mysql.server:3306/gitlab_reviewer"

# Gitlab相关配置
# Gitlab URL
gitlab_url="https://gitlab.example.com/"
# 请以管理员身份登录gitlab后，在`管理面板`-`应用`中新增一个应用,
# `scope`勾选`api`即可，`Redirect URI`填写`{self_url}/_/auth/callback`
# 并获取client_id和client_secret，填写以下2个字段
gitlab_client_id="xxxxxxxxxxxxx"
gitlab_client_secret="gloas-xxxxxxxxxxxxxx"
# 管理员访问令牌，用于在用户未登录的情况下，收到评审webhook时，获取任意项目的信息
# 请以管理员身份登录gitlab后，在`个人设置`-`访问令牌`中新增一个令牌，
# `选择范围`勾选`api`即可，并获取令牌，填写以下字段（注意过期时间，及时更换）
gitlab_root_private_token="glpat-xxxxxxxxxxxx"
# gitlab防伪token，用于验证webhook请求，自己拟定。
# 会在绑定仓库时自动向仓库添加webhook并配置该token
gitlab_webhook_token='xxxxxxxxxxxx'

# 大模型相关配置。不必是ChaptGPT，只要是支持ChatCompletion接口的模型即可
openai_base_url="https://api.openai.com/v1"
openai_api_key='sk-xxxxxxxxxxxxx'
openai_model='gpt-3.5-turbo'

# 邮件配置
# 是否启用邮件通知。如果填`false`，则下面的其他字段都可以不填
enable_email="true"
smtp_host="smtp.example.com"
smtp_port="465"
smtp_username="user@example.com"
smtp_password="smtp_password"
# smtp加密方式，可选值：`none`,`ssl`,`starttls`
smtp_encryption="ssl"
# 发件人昵称
email_from="Sender Nickname"
```

其中，

- 获取`client_id`和`client_secret`的步骤为：
  <img width="2505" height="1423" alt="image" src="https://github.com/user-attachments/assets/96879786-49e6-4a71-a048-bd174b2227f4" />
  <img width="2505" height="1428" alt="image" src="https://github.com/user-attachments/assets/bbb80e8f-c308-40e7-89aa-bbe925489ba1" />

- 获取管理员令牌的步骤为：
  <img width="2505" height="1423" alt="image" src="https://github.com/user-attachments/assets/763606ed-1d22-4832-b4c7-5f1c6fc26534" />
  <img width="2505" height="1422" alt="image" src="https://github.com/user-attachments/assets/db173579-a3c7-46dc-90c3-a92828551f1a" />

另外，监听 ip 和端口默认为 `[::]:8000` ，可在 `back/run.py` 中修改

#### 前端配置说明
配置文件：`front/.env.local`
```bash
# 后端URL
NEXT_PUBLIC_API_BASE_URL=http://back.gr.example.com/
# Gitlab URL
NEXT_PUBLIC_GITLAB_BASE_URL=https://gitlab.example.com/
```

### 使用方法

1. 按照上述说明，部署本服务
2. 使用 Gitlab 账号进行 OAuth 登录
3. 绑定 Gitlab 仓库，会自动开始分析整个仓库，并创建 webhook 以监听事件
4. 可以在设置中配置个人的通知方式
5. 当绑定的仓库有推送或创建 MR 时，会自动触发分析并生成报告

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进本项目。

### 开发流程

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 GPLv3 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

项目链接: [https://your-gitlab-url/gitlab-reviewer](https://your-gitlab-url/gitlab-reviewer)

## 致谢

- [GitLab API](https://docs.gitlab.com/ee/api/)
- [OpenAI](https://openai.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
