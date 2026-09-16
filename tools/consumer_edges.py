"""Direct consumer edges only: no imports, sys.modules scans, or execution.

Conservative alias propagation intentionally visits both dual-context branches.
Dynamic imports need exact expression + context + rationale dispositions; an
engine-internal literal can never be waived by a disposition.
"""
import ast
from pathlib import Path


def package_contexts(repo, path):
    """Checkout namespace context, plus a bundled loader context when applicable.

    Namespace packages (e.g. surfaces/) count too. A root __init__.py indicates
    the second, parent-loaded context; its actual directory name is used.
    """
    path = Path(path)
    parts = path.parent.parts
    package = '.'.join(parts)
    contexts = [package]
    if (Path(repo) / '__init__.py').is_file():
        contexts.append('.'.join((Path(repo).name, *parts)))
    return contexts


def resolve(module, level, package):
    if not level:
        return module or ''
    parts = package.split('.') if package else []
    # Python: level=1 remains in the current package, not its parent.
    if level > len(parts):
        return None
    return '.'.join(parts[:len(parts) - level + 1] + ([module] if module else []))


def engine_suffix(name):
    parts = name.split('.')
    if 'dgemma' not in parts:
        return None
    return parts[parts.index('dgemma') + 1:]


def check_edges(text, exports, *, path='<fixture>', packages=('',), dispositions=()):
    """Return diagnostics. No dynamic-import disposition is implicit.

    Dispositions are dictionaries with package, expression, reason. A caller
    must provide reviewed records explicitly (the candidate gate provides none).
    """
    root = ast.parse(text, filename=path)
    errors = set()
    for package in packages:
        aliases = {}
        def report(node, message):
            errors.add(f'{path}:{node.lineno} [{package or "top-level"}]: {message}')
        def edge(node, name, importing=False):
            suffix = engine_suffix(name)
            if suffix is not None and suffix:
                # Importing a module below root is never a root-symbol import.
                if importing or suffix[0] not in exports or any(p.startswith('_') for p in suffix):
                    report(node, f'private engine edge {name}')
        def dotted(node):
            if isinstance(node, ast.Name):
                return aliases.get(node.id, node.id)
            if isinstance(node, ast.Attribute):
                base = dotted(node.value)
                return f'{base}.{node.attr}' if base else None
            return None
        for node in ast.walk(root):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    edge(node, alias.name, importing=True)
                    aliases[alias.asname or alias.name.split('.')[0]] = alias.name if alias.asname else alias.name.split('.')[0]
            elif isinstance(node, ast.ImportFrom):
                module = resolve(node.module, node.level, package)
                if module is None:
                    # A dual-context fallback may be out-of-range in this context;
                    # still inspect its written engine target and the other branch.
                    module = node.module or ''
                    if not module:
                        report(node, 'unresolved relative import requires disposition')
                edge(node, module, importing=True)
                for alias in node.names:
                    target = '.'.join(filter(None, (module, alias.name)))
                    if alias.name == '*':
                        report(node, f'wildcard import cannot establish boundary: {module}')
                    else:
                        edge(node, target)
                    aliases[alias.asname or alias.name] = target
        # Conservative fixed point handles aliases inside functions/branches and
        # aliases assigned before their use without relying on AST walk order.
        for _ in range(len(list(ast.walk(root)))):
            changed = False
            for node in ast.walk(root):
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    value = dotted(node.value)
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for target in targets:
                        if isinstance(target, ast.Name) and value and target.id != value and aliases.get(target.id) != value:
                            # Only propagate boundary/import machinery, not arbitrary data.
                            if engine_suffix(value) is not None or value.startswith(('importlib', 'builtins.__import__')) or value == '__import__':
                                aliases[target.id] = value
                                changed = True
            if not changed:
                break
        for node in ast.walk(root):
            if isinstance(node, ast.Attribute):
                name = dotted(node)
                if name:
                    edge(node, name)
            if not isinstance(node, ast.Call):
                continue
            function = dotted(node.func)
            if function in {'getattr', 'builtins.getattr'} and node.args:
                base = dotted(node.args[0])
                if base and engine_suffix(base) is not None:
                    report(node, 'dynamic engine attribute access requires explicit review')
                if base in {'importlib', 'builtins'}:
                    report(node, 'dynamic import machinery access requires explicit disposition')
            if function not in {'__import__', 'builtins.__import__', 'importlib.import_module', 'eval', 'exec', 'runpy.run_module', 'runpy.run_path'}:
                continue
            expression = ast.unparse(node)
            allowed = any(d.get('package') == package and d.get('expression') == expression
                          and isinstance(d.get('reason'), str) and d['reason'].strip()
                          for d in dispositions)
            if not allowed:
                report(node, f'dynamic import requires explicit disposition: {expression}')
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                name = node.args[0].value
                if name.startswith('.'):
                    name = resolve(name.lstrip('.'), len(name) - len(name.lstrip('.')), package) or name
                edge(node, name, importing=True)
    return sorted(errors)


def candidate_edges(repo, rows, exports):
    paths = sorted({r['destination']['path'] for r in rows if r['destination']
                    and r['role'] in {'private-adapter', 'consumer-only'}
                    and r['destination']['path'].endswith('.py')})
    violations = []
    for path in paths:
        violations.extend(check_edges((repo / path).read_text(), exports, path=path,
                                     packages=package_contexts(repo, path)))
    return paths, violations
