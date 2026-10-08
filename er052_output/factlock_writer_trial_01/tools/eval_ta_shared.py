# all6側eval_ta.pyのINSTR/SCHEMAをread-only抽出(同一rubric・同一スキーマ・同一指示で採点するため)。all6側ファイルは編集しない。
import ast
import os

_p = os.path.join(os.path.dirname(__file__), "..", "..", "all6_writer_redesign_necessity_01", "tools", "eval_ta.py")
_src = open(_p, encoding="utf-8").read()
_tree = ast.parse(_src)
_ns = {}
for node in _tree.body:
    if isinstance(node, ast.Assign) and any(getattr(t, "id", "") in ("SCHEMA", "INSTR") for t in node.targets):
        exec(compile(ast.Module([node], []), _p, "exec"), _ns)
SCHEMA, INSTR = _ns["SCHEMA"], _ns["INSTR"]
