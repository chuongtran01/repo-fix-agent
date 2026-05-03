from __future__ import annotations

from pathlib import Path

import pytest

from repo_fix_agent.tools.file_tools import (
    apply_patch,
    create_file,
    detect_project_type,
    find_test_files,
    grep_code,
    list_files,
    read_file,
    read_package_metadata,
    replace_in_file,
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


def test_read_file_can_truncate_when_requested(sample_repo: Path) -> None:
    repo_path = str(sample_repo)

    truncated = read_file(repo_path, "src/app.py", max_chars=10)

    assert truncated.startswith("def login_")
    assert truncated.endswith("...[TRUNCATED]...")


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


def test_create_file_creates_parents_and_reports_creation(sample_repo: Path) -> None:
    repo_path = str(sample_repo)

    result = create_file(repo_path, "nested/new_test.py", "assert True\n")

    assert result == {
        "path": "nested/new_test.py",
        "created": True,
        "overwritten": False,
        "parent_created": True,
    }
    assert (sample_repo / "nested" / "new_test.py").read_text(encoding="utf-8") == "assert True\n"


def test_replace_in_file_updates_exact_match(sample_repo: Path) -> None:
    repo_path = str(sample_repo)

    result = replace_in_file(
        repo_path,
        "src/app.py",
        "return 'ok'",
        "return 'fixed'",
    )

    assert result == {"path": "src/app.py", "replacements": 1}
    assert "return 'fixed'" in read_file(repo_path, "src/app.py")


def test_apply_patch_applies_multiple_hunks_atomically(sample_repo: Path) -> None:
    repo_path = str(sample_repo)

    result = apply_patch(
        repo_path,
        "src/app.py",
        [
            {"old": "def login_user():", "new": "def login_user(email: str):"},
            {"old": "return 'ok'", "new": "return email"},
        ],
    )

    assert result == {"path": "src/app.py", "hunks_applied": 2}
    updated = read_file(repo_path, "src/app.py")
    assert "def login_user(email: str):" in updated
    assert "return email" in updated


def test_apply_patch_rejects_ambiguous_single_hunk(tmp_path: Path) -> None:
    file_path = tmp_path / "dup.py"
    file_path.write_text("x = 1\nx = 1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must appear exactly once"):
        apply_patch(
            str(tmp_path),
            "dup.py",
            [{"old": "x = 1", "new": "x = 2"}],
        )
