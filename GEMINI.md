# Project Instructions (GEMINI.md)

## Workflow Conventions

### GitHub Interactions
- **Use the GitHub CLI (`gh`):** All GitHub-related actions, including issue management, pull request creation, and repository settings/information retrieval, must be performed using the `gh` tool.

### Issue Management & Pull Requests
- **Never close issues directly.** All issues must be closed via a Pull Request.
- **PR Descriptions:** Always include the keyword `Closes #<issue_number>` in the PR description to ensure the issue is automatically closed upon merging.
- **Branching:** Use descriptive branch names prefixed with the issue type (e.g., `feature/issue-2`, `fix/issue-5`).

### Testing Requirements
- **Mandatory Testing:** Every new feature, attack vector, or bug fix MUST include corresponding unit or integration tests.
- **Validation:** All tests must pass locally (`python main.py test`) before pushing changes or creating a PR.
- **Coverage:** Ensure new attack modules are tested for structure, metadata, and integration with the generator.
