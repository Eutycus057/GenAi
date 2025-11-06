walker DocGenie {
    can generate(repo_name: str, summary: str, file_tree_str: str, ccg_str: str) -> str {
        file_tree = eval(file_tree_str);
        ccg = eval(ccg_str);
        md = f"""# Codebase Genius: {repo_name}

## Overview
{summary}

## File Tree
""";
        for item in file_tree:
            md += f"### {item['dir'] or 'Root'}\n";
            for f in item['files']:
                md += f"- {f}\n";
            md += "\n";

        md += "## Code Analysis\n";
        for file, info in ccg.items():
            md += f"### {file}\n";
            if info['type'] == 'python':
                if info.get('funcs'):
                    md += f"**Functions:** {', '.join(info['funcs'])}\n";
                if info.get('classes'):
                    md += f"**Classes:** {', '.join(info['classes'])}\n";
            elif info['type'] == 'jac':
                if info.get('walkers'):
                    md += f"**Walkers:** {', '.join(info['walkers'])}\n";
                if info.get('nodes'):
                    md += f"**Nodes:** {', '.join(info['nodes'])}\n";
            md += "\n";

        md += """## Simple CCG Diagram (File Relationships)
```mermaid
graph TD
    A[Entry Point Files] --> B[Utility Modules]
    style A fill:#f9f
(This is a placeholder; extend with real edges from CCG.)
""";
output_path = f"outputs/{repo_name}-docs.md";
py_call("utils.write_md", [output_path, md]);
report output_path;
}
}