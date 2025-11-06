walker RepoMapper {
    can build_tree(repo_url: str) -> str {
        # Clone the repo using utils.py
        repo_info = py_call("utils.clone_repo", [repo_url]);
        repo_path = repo_info[0];   # temp folder path
        repo_name = repo_info[1];

        # Build file tree
        tree = py_call("utils.build_file_tree", [repo_path]);
        report str(tree);  # Serialize as str for Jac (or JSON)
    }

    can summarize_readme(repo_url: str) -> str {
        repo_info = py_call("utils.clone_repo", [repo_url]);
        repo_path = repo_info[0];

        readme = py_call("utils.read_readme", [repo_path]);
        summary = py_call("utils.summarize_readme", [readme]);
        report summary;
    }
}
