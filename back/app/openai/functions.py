import gitlab
from ..core.config import settings

def get_repo_tree(oauth_token, project_id, ref=None):
    """
    Get the GitLab repository info by project ID.
    """
    gl = gitlab.Gitlab(url = settings.gitlab_url, oauth_token = oauth_token)
    gl.auth()
    project = gl.projects.get(project_id)
    return project.repository_tree(ref=ref, recursive=True)

def get_file_content(oauth_token, project_id, ref, file_path):
    """
    Get the content of a file in the GitLab repository.
    """
    gl = gitlab.Gitlab(url = settings.gitlab_url, oauth_token = oauth_token)
    gl.auth()
    project = gl.projects.get(project_id)
    file = project.files.get(file_path = file_path, ref = ref)
    return file.decode().strip()


function_map = {
    "get_repo_tree": get_repo_tree,
    "get_file_content": get_file_content,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_repo_tree",
            "description": "通过项目ID获取GitLab仓库的文件树结构。",
            "parameters": {
                "type": "object",
                "properties": {
                    "oauth_token": {
                        "type": "string",
                        "description": "用于认证GitLab API的OAuth令牌。",
                    },
                    "project_id": {
                        "type": "integer",
                        "description": "GitLab项目的ID。",
                    },
                    "ref": {
                        "type": "string",
                        "description": "分支、标签或提交的名称，用于指定仓库的版本。默认为默认分支。",
                    },
                },
                "required": ["oauth_token", "project_id"],
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
                    "oauth_token": {
                        "type": "string",
                        "description": "用于认证GitLab API的OAuth令牌。",
                    },
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
                "required": ["oauth_token", "project_id", "ref", "file_path"],
            },
        },
    },
]


if __name__ == "__main__":
    result = get_file_content("4005b71d135981d2a5926cc3a4e1a32a0d47a44d5f8213f3db2c3dad011d3972", 1, "main", "README.md")
    print(f"File content: {result}")