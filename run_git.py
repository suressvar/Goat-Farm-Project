import subprocess
import sys

git_path = r"C:\Program Files\Git\cmd\git.exe"
args = [git_path] + sys.argv[1:]

print(f"Running: {' '.join(args)}")
result = subprocess.run(args, capture_output=True, text=True)

print("--- STDOUT ---")
print(result.stdout)
print("--- STDERR ---")
print(result.stderr)
print(f"Exit code: {result.returncode}")
