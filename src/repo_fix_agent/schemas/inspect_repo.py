from typing import Annotated

from pydantic import BaseModel, Field


class SelectedFile(BaseModel):
    path: Annotated[str, Field(
        description="Relative path of the selected file")]
    reason: Annotated[str, Field(description="Why this file is relevant")]


class InspectRepoOutput(BaseModel):
    project_summary: Annotated[
        str,
        Field(description="Short summary of the repo/project"),
    ]
    selected_files: Annotated[
        list[SelectedFile],
        Field(description="Files that should be read for the next planning step"),
    ]
    inspection_notes: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Important notes discovered during repo inspection",
        ),
    ]
    project_type: Annotated[
        str,
        Field(description="Type of project (e.g. 'node', 'python', 'react', etc.)"),
    ]
    test_files: Annotated[
        list[str],
        Field(description="Files that are test files"),
    ]
