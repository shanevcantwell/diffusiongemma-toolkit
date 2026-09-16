"""AST fidelity against pinned native contracts, without importing the engine."""
import ast

from .refactor_support import Invalid, require, unique


def expr(node):
    return ast.unparse(node) if node is not None else None


def parameters(node):
    args = node.args
    out = []
    positional = args.posonlyargs + args.args
    defaults = [None] * (len(positional) - len(args.defaults)) + args.defaults
    def add(arg, kind, default, required):
        out.append(dict(name=arg.arg, kind=kind, annotation=expr(arg.annotation),
                        default=expr(default), required=required))
    for i, (arg, default) in enumerate(zip(positional, defaults)):
        add(arg, 'POSITIONAL_ONLY' if i < len(args.posonlyargs) else 'POSITIONAL_OR_KEYWORD', default, default is None)
    if args.vararg:
        add(args.vararg, 'VAR_POSITIONAL', None, False)
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        add(arg, 'KEYWORD_ONLY', default, default is None)
    if args.kwarg:
        add(args.kwarg, 'VAR_KEYWORD', None, False)
    return out


def definitions(root):
    """Class/function-qualified definitions, including nested functions."""
    result = {}
    def walk(node, prefix=''):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                result[name] = child
                walk(child, name + '.')
            else:
                walk(child, prefix)
    walk(root)
    return result


def check_record(record, text, label, baseline=False):
    root = ast.parse(text, filename=label)
    kind = record['kind']
    defs = definitions(root)
    name = record.get('name') or record.get('native', '').split('.')[-1]
    if kind in {'callable', 'type', 'owned-callable'}:
        matches = [n for key, n in defs.items() if key == name or ('.' not in name and key.split('.')[-1] == name)]
        require(len(matches) == 1, f"{label}: missing or ambiguous definition {name}")
        node = matches[0]
    else:
        nodes = [n for n in ast.walk(root) if getattr(n, 'lineno', None) == record['line']]
        expected = ast.Raise if kind == 'raise' else (ast.Assign, ast.AnnAssign)
        node = next((n for n in nodes if isinstance(n, expected)), None)
        require(node is not None, f"{label}: stale AST line {record['line']}")
    if baseline:
        require(node.lineno == record['line'], f"{label}: stale baseline line")
    def same(key, value):
        require(record[key] == value, f"{label}: stale AST {record['id']} {key}: expected {record[key]!r}, got {value!r}")
    if kind in {'callable', 'owned-callable'}:
        same('parameters', parameters(node))
        same('returns', expr(node.returns))
        if kind == 'callable':
            same('decorators', [expr(d) for d in node.decorator_list])
        else:
            same('async', isinstance(node, ast.AsyncFunctionDef))
    elif kind == 'type':
        same('bases', [expr(b) for b in node.bases])
        same('decorators', [expr(d) for d in node.decorator_list])
        same('fields', [dict(name=n.target.id, annotation=expr(n.annotation),
                            default=expr(n.value), required=n.value is None)
                        for n in node.body if isinstance(n, ast.AnnAssign)])
        same('methods', [dict(name=n.name, parameters=parameters(n), returns=expr(n.returns),
                             decorators=[expr(d) for d in n.decorator_list])
                         for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))])
    elif kind == 'constant':
        same('expression', expr(node.value))
        same('annotation', expr(getattr(node, 'annotation', None)))
    elif kind == 'raise':
        same('exception', expr(node.exc))
        same('cause', expr(node.cause))


def check_contracts(records, exports, source_text, source, baseline, repo, tasks):
    unique(records, lambda r: r['id'], 'contract ID across shards')
    public = unique([r for r in records if 'export' in r], lambda r: r['export'], 'export')
    require(len(exports) == len(set(exports)) == 30 and set(exports) == public.keys(),
            'exact 30 contract root exports required')
    for record in records:
        label = record['id']
        origin = record['source']
        path = origin['path']
        require(origin['repository'] == baseline['repository'] and origin['revision'] == baseline['revision']
                and origin['blob'] == source.get(path), f'{label}: wrong contract origin/blob')
        require(record['enforcement'] and set(record['enforcement']) <= tasks.keys(), f'{label}: dangling enforcement')
        if record['kind'] == 'owned-callable' and path == 'dgemma/composite.py':
            require(record['name'].endswith('.__call__') and record['id'] == 'OWN-composite-' + record['name'],
                    f'{label}: composite __call__ must be class-qualified in name and ID')
        if 'export' in record:
            require(record['consumer_reason'].strip(), f'{label}: missing consumer rationale')
            require(record['native'].startswith(path[:-3].replace('/', '.') + '.'), f'{label}: native module mismatch')
        check_record(record, source_text(path), f'baseline {label}', baseline=True)
        if (repo / path).is_file():
            check_record(record, (repo / path).read_text(), f'candidate {label}')
        for use in record.get('consumer_uses', []):
            require(use['path'] in source and use['line'] > 0, f'{label}: dangling consumer callsite')
            lines = source_text(use['path']).splitlines()
            require(use['line'] <= len(lines) and use['name'] in lines[use['line']-1], f'{label}: stale consumer callsite {use}')
    check_root(repo / 'dgemma/__init__.py', exports, public)


def check_root(path, exports, public):
    root = ast.parse(path.read_text(), filename=str(path))
    bound = {}
    alls = []
    for node in root.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == '__future__':
                continue
            require(node.level == 1, f'{path}: root must re-export canonical native objects')
            for alias in node.names:
                name = alias.asname or alias.name
                require(name not in bound, f'{path}: duplicate root binding {name}')
                bound[name] = f'dgemma.{node.module}.{alias.name}'
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == '__all__':
            alls.append(ast.literal_eval(node.value))
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        else:
            raise Invalid(f'{path}:{node.lineno}: undeclared root export or executable statement')
    require(alls == [exports], f'{path}: exact ordered 30 root exports (__all__) differ')
    require(bound == {name: r['native'] for name, r in public.items()}, f'{path}: undeclared root export or noncanonical binding')
