# 前端代码结构说明

## 重构后的代码架构

### 目录结构
```
front/app/
├── components/          # React 组件
│   ├── ui/             # 通用UI组件
│   │   └── Skeleton.js # 骨架屏组件
│   ├── LoginOverlay.js # 登录界面
│   ├── Sidebar.js      # 侧边栏
│   ├── UserProfile.js  # 用户资料
│   ├── ProjectList.js  # 项目列表
│   ├── ProjectDetails.js # 项目详情
│   └── SettingsModal.js # 设置模态框
├── hooks/              # 自定义Hooks
│   ├── useAuth.js      # 认证相关Hook
│   ├── useProjects.js  # 项目相关Hook
│   └── useUI.js        # UI相关Hook
├── lib/                # 工具库
│   └── api.js          # API服务封装
└── page.js             # 主页面组件
```

### API服务层 (`lib/api.js`)

#### GitLab API服务 (`gitlabService`)
- **用途**: 调用GitLab官方API
- **基础URL**: `process.env.NEXT_PUBLIC_GITLAB_BASE_URL`
- **路径**: `/api/v4/*`
- **认证**: Bearer Token (从cookie获取)

```javascript
gitlabService.getUser()                    // 获取用户信息
gitlabService.getProjects()               // 获取项目列表
gitlabService.getProject(projectId)       // 获取项目详情
gitlabService.getProjectCommits(projectId) // 获取提交记录
gitlabService.getProjectBranches(projectId) // 获取分支信息
gitlabService.getMergeRequests(projectId)  // 获取合并请求
```

#### 后端API服务 (`backendService`)
- **用途**: 调用自己的后端API
- **路径**: 
  - `/_/*` (认证相关)
  - `/api/*` (业务API)

```javascript
backendService.auth.login()               // 登录
backendService.auth.logout()              // 登出
backendService.auth.getProfile()          // 获取用户信息
backendService.analysis.getProjectAnalysis(projectId) // 获取项目分析
```

### 自定义Hooks

#### `useAuth` - 认证管理
- 管理用户登录状态
- 提供登录/登出功能
- 自动获取用户信息

#### `useProjects` - 项目管理
- 获取项目列表
- 管理项目加载状态

#### `useProjectDetails` - 项目详情管理
- 获取项目详细信息
- 管理提交记录、分支、合并请求等数据

#### `useUI` - UI交互
- `useTypewriter`: 打字机效果
- `useModal`: 模态框状态管理

### 组件设计

#### 组件职责分离
- **LoginOverlay**: 登录界面，包含打字机效果
- **Sidebar**: 侧边栏，包含用户信息和项目列表
- **UserProfile**: 用户资料显示
- **ProjectDetails**: 项目详细信息展示
- **SettingsModal**: 设置弹窗
- **Skeleton**: 骨架屏加载效果

#### 数据流
```
page.js (主组件)
├── useAuth() → user, login, logout
├── useProjects(user) → projects
├── useProjectDetails() → project details
└── 将数据传递给子组件
```

### API路径规范

#### GitLab API调用
- 所有GitLab API调用通过 `gitlabService`
- 路径: `${GITLAB_BASE_URL}/api/v4/*`
- 认证: Bearer Token

#### 后端API调用
- 认证相关: `/_/auth/*`
- 业务API: `/api/*`
- 通过Next.js的API路由转发到后端服务

### 环境变量
```bash
NEXT_PUBLIC_API_BASE_URL=http://gr.bail.asia/
NEXT_PUBLIC_GITLAB_BASE_URL=https://gitlab.bail.asia
```

### 重构优势

1. **代码分离**: 逻辑、UI、API调用完全分离
2. **可维护性**: 每个组件职责单一，易于维护
3. **可复用性**: Hook和组件可以在其他地方复用
4. **类型安全**: API调用统一封装，便于添加类型检查
5. **错误处理**: 统一的错误处理机制
6. **性能优化**: 使用并行请求提升加载速度
