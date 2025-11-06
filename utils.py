import os
import subprocess
import tempfile
import shutil
import ast
from pathlib import Path
from openai import OpenAI

def get_api_key():
    return os.getenv('OPENAI_API_KEY')

def clone_repo(url):
    """Clone a GitHub repo to a temporary folder."""
    if not url.endswith('.git'):
        url += '.git'
    temp_dir = tempfile.mkdtemp(prefix='repo_')
    try:
        subprocess.run(['git', 'clone', url, temp_dir], check=True, capture_output=True)
        repo_name = Path(url).name.replace('.git', '')
        return temp_dir, repo_name
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to clone repo: {e}")

def load_gitignore(repo_path):
    """Load ignore patterns from .gitignore in the repo root."""
    gitignore_path = os.path.join(repo_path, ".gitignore")
    ignore_patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.append(line)
    return ignore_patterns

def is_ignored(file_path, ignore_patterns, repo_path):
    """Check if a file path matches any pattern in .gitignore."""
    rel_path = os.path.relpath(file_path, repo_path)
    for pattern in ignore_patterns:
        if Path(rel_path).match(pattern):
            return True
    return False

def build_file_tree(repo_path):
    """Build a structured representation of source files in a repo."""
    result = []
    ignore_dirs = ['.git', 'node_modules', '__pycache__', 'venv', '.venv']
    ignore_patterns = load_gitignore(repo_path)

    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not is_ignored(os.path.join(root, d), ignore_patterns, repo_path)]
        rel_root = os.path.relpath(root, repo_path)
        # Include only source files and skip ignored files
        src_files = [
            f for f in files
            if f.endswith(('.py', '.jac')) and not is_ignored(os.path.join(root, f), ignore_patterns, repo_path)
        ]
        if src_files:  # Only include dirs with source files
            result.append({'dir': rel_root if rel_root != '.' else '', 'files': src_files})

    return result

def read_readme(repo_path):
    """Read README file from repo if present."""
    candidates = ['README.md', 'readme.md', 'README.txt']
    for c in candidates:
        f = os.path.join(repo_path, c)
        if os.path.isfile(f):
            with open(f, 'r', encoding='utf-8') as file:
                return file.read()
    return 'No README found.'

def summarize_readme(readme):
    """Summarize README content using OpenAI API."""
    api_key = get_api_key()
    if not api_key:
        return 'Summary unavailable: Set OPENAI_API_KEY.'
    client = OpenAI(api_key=api_key)
    prompt = f"Summarize this README into a concise 3-5 sentence overview:\n\n{readme[:2000]}"  # Truncate for token limit
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def parse_source_file(file_path):
    """Extract functions, classes, and walkers/nodes from Python and Jac files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if file_path.endswith('.py'):
        try:
            tree = ast.parse(content)
            funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            return {'type': 'python', 'funcs': list(set(funcs)), 'classes': list(set(classes))}
        except SyntaxError:
            return {'type': 'python', 'error': 'Parse error', 'funcs': [], 'classes': []}
    elif file_path.endswith('.jac'):
        import re
        walkers = re.findall(r'walker\s+(\w+)', content)
        nodes = re.findall(r'node\s+(\w+)', content)
        return {'type': 'jac', 'walkers': list(set(walkers)), 'nodes': list(set(nodes))}
    return {'type': 'unknown', 'content': content[:500]}

def write_md(output_path, md_content):
    """Write markdown content to a file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
