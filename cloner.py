import tempfile
import shutil
from git import Repo

def clone_repo(github_url):
    temp_dir = tempfile.mkdtemp()
    Repo.clone_from(github_url, temp_dir)
    return temp_dir

def cleanup_repo(path):
    shutil.rmtree(path, ignore_errors=True)


if __name__ == "__main__":
    test_url = "https://github.com/karpathy/micrograd"
    print("Cloning...")
    path = clone_repo(test_url)
    print(f"Repo cloned to: {path}")