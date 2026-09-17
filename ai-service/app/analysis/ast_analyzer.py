"""Deterministic Python AST Code Analyzer for Django API Extraction.

This module inspects Python source code using Python's standard `ast` module.
It extracts:
- Imports (Import and ImportFrom)
- Function and class calls (ast.Call)
- Attribute accesses (ast.Attribute)
While preserving exact line numbers and resolving symbols to their fully qualified modules.
"""

import ast
from typing import List, Dict, Any, Optional


class DetectedSymbol:
    def __init__(
        self,
        line: int,
        symbol_type: str,
        name: str,
        module: Optional[str] = None,
        full_symbol: Optional[str] = None,
        code_context: str = ""
    ):
        self.line = line
        self.symbol_type = symbol_type  # 'import', 'function_call', 'attribute_access'
        self.name = name
        self.module = module
        self.full_symbol = full_symbol or (f"{module}.{name}" if module else name)
        self.code_context = code_context

    def to_dict(self) -> Dict[str, Any]:
        return {
            "line": self.line,
            "type": self.symbol_type,
            "name": self.name,
            "module": self.module,
            "full_symbol": self.full_symbol,
            "code_context": self.code_context
        }

    def __repr__(self) -> str:
        return f"<DetectedSymbol line={self.line} type={self.symbol_type} symbol={self.full_symbol}>"


class ASTAnalyzer(ast.NodeVisitor):
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.lines = source_code.splitlines()
        self.detected_symbols: List[DetectedSymbol] = []
        # Map local names to their imported module (e.g. 'url' -> 'django.conf.urls')
        self.import_map: Dict[str, str] = {}

    def _get_context(self, lineno: int) -> str:
        if 1 <= lineno <= len(self.lines):
            return self.lines[lineno - 1].strip()
        return ""

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            local_name = alias.asname or alias.name
            self.import_map[local_name] = alias.name
            if "django" in alias.name:
                self.detected_symbols.append(
                    DetectedSymbol(
                        line=node.lineno,
                        symbol_type="import",
                        name=alias.name,
                        module=None,
                        full_symbol=alias.name,
                        code_context=self._get_context(node.lineno)
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            local_name = alias.asname or alias.name
            full_name = f"{module}.{alias.name}" if module else alias.name
            self.import_map[local_name] = full_name
            
            # Detect any import from django
            if "django" in module or module.startswith("django"):
                self.detected_symbols.append(
                    DetectedSymbol(
                        line=node.lineno,
                        symbol_type="import",
                        name=alias.name,
                        module=module,
                        full_symbol=full_name,
                        code_context=self._get_context(node.lineno)
                    )
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name, full_symbol, module = self._resolve_node_name(node.func)
        if call_name:
            self.detected_symbols.append(
                DetectedSymbol(
                    line=node.lineno,
                    symbol_type="function_call",
                    name=call_name,
                    module=module,
                    full_symbol=full_symbol,
                    code_context=self._get_context(node.lineno)
                )
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        attr_name, full_symbol, module = self._resolve_node_name(node)
        if attr_name and (full_symbol and ("django" in full_symbol or full_symbol in self.import_map.values())):
            self.detected_symbols.append(
                DetectedSymbol(
                    line=node.lineno,
                    symbol_type="attribute_access",
                    name=attr_name,
                    module=module,
                    full_symbol=full_symbol,
                    code_context=self._get_context(node.lineno)
                )
            )
        self.generic_visit(node)

    def _resolve_node_name(self, node: ast.AST) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Resolves an AST node (Name, Attribute) to (name, full_symbol, module)."""
        if isinstance(node, ast.Name):
            name = node.id
            if name in self.import_map:
                full = self.import_map[name]
                parts = full.rsplit(".", 1)
                module = parts[0] if len(parts) > 1 else None
                return name, full, module
            return name, name, None

        elif isinstance(node, ast.Attribute):
            base_name, base_full, _ = self._resolve_node_name(node.value)
            attr_name = node.attr
            if base_full:
                full = f"{base_full}.{attr_name}"
                parts = full.rsplit(".", 1)
                module = parts[0] if len(parts) > 1 else None
                return attr_name, full, module
            return attr_name, attr_name, None

        return None, None, None


def analyze_code_ast(source_code: str) -> List[DetectedSymbol]:
    """Parse python source code and return detected Django symbols with line numbers."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        # Gracefully handle code fragments
        return []

    analyzer = ASTAnalyzer(source_code)
    analyzer.visit(tree)
    
    # Filter to unique relevant entries prioritized by full_symbol and line
    return analyzer.detected_symbols
