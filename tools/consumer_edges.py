"""Direct consumer edges only: no imports, sys.modules scans, or execution.

Conservative alias propagation intentionally visits both dual-context branches.
Dynamic imports need exact expression + context + rationale dispositions; an
engine-internal literal can never be waived by a disposition.
"""
import ast
from pathlib import Path


# Shared by assignment propagation and call inspection, including bound builtins.
DYNAMIC_PRIMITIVES = frozenset({
    '__import__', 'builtins.__import__', 'importlib.import_module',
    'eval', 'builtins.eval', 'exec', 'builtins.exec',
    'runpy.run_module', 'runpy.run_path',
})
DYNAMIC_MODULES = frozenset(name.split('.')[0] for name in DYNAMIC_PRIMITIVES if '.' in name)


def assignment_binding(name):
    """Finite boundary-relevant representatives, not arbitrary dotted strings.

    For engine objects only the first root member and first private traversal
    matter to edge(). Discard intervening public attributes so x = x.member
    cycles cannot grow paths forever. Module/primitive bindings are exact.
    """
    suffix = engine_suffix(name)
    if suffix is not None:
        parts = ['dgemma'] + suffix[:1]
        if suffix and not suffix[0].startswith('_'):
            parts += next(([part] for part in suffix[1:] if part.startswith('_')), [])
        return '.'.join(parts)
    if name in DYNAMIC_MODULES or name in DYNAMIC_PRIMITIVES:
        return name
    return None


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
    nodes = list(ast.walk(root))
    errors = set()
    for package in packages:
        # May-bindings: neither later imports nor sibling scopes erase an edge.
        aliases = {}
        def bind(name, values):
            known = aliases.setdefault(name, set())
            added = values - known
            known.update(added)
            return bool(added)
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
                return aliases.get(node.id, {node.id})
            if isinstance(node, ast.Attribute):
                return {f'{base}.{node.attr}' for base in dotted(node.value)}
            return set()
        for node in nodes:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    edge(node, alias.name, importing=True)
                    bind(alias.asname or alias.name.split('.')[0],
                         {alias.name if alias.asname else alias.name.split('.')[0]})
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
                    bind(alias.asname or alias.name, {target})
        # Monotone fixed point over finite representatives handles functions,
        # branches and forward/chained aliases without flow-sensitive semantics.
        while True:
            changed = False
            for node in nodes:
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    values = {binding for value in dotted(node.value)
                              if (binding := assignment_binding(value)) is not None}
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for target in targets:
                        if isinstance(target, ast.Name) and values:
                            changed = bind(target.id, values) or changed
            if not changed:
                break
        for node in nodes:
            if isinstance(node, ast.Attribute):
                for name in dotted(node):
                    edge(node, name)
            if not isinstance(node, ast.Call):
                continue
            functions = dotted(node.func)
            if functions & {'getattr', 'builtins.getattr'} and node.args:
                bases = dotted(node.args[0])
                if any(engine_suffix(base) is not None for base in bases):
                    report(node, 'dynamic engine attribute access requires explicit review')
                if bases & DYNAMIC_MODULES:
                    report(node, 'dynamic import machinery access requires explicit disposition')
            if not functions & DYNAMIC_PRIMITIVES:
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
