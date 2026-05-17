import subprocess
import os

git_path = r"C:\Program Files\Git\cmd\git.exe"

# Read command from cmd.txt
if not os.path.exists("cmd.txt"):
    print("cmd.txt does not exist")
    exit(1)

with open("cmd.txt", "r") as f:
    cmd_str = f.read().strip()

# Split command
args = cmd_str.split()
if not args:
    print("Empty command")
    exit(1)

# Replace 'git' with actual git path if it's the first word
if args[0].lower() == 'git':
    args[0] = git_path

print(f"Executing: {args}")
result = subprocess.run(args, capture_output=True, text=True)

with open("output.txt", "w", encoding="utf-8") as f:
    f.write("--- STDOUT ---\n")
    f.write(result.stdout)
    f.write("\n--- STDERR ---\n")
    f.write(result.stderr)
    f.write(f"\nExit code: {result.returncode}\n")

print("Done! Check output.txt")
