include repomapper.jac;
include codeanalyzer.jac;
include docgenie.jac;
include supervisor.jac;  # Placeholder

walker gen_docs {
    param url: str;

    can run(url: str) -> str {
        try {
            repo_path, repo_name = py_call("utils.clone_repo", [url]);
            tree_str = spawn RepoMapper -> build_tree(repo_path);
            summary = spawn RepoMapper -> summarize_readme(repo_path);
            ccg_str = spawn CodeAnalyzer -> analyze(repo_path, tree_str);
            output_path = spawn DocGenie -> generate(repo_name, summary, tree_str, ccg_str);
            # Cleanup temp (optional)
            py_call("shutil.rmtree", [repo_path]);
            report f'{{"success": true, "output_path": "{output_path}"}}';
        } except e {
            report f'{{"error": "Failed: {str(e)}"}}';
        }
    }
}

with entry init {
    report "Codebase Genius server ready.";
}