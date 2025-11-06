walker CodeAnalyzer {
    can analyze(repo_path: str, file_tree_str: str) -> str {
        # Deserialize tree (simple eval for sample; use JSON in prod)
        file_tree = eval(file_tree_str);
        ccg = {};
        for item in file_tree:
            for f in item['files']:
                full_path = os.path.join(repo_path, item['dir'], f) if item['dir'] else os.path.join(repo_path, f);
                analysis = py_call("utils.parse_source_file", [full_path]);
                ccg[f] = analysis;
        report str(ccg);
    }
}