#!/usr/bin/env python
"""
Vercel build script for Django
This script runs collectstatic during Vercel deployment with caching optimization
"""
import os
import subprocess
import hashlib
from pathlib import Path

def get_static_files_hash():
    """Generate hash of static source files to detect changes"""
    hash_md5 = hashlib.md5()

    # Hash assets directory
    assets_dir = Path("assets")
    if assets_dir.exists():
        for file_path in sorted(assets_dir.rglob("*")):
            if file_path.is_file():
                hash_md5.update(str(file_path).encode())
                hash_md5.update(file_path.read_bytes())

    return hash_md5.hexdigest()

def should_collect_static():
    """Check if we need to run collectstatic"""
    cache_file = Path(".vercel_static_cache")
    current_hash = get_static_files_hash()

    if not cache_file.exists():
        print("No cache found, running collectstatic...")
        cache_file.write_text(current_hash)
        return True

    cached_hash = cache_file.read_text().strip()
    if cached_hash != current_hash:
        print("Static files changed, running collectstatic...")
        cache_file.write_text(current_hash)
        return True

    print("Static files unchanged, skipping collectstatic (using cache)...")
    return False

# Run migrations
print("Running Django migrations...")
subprocess.run([
    "python", "manage.py", "migrate", "--noinput"
], check=True)
print("Migrations completed successfully!")

# Run collectstatic
print("Running Django collectstatic...")
subprocess.run([
    "python", "manage.py", "collectstatic", "--noinput", "--clear"
], check=True)
print("Static files collected successfully!")
