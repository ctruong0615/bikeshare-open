# Submission checklist and GitHub workflow

Repository: https://github.com/ctruong0615/bikeshare-open (created private).

The repository has the required unmodified starter root commit, a genuinely
failing feature-test commit followed by its implementation, separate fault
demonstration commits, final metrics, and a report draft. Keep that history;
do not squash it into one commit.

## What still needs the group

- Follow the instructor's shared-repository branch-audit clarification:
  Calvin audits Faline, Faline audits Andrew, and Andrew audits Calvin before
  merge. Calvin's accepted audit of Faline is recorded in `docs/AUDIT.md`;
  the other two reviews are pending. No external-group repository is needed
  for this instructed team workflow.
- Review `REPORT.md` and the agent-proposed decisions in `docs/DECISIONS.md`.
  Record what the group actually agrees with. Do not assign invented work to
  members or describe scripted restores as local-model reasoning turns.
  An all-member review is a recommendation, not an extra required deliverable.
- Confirm the own-repository audit is a successful real run and address any
  findings. An error record is evidence of failure, not a completed audit.
- Ensure graders and collaborators can access the private GitHub repository
  using the course's required access arrangements before submitting its URL.

## Push from your own PowerShell

The browser session created the repository, but terminal authentication is
separate. Windows Credential Manager is unavailable inside the Codex sandbox.
Run this outside the sandbox and complete any GitHub sign-in prompt:

```powershell
$assignmentRepo = "C:/Users/Calvin/Documents/Codex/2026-11-18/https-dsc-capstone-org-2026-27/outputs/bikeshare-open"
git -c "safe.directory=$assignmentRepo" -C $assignmentRepo push -u origin main
```

The remote is already configured. After later commits, use the same command
again. The path-specific trust exception is needed because the sandbox account
created the repository; it applies only to this command. Push each completed milestone and
push once more after the peer audit and final report review. Do not add the
virtual environment, downloaded tools, or model files to Git.

## Open the local environment

Run the sibling `outputs/Open-Assignment.ps1` in PowerShell. It prepares this
session's PATH, activates the project Python environment, and starts Ollama
if necessary. Then `make all`, `make test`, `make check-model`, and `claude`
are available in that terminal. This is a portable workspace setup rather
than a machine-wide install. Keep the workspace's `work/` folder: it contains
the downloaded tools and model. Teammates should follow Appendix A to set up
their own laptops; only project code and committed evidence belong on GitHub.
