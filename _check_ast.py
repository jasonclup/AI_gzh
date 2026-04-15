import ast
path = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\team_manager.py'
with open(path, 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(f'{"  " * (node.col_offset // 4)}def {node.name} (col={node.col_offset})')
