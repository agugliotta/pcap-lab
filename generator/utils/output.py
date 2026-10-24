import shutil
from pathlib import Path


def clean_output(output_dir):
    """Delete only a directory containing generated student artifacts."""
    target = Path(output_dir)
    if target.is_symlink():
        raise ValueError("Refusing to clean a symlink.")
    if not target.exists():
        return
    if not target.is_dir():
        raise ValueError("Output must be a directory.")
    for student in target.iterdir():
        if student.is_symlink() or not student.is_dir():
            raise ValueError("Output contains unrelated files; refusing to delete it.")
        files = list(student.iterdir())
        if not files or any(f.is_symlink() or not f.is_file() or f.name not in ("traffic.pcap", "answer_key.json") for f in files):
            raise ValueError("Output contains unrelated files; refusing to delete it.")
    shutil.rmtree(target)
