ALLOWED_COMMAND_PREFIXES: list[list[str]] = [
    ["git", "status"],
    ["git", "diff"],
    ["git", "log"],
    ["git", "show"],
    ["git", "rev-parse"],
    ["git", "ls-files"],
    ["npm", "test"],
    ["npm", "run", "test"],
    ["npm", "run", "typecheck"],
    ["npm", "run", "lint"],
    ["pytest"],
    ["python", "-m", "pytest"],
    ["python3", "-m", "pytest"],
    ["mvn", "test"],
    ["./mvnw", "test"],
    ["gradle", "test"],
    ["./gradlew", "test"],
]

BLOCKED_TOKENS = {
    "rm",
    "sudo",
    "su",
    "chmod",
    "chown",
    "curl",
    "wget",
    "scp",
    "ssh",
    "docker",
    "kubectl",
    "git push",
    "npm publish",
}

READONLY_GIT_COMMANDS = {
    "status",
    "diff",
    "log",
    "show",
    "rev-parse",
    "ls-files",
}

SAFE_WRITE_GIT_COMMANDS = {"restore", "checkout"}

ALLOWED_TEST_PREFIXES: list[list[str]] = [
    ["npm", "test"],
    ["npm", "run", "test"],
    ["npm", "run", "typecheck"],
    ["npm", "run", "lint"],
    ["pytest"],
    ["python", "-m", "pytest"],
    ["python3", "-m", "pytest"],
    ["mvn", "test"],
    ["./mvnw", "test"],
    ["gradle", "test"],
    ["./gradlew", "test"],
]
