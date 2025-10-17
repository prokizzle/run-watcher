"""GitHub API client for fetching workflow runs."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from github import Github, Repository, WorkflowRun
from github.GithubException import GithubException


@dataclass
class JobFailure:
    """Information about a failed job."""

    job_name: str
    step_name: str
    conclusion: str
    number: int


@dataclass
class RunInfo:
    """Information about a workflow run."""

    id: int
    name: str
    status: str  # queued, in_progress, completed
    conclusion: Optional[str]  # success, failure, cancelled, skipped, etc.
    created_at: datetime
    updated_at: datetime
    html_url: str
    head_branch: str
    head_sha: str
    run_number: int

    @property
    def display_status(self) -> str:
        """Get a display-friendly status."""
        if self.status != "completed":
            return self.status
        return self.conclusion or "unknown"

    @property
    def is_success(self) -> bool:
        """Check if run was successful."""
        return self.conclusion == "success"

    @property
    def is_failure(self) -> bool:
        """Check if run failed."""
        return self.conclusion == "failure"

    @property
    def is_running(self) -> bool:
        """Check if run is currently running."""
        return self.status == "in_progress"


class GitHubClient:
    """Client for interacting with GitHub API."""

    def __init__(self, token: str):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token
        """
        self.github = Github(token)
        self.user = self.github.get_user()

    def search_repositories(self, query: str, org: Optional[str] = None) -> List[tuple[str, str]]:
        """Search for repositories.

        Args:
            query: Search query
            org: Optional organization to limit search to

        Returns:
            List of (full_name, description) tuples
        """
        search_query = query
        if org:
            search_query = f"{query} org:{org}"

        try:
            repos = self.github.search_repositories(search_query, sort="updated")
            return [(repo.full_name, repo.description or "") for repo in repos[:20]]
        except GithubException as e:
            return []

    def get_repository(self, full_name: str) -> Optional[Repository.Repository]:
        """Get a repository by full name.

        Args:
            full_name: Repository full name (owner/repo)

        Returns:
            Repository object or None if not found
        """
        try:
            return self.github.get_repo(full_name)
        except GithubException:
            return None

    def get_recent_runs(self, repo_full_name: str, limit: int = 10) -> List[RunInfo]:
        """Get recent workflow runs for a repository.

        Args:
            repo_full_name: Repository full name (owner/repo)
            limit: Maximum number of runs to fetch

        Returns:
            List of RunInfo objects
        """
        repo = self.get_repository(repo_full_name)
        if not repo:
            return []

        try:
            runs = repo.get_workflow_runs()
            result = []

            for run in runs[:limit]:
                result.append(RunInfo(
                    id=run.id,
                    name=run.name or "Workflow",
                    status=run.status,
                    conclusion=run.conclusion,
                    created_at=run.created_at,
                    updated_at=run.updated_at,
                    html_url=run.html_url,
                    head_branch=run.head_branch,
                    head_sha=run.head_sha[:7],
                    run_number=run.run_number,
                ))

            return result
        except GithubException:
            return []

    def get_run_logs(self, repo_full_name: str, run_id: int) -> Optional[str]:
        """Get logs for a specific workflow run.

        Args:
            repo_full_name: Repository full name (owner/repo)
            run_id: Workflow run ID

        Returns:
            Log content or None if not available
        """
        repo = self.get_repository(repo_full_name)
        if not repo:
            return None

        try:
            # Note: Getting actual logs requires downloading zip files
            # For now, we'll return a placeholder
            run = repo.get_workflow_run(run_id)
            jobs = run.jobs()

            log_lines = []
            for job in jobs:
                log_lines.append(f"Job: {job.name}")
                log_lines.append(f"Status: {job.status}")
                log_lines.append(f"Conclusion: {job.conclusion}")
                log_lines.append("")

                for step in job.steps:
                    status_icon = "✓" if step.conclusion == "success" else "✗" if step.conclusion == "failure" else "○"
                    log_lines.append(f"  {status_icon} {step.name} - {step.conclusion or step.status}")

                log_lines.append("")

            return "\n".join(log_lines)
        except GithubException:
            return None

    def get_run_failures(self, repo_full_name: str, run_id: int) -> List[JobFailure]:
        """Get failed jobs and steps for a workflow run.

        Args:
            repo_full_name: Repository full name (owner/repo)
            run_id: Workflow run ID

        Returns:
            List of JobFailure objects for failed steps
        """
        repo = self.get_repository(repo_full_name)
        if not repo:
            return []

        try:
            run = repo.get_workflow_run(run_id)
            jobs = run.jobs()

            failures = []
            for job in jobs:
                for step in job.steps:
                    if step.conclusion in ("failure", "timed_out", "action_required"):
                        failures.append(JobFailure(
                            job_name=job.name,
                            step_name=step.name,
                            conclusion=step.conclusion,
                            number=step.number
                        ))

            return failures
        except GithubException:
            return []

    def get_job_logs(self, repo_full_name: str, run_id: int, job_name: str) -> Optional[str]:
        """Get logs for a specific job in a workflow run.

        Args:
            repo_full_name: Repository full name (owner/repo)
            run_id: Workflow run ID
            job_name: Name of the job to get logs for

        Returns:
            Log content or None if not available
        """
        repo = self.get_repository(repo_full_name)
        if not repo:
            return None

        try:
            run = repo.get_workflow_run(run_id)
            jobs = run.jobs()

            # Find the matching job
            target_job = None
            for job in jobs:
                if job.name == job_name:
                    target_job = job
                    break

            if not target_job:
                return None

            # Build a detailed log from job steps
            log_lines = []
            log_lines.append(f"Job: {target_job.name}")
            log_lines.append(f"Status: {target_job.status}")
            log_lines.append(f"Conclusion: {target_job.conclusion or 'N/A'}")
            log_lines.append(f"Started: {target_job.started_at}")
            log_lines.append(f"Completed: {target_job.completed_at or 'N/A'}")
            log_lines.append("=" * 60)
            log_lines.append("")

            for step in target_job.steps:
                status_icon = "✓" if step.conclusion == "success" else "✗" if step.conclusion == "failure" else "⟳" if step.status == "in_progress" else "○"
                status_style = step.conclusion or step.status

                log_lines.append(f"{status_icon} Step {step.number}: {step.name}")
                log_lines.append(f"  Status: {status_style}")

                if step.started_at:
                    log_lines.append(f"  Started: {step.started_at}")
                if step.completed_at:
                    log_lines.append(f"  Completed: {step.completed_at}")

                log_lines.append("")

            log_lines.append("=" * 60)
            log_lines.append("")
            log_lines.append("Note: Full step logs require downloading from GitHub.")
            log_lines.append(f"URL: {target_job.html_url}")

            return "\n".join(log_lines)
        except GithubException as e:
            return f"Error fetching logs: {e}"
