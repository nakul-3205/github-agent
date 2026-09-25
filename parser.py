import ast
import os

def parse_file(filepath):
    with open(filepath, "r") as f:
        source = f.read()

    source_lines = source.splitlines()
    tree = ast.parse(source)
    chunks = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    chunks.append(make_chunk(child, source_lines, filepath, class_name))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not isinstance(getattr(node, "parent_class", None), ast.ClassDef):
                pass

    top_level_functions = [
        n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    for node in top_level_functions:
        chunks.append(make_chunk(node, source_lines, filepath, class_name=None))

    return chunks


def make_chunk(node, source_lines, filepath, class_name):
    start = node.lineno
    end = node.end_lineno
    code_text = "\n".join(source_lines[start - 1:end])

    return {
        "file": filepath,
        "class": class_name,
        "function": node.name,
        "start_line": start,
        "end_line": end,
        "code": code_text,
    }


# if __name__ == "__main__":
#     result = parse_file("sample.py")
#     for chunk in result:
#         label = f"{chunk['class']}.{chunk['function']}" if chunk['class'] else chunk['function']
#         print(f"--- {label} (lines {chunk['start_line']}-{chunk['end_line']}) ---")
#         print(chunk['code'])
#         print()


if __name__ == "__main__":
    result = parse_file("sample.py")
    for chunk in result:
        label = f"{chunk['class']}.{chunk['function']}" if chunk['class'] else chunk['function']
        print(f"--- {label} (lines {chunk['start_line']}-{chunk['end_line']}) ---")

        
def parse_repo(folder_path):
    all_chunks = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    chunks = parse_file(filepath)
                    all_chunks.extend(chunks)
                except SyntaxError:
                    print(f"Skipping {filepath} (syntax error)")

    return all_chunks