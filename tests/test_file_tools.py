from __future__ import annotations

from pathlib import Path

import pytest

from repo_fix_agent.tools.file_tools import (
    detect_project_type,
    find_test_files,
    grep_code,
    list_files,
    read_file,
    read_package_metadata,
    search_code,
)


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / ".git").mkdir()

    (tmp_path / "package.json").write_text('{"name":"demo"}', encoding="utf-8")
    (tmp_path / "tsconfig.json").write_text("{}", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    (tmp_path / "src" / "app.py").write_text(
        "def login_user():\n    return 'ok'\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "auth.ts").write_text(
        "export function login() { return 'ok' }\n",
        encoding="utf-8",
    )
    (tmp_path / "tests" / "test_app.py").write_text(
        "from src.app import login_user\n",
        encoding="utf-8",
    )
    (tmp_path / ".git" / "ignored.txt").write_text("ignore me", encoding="utf-8")

    return tmp_path


def test_read_file_reads_content(sample_repo: Path) -> None:
    repo_path = str(sample_repo)

    assert read_file(repo_path, "src/app.py") == "def login_user():\n    return 'ok'\n"


def test_list_files_filters_repo_contents(sample_repo: Path) -> None:
    repo_path = str(sample_repo)

    files = list_files(repo_path)
    assert "src/app.py" in files
    assert ".git/ignored.txt" not in files


def test_search_and_grep_find_expected_matches(sample_repo: Path) -> None:
    repo_path = str(sample_repo)

    assert search_code(repo_path, "login")
    assert grep_code(repo_path, "login_user")


def test_find_test_files_and_metadata_return_expected_results(sample_repo: Path) -> None:
    repo_path = str(sample_repo)

    assert find_test_files(repo_path) == ["tests/test_app.py"]
    metadata = read_package_metadata(repo_path)
    assert "package.json" in metadata
    assert "requirements.txt" in metadata


def test_detect_project_type_reports_expected_types(sample_repo: Path) -> None:
    repo_path = str(sample_repo)

    result = detect_project_type(repo_path)

    assert result["primary"] == "node"
    assert "typescript" in result["types"]
    assert "python" in result["types"]


def test_read_file_blocks_path_traversal(sample_repo: Path) -> None:
    with pytest.raises(ValueError, match="file_path must stay inside repo_path"):
        read_file(str(sample_repo), "../outside.txt")
