def inspect_repo_node(repo_path: str) -> str:
    """
    Add/Update state:
    - relevant_files: list[str]
    - files_read: dict[str, str]
    - file_summaries: dict[str, str]
    - repo_summary: str
    - project_type: str
    - inspection_notes: list[str]
    - test_files: list[str]
    - entry_points: list[str]
    - config_files: list[str]

    Inspect repo node flow:
      1. Detect project type
      2. Get compact file tree
      3. Search using likely_areas from analyze_request
      4. Search using keywords from user_request
      5. Find test files if needs_tests = true
      6. Pick top relevant files
      7. Read those files
      8. Summarize long files
      9. Store files_read + relevant_files + notes
    """
    pass
