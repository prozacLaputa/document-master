#!/usr/bin/env python3
"""Build a portable skill ZIP and verify every archived file."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

root = Path(__file__).resolve().parents[1]
source = root / "document-master"
version = re.search(r'version: "([0-9]+\.[0-9]+\.[0-9]+)"', (source / "SKILL.md").read_text()).group(1)
paths = sorted(source.rglob("*"))
if any(p.is_symlink() for p in paths):
    raise SystemExit("Symlinks are not allowed")
files = [p for p in paths if p.is_file()]
for p in files:
    if any(part.startswith(".") or part in ("__pycache__", "node_modules") for part in p.relative_to(source).parts):
        raise SystemExit("Unexpected hidden or generated file")
output = root / "dist"
output.mkdir(exist_ok=True)
archive = output / f"document-master-{version}.zip"
manifest = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
    for p in files:
        info = zipfile.ZipInfo(str(p.relative_to(root)), (2020, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, p.read_bytes())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert {name: hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist()} == manifest
(output / f"document-master-{version}-manifest.json").write_text(json.dumps({"version": version, "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "files": manifest}, indent=2) + "\n")
print(f"Verified {len(files)} files: {archive.name}")
