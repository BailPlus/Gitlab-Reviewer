import gitlab

def get_repo_info(gl: gitlab.Gitlab, project_id):
    """
    根据项目 ID 获取 GitLab 仓库的基本信息。
    """
    project = gl.projects.get(project_id)
    return project.attributes

def get_repo_branches(gl: gitlab.Gitlab, project_id):
    """
    根据项目 ID 获取 GitLab 仓库的分支列表。
    """
    project = gl.projects.get(project_id)
    return [branch.name for branch in project.branches.list(get_all=True)]

def get_repo_tree(gl: gitlab.Gitlab, project_id, ref=None):
    """
    根据项目 ID 获取 GitLab 仓库的文件树结构。
    可通过 ref 指定分支、标签或提交（默认为仓库默认分支）。
    """
    project = gl.projects.get(project_id)
    return project.repository_tree(ref=ref, recursive=True, get_all=True) # type: ignore

def get_file_content(gl: gitlab.Gitlab, project_id, ref, file_path):
    """
    获取 GitLab 仓库中指定文件的内容。
    参数:
      - project_id: 项目 ID
      - ref: 文件所在的分支、标签或提交 SHA
      - file_path: 仓库中文件的完整路径
    返回 UTF-8 解码后的文件内容字符串。
    """
    project = gl.projects.get(project_id)
    file = project.files.get(file_path = file_path, ref = ref)
    content_bytes = file.decode()
    return content_bytes.decode('utf-8') if isinstance(content_bytes, bytes) else content_bytes

def get_project_commits(gl: gitlab.Gitlab, project_id, ref_name=None, per_page=20):
    """
    获取 GitLab 项目的提交列表。
    参数:
      - project_id: 项目 ID
      - ref_name: 可为分支名、标签名或 commit SHA（可选）
      - per_page: 每页返回的提交数量（默认 20）
    返回提交的摘要信息列表。
    """
    project = gl.projects.get(project_id)
    # 'ref_name' 可以是分支名、标签名或 commit SHA
    # 使用 per_page 限制返回的提交数量，例如最近的 20 个
    commits = project.commits.list(ref_name=ref_name, per_page=per_page, get_all=False)
    return [
        {
            "id": c.id,
            "short_id": c.short_id,
            "title": c.title,
            "message": c.message,
            "author_name": c.author_name,
            "created_at": c.created_at,
        }
        for c in commits
    ]

def get_commit_details(gl: gitlab.Gitlab, project_id, commit_sha):
    """
    获取指定提交的详细信息。
    参数:
      - project_id: 项目 ID
      - commit_sha: 提交的 SHA 值
    返回包含提交详细信息的字典。
    """
    project = gl.projects.get(project_id)
    commit = project.commits.get(commit_sha)
    return {
        "id": commit.id,
        "message": commit.message,
        "author_name": commit.author_name,
        "author_email": commit.author_email,
        "created_at": commit.created_at,
        "stats": commit.stats
    }

def get_commit_compare(gl: gitlab.Gitlab, project_id, before_sha, after_sha):
    """
    获取指定提交的差异信息。
    参数:
      - project_id: 项目 ID
      - before_sha: 提交的 SHA 值
      - after_sha: 提交的 SHA 值
    """
    project = gl.projects.get(project_id)
    return project.repository_compare(before_sha, after_sha)

def get_branch(gl: gitlab.Gitlab, project_id, branch_name):
    """
    获取指定分支的详细信息，包括最新提交信息。
    参数:
      - project_id: 项目 ID
      - branch_name: 分支名称
    返回包含分支和最新提交信息的字典。
    """
    project = gl.projects.get(project_id)
    branch = project.branches.get(branch_name)
    return {
        "name": branch.name,
        "commit": {
            "id": branch.commit['id'],
            "message": branch.commit['message'],
            "author_name": branch.commit['author_name'],
            "author_email": branch.commit['author_email'],
            "created_at": branch.commit['created_at']
        }
    }

function_map = {
    "get_repo_info": get_repo_info,
    "get_repo_branches": get_repo_branches,
    "get_repo_tree": get_repo_tree,
    "get_file_content": get_file_content,
    "get_project_commits": get_project_commits,
    "get_commit_details": get_commit_details,
    "get_commit_compare": get_commit_compare,
    "get_branch": get_branch,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_repo_info",
            "description": "获取GitLab仓库的基本信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "GitLab项目的ID。",
                    },
                },
                "required": ["project_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_repo_branches",
            "description": "获取GitLab仓库的分支列表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "GitLab项目的ID。",
                    },
                },
                "required": ["project_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_repo_tree",
            "description": "通过项目ID获取GitLab仓库的文件树结构。",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "GitLab项目的ID。",
                    },
                    "ref": {
                        "type": "string",
                        "description": "分支、标签或提交的名称，用于指定仓库的版本。默认为默认分支。",
                    },
                },
                "required": ["project_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_content",
            "description": "获取GitLab仓库中指定文件的内容。",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "GitLab项目的ID。",
                    },
                    "ref": {
                        "type": "string",
                        "description": "文件所在的分支、标签或提交的名称。",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "仓库中文件的完整路径。",
                    },
                },
                "required": ["project_id", "ref", "file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_commits",
            "description": "获取GitLab项目的 Commit 提交列表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "GitLab项目的ID。",
                    },
                    "ref_name": {
                        "type": "string",
                        "description": "分支名、标签名或 commit SHA。",
                    },
                    "per_page": {
                        "type": "integer",
                        "default": 20,
                        "description": "每页返回的提交数量。",
                    },
                },
                "required": ["project_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_commit_details",
            "description": "获取指定提交的详细信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "GitLab项目的ID。",
                    },
                    "commit_sha": {
                        "type": "string",
                        "description": "提交的SHA值。",
                    },
                },
                "required": ["project_id", "commit_sha"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_commit_compare",
            "description": "获取两个提交之间的差异信息，你可以通过这个直接获取一次push的diff。",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "GitLab项目的ID。",
                    },
                    "before_sha": {
                        "type": "string",
                        "description": "比较的起始提交SHA值。",
                    },
                    "after_sha": {
                        "type": "string",
                        "description": "比较的结束提交SHA值。",
                    },
                },
                "required": ["project_id", "before_sha", "after_sha"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_branch",
            "description": "获取指定分支的详细信息,包括最新提交。",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "GitLab项目的ID。",
                    },
                    "branch_name": {
                        "type": "string",
                        "description": '分支名称。',
                    },
                },
                'required': ['project_id', 'branch_name'],
            }
        }
    },
]