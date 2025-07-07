import gitlab
from ..core.config import settings

def get_repo_branches(oauth_token, project_id):
    """
    Get the branches of a GitLab repository by project ID.
    """
    gl = gitlab.Gitlab(url=settings.gitlab_url, oauth_token=oauth_token)
    gl.auth()
    project = gl.projects.get(project_id)
    return [branch.name for branch in project.branches.list(get_all=True)]

def get_repo_tree(oauth_token, project_id, ref=None):
    """
    Get the GitLab repository info by project ID.
    """
    gl = gitlab.Gitlab(url = settings.gitlab_url, oauth_token = oauth_token)
    gl.auth()
    project = gl.projects.get(project_id)
    return project.repository_tree(ref=ref, recursive=True, get_all=True)

def get_file_content(oauth_token, project_id, ref, file_path):
    """
    Get the content of a file in the GitLab repository.
    """
    gl = gitlab.Gitlab(url = settings.gitlab_url, oauth_token = oauth_token)
    gl.auth()
    project = gl.projects.get(project_id)
    file = project.files.get(file_path = file_path, ref = ref)
    content_bytes = file.decode()
    return content_bytes.decode('utf-8') if isinstance(content_bytes, bytes) else content_bytes

def get_project_commits(oauth_token, project_id, ref_name=None, per_page=20):
    """
    获取 GitLab 项目的提交列表。
    """
    gl = gitlab.Gitlab(url=settings.gitlab_url, oauth_token=oauth_token)
    gl.auth()
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

def get_commit_details(oauth_token, project_id, commit_sha):
    """
    Get the details of a specific commit in the GitLab repository.
    """
    gl = gitlab.Gitlab(url = settings.gitlab_url, oauth_token = oauth_token)
    gl.auth()
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

def get_branch(oauth_token, project_id, branch_name):
    """
    Get the details of a specific branch in the GitLab repository.
    """
    gl = gitlab.Gitlab(url = settings.gitlab_url, oauth_token = oauth_token)
    gl.auth()
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
    "get_repo_branches": get_repo_branches,
    "get_repo_tree": get_repo_tree,
    "get_file_content": get_file_content,
    "get_project_commits": get_project_commits,
    "get_commit_details": get_commit_details,
    "get_branch": get_branch,
}

tools = [
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


if __name__ == "__main__":
    result = get_repo_branches("5c8c09c3ef93e4d7162c944be254a0ebcae6e475b749e3efbccf3a720012b944", 1)
    print(f"Branches: {result}")