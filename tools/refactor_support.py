"""Small, fail-closed stdlib primitives for the read-only refactor gate."""
import hashlib
import json
from pathlib import Path
import subprocess


class Invalid(ValueError):
    """A candidate does not satisfy the recorded contract."""


def require(condition, message):
    if not condition:
        raise Invalid(message)


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        raise Invalid(f"{path}: {exc}") from exc


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def blob(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def local(base, name):
    require(isinstance(name, str) and bool(name.strip()), f"invalid path: {name!r}")
    path = (base / name).resolve()
    require(path.is_relative_to(base.resolve()), f"path escapes {base}: {name}")
    return path


def git(repo, *args):
    try:
        return subprocess.check_output(
            ['git', '-C', str(repo), *args], stderr=subprocess.PIPE
        ).decode()
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, 'stderr', b'').decode(errors='replace')
        raise Invalid(f"read-only git {args} in {repo}: {exc}: {detail}") from exc


def tree(repo, revision):
    result = {}
    for row in git(repo, 'ls-tree', '-rz', revision).split('\0'):
        if row:
            info, path = row.split('\t', 1)
            mode, kind, oid = info.split()
            require(kind == 'blob' and mode in {'100644', '100755'},
                    f"unsupported baseline entry {path}: {info}")
            result[path] = oid
    return result


def unique(records, key, label):
    out = {}
    for item in records:
        value = key(item)
        require(value not in out, f"duplicate {label}: {value}")
        out[value] = item
    return out


class Shapes:
    """Interpret only the schema vocabulary used by this repository.

    Unknown keywords fail closed; this is deliberately not a JSON Schema library.
    """
    def __init__(self, schema):
        self.defs = schema['$defs']

    def check(self, value, spec, at='$'):
        if isinstance(spec, str):
            spec = self.defs[spec]
        supported = {'$ref', 'type', 'enum', 'anyOf', 'properties', 'required',
                     'additionalProperties', 'items'}
        require(not set(spec) - supported, f"{at}: unsupported schema keywords {set(spec)-supported}")
        if '$ref' in spec:
            ref = spec['$ref']
            require(ref.startswith('#/$defs/'), f"{at}: unsupported schema ref {ref}")
            self.check(value, self.defs[ref.split('/')[-1]], at)
        if 'anyOf' in spec:
            errors = []
            for choice in spec['anyOf']:
                try:
                    self.check(value, choice, at)
                    break
                except Invalid as exc:
                    errors.append(str(exc))
            else:
                raise Invalid(f"{at}: no matching shape: {'; '.join(errors)}")
        if 'enum' in spec:
            require(any(type(value) is type(v) and value == v for v in spec['enum']),
                    f"{at}: expected enum {spec['enum']}, got {value!r}")
        if 'type' in spec:
            types = spec['type'] if isinstance(spec['type'], list) else [spec['type']]
            mapping = {'object': dict, 'array': list, 'string': str,
                       'integer': int, 'boolean': bool, 'null': type(None)}
            require(any(type(value) is mapping[t] for t in types),
                    f"{at}: expected {types}, got {type(value).__name__}")
        if isinstance(value, dict):
            require(set(spec.get('required', [])) <= value.keys(),
                    f"{at}: missing required keys {set(spec.get('required', []))-value.keys()}")
            props = spec.get('properties', {})
            if spec.get('additionalProperties') is False:
                require(not value.keys() - props.keys(), f"{at}: unexpected keys {value.keys()-props.keys()}")
            for key in value.keys() & props.keys():
                self.check(value[key], props[key], f'{at}.{key}')
        if isinstance(value, list) and 'items' in spec:
            for i, item in enumerate(value):
                self.check(item, spec['items'], f'{at}[{i}]')


def obj(**props):
    return dict(type='object', properties=props, required=list(props), additionalProperties=False)


def array(item):
    return dict(type='array', items=item)


STRING = {'type': 'string'}
INTEGER = {'type': 'integer'}
VERSION = {'enum': [1]}
