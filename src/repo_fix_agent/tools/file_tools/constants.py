MAX_FILES = 1000
TOOL_READ_CHAR_LIMIT = 12_000
CONTENT_SEARCH_CHAR_LIMIT = 80 * 1024  # 80 KB
SUMMARY_INPUT_CHAR_LIMIT = 80 * 1024  # 80 KB

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "coverage",
    ".next",
    ".turbo",
}

IGNORE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".mp4",
    ".mp3",
    ".woff",
    ".woff2",
}
