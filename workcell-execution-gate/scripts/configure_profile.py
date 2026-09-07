"""Select only the workspace identity from observed Docker security options."""
import json
from pathlib import Path
import sys


def configure(definition, security_options):
    if not isinstance(security_options, list) or not all(isinstance(x, str) for x in security_options):
        raise ValueError('Docker SecurityOptions must be a string list')
    result = json.loads(json.dumps(definition))
    rootless = any(x.split(',')[0] == 'name=rootless' for x in security_options)
    result.setdefault('workspace', {})['run_as'] = 'rootless' if rootless else 'host'
    return result


if __name__ == '__main__':
    source, security, output = map(Path, sys.argv[1:])
    output.write_text(json.dumps(configure(json.loads(source.read_text()), json.loads(security.read_text())), indent=2) + '\n')
