#!/usr/bin/env python3
"""
Incremental Extraction for Kraang

Uses git to detect changes and extract facts only from modified files.
Expected: 80-95% reduction in work for incremental updates.
"""

import subprocess
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ChangeSet:
    """Detected changes in the repository"""
    modified_files: List[str]
    added_files: List[str]
    deleted_files: List[str]
    modified_line_ranges: Dict[str, List[Tuple[int, int]]]  # file -> [(start, end)]
    commit_hash: str
    timestamp: str


@dataclass
class ExtractionState:
    """State of last extraction"""
    last_commit: Optional[str]
    last_timestamp: str
    artifact_hashes: Dict[str, str]  # artifact_id -> content_hash
    total_facts: int


class GitAnalyzer:
    """Detect changes using git"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

        # Verify git repo
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")

    def get_current_commit(self) -> str:
        """Get current git commit hash"""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to get commit hash: {result.stderr}")

        return result.stdout.strip()

    def get_changed_files(self, since_commit: Optional[str] = None) -> ChangeSet:
        """
        Get files changed since a specific commit.

        Args:
            since_commit: Commit to compare against (None = all uncommitted changes)

        Returns:
            ChangeSet with detected changes
        """
        if since_commit:
            # Compare against specific commit
            cmd = ["git", "diff", "--name-status", f"{since_commit}..HEAD"]
        else:
            # Get uncommitted changes
            cmd = ["git", "diff", "--name-status"]

        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to get diff: {result.stderr}")

        # Parse output
        modified_files = []
        added_files = []
        deleted_files = []

        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) < 2:
                continue

            status = parts[0]
            file_path = parts[1]

            if status == 'M':
                modified_files.append(file_path)
            elif status == 'A':
                added_files.append(file_path)
            elif status == 'D':
                deleted_files.append(file_path)

        # Get line ranges for modified files
        modified_line_ranges = {}
        for file_path in modified_files:
            ranges = self._get_modified_line_ranges(file_path, since_commit)
            if ranges:
                modified_line_ranges[file_path] = ranges

        return ChangeSet(
            modified_files=modified_files,
            added_files=added_files,
            deleted_files=deleted_files,
            modified_line_ranges=modified_line_ranges,
            commit_hash=self.get_current_commit(),
            timestamp=datetime.now().isoformat()
        )

    def _get_modified_line_ranges(
        self,
        file_path: str,
        since_commit: Optional[str] = None
    ) -> List[Tuple[int, int]]:
        """Get line ranges modified in a file"""
        if since_commit:
            cmd = ["git", "diff", "-U0", f"{since_commit}..HEAD", "--", file_path]
        else:
            cmd = ["git", "diff", "-U0", "--", file_path]

        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return []

        # Parse diff output for line ranges
        ranges = []
        for line in result.stdout.split('\n'):
            if line.startswith('@@'):
                # Extract line range from @@ -a,b +c,d @@
                try:
                    parts = line.split('@@')[1].strip().split()
                    if len(parts) >= 2:
                        # Parse +c,d (new file line range)
                        new_range = parts[1]
                        if new_range.startswith('+'):
                            new_range = new_range[1:]  # Remove +

                        if ',' in new_range:
                            start, count = map(int, new_range.split(','))
                            end = start + count
                        else:
                            start = int(new_range)
                            end = start + 1

                        ranges.append((start, end))
                except (ValueError, IndexError):
                    continue

        return ranges


class IncrementalExtractionPlanner:
    """Plan what to extract based on changes"""

    def __init__(self, kraang_dir: Path = Path(".kraang")):
        self.kraang_dir = kraang_dir
        self.state_file = kraang_dir / "extraction_state.json"

    def load_state(self) -> Optional[ExtractionState]:
        """Load last extraction state"""
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)

            return ExtractionState(
                last_commit=data.get('last_commit'),
                last_timestamp=data['last_timestamp'],
                artifact_hashes=data.get('artifact_hashes', {}),
                total_facts=data.get('total_facts', 0)
            )
        except Exception as e:
            print(f"Warning: Could not load extraction state: {e}")
            return None

    def save_state(self, state: ExtractionState):
        """Save extraction state"""
        self.kraang_dir.mkdir(parents=True, exist_ok=True)

        with open(self.state_file, 'w') as f:
            json.dump({
                'last_commit': state.last_commit,
                'last_timestamp': state.last_timestamp,
                'artifact_hashes': state.artifact_hashes,
                'total_facts': state.total_facts
            }, f, indent=2)

    def plan_extraction(
        self,
        changeset: ChangeSet,
        artifact_paths: Dict[str, str]  # artifact_id -> file_path
    ) -> Dict[str, str]:
        """
        Plan what needs to be extracted.

        Args:
            changeset: Detected changes from git
            artifact_paths: Mapping of artifact IDs to file paths

        Returns:
            Dict of artifact_id -> reason for extraction
        """
        to_extract = {}

        # Map file paths to artifact IDs (reverse lookup)
        path_to_artifact = {v: k for k, v in artifact_paths.items()}

        # Added files
        for file_path in changeset.added_files:
            if file_path in path_to_artifact:
                artifact_id = path_to_artifact[file_path]
                to_extract[artifact_id] = "new file"

        # Modified files
        for file_path in changeset.modified_files:
            if file_path in path_to_artifact:
                artifact_id = path_to_artifact[file_path]
                line_ranges = changeset.modified_line_ranges.get(file_path, [])
                if line_ranges:
                    total_lines = sum(end - start for start, end in line_ranges)
                    to_extract[artifact_id] = f"modified ({total_lines} lines changed)"
                else:
                    to_extract[artifact_id] = "modified (full re-extraction)"

        # Deleted files (mark for fact removal)
        deleted_artifacts = []
        for file_path in changeset.deleted_files:
            if file_path in path_to_artifact:
                deleted_artifacts.append(path_to_artifact[file_path])

        if deleted_artifacts:
            print(f"\nDeleted artifacts (facts will be removed): {deleted_artifacts}")

        return to_extract


class IncrementalExtractor:
    """Main incremental extraction coordinator"""

    def __init__(self, repo_path: str = ".", kraang_dir: Path = Path(".kraang")):
        self.git = GitAnalyzer(repo_path)
        self.planner = IncrementalExtractionPlanner(kraang_dir)

    def analyze_changes(self) -> Tuple[ChangeSet, Dict[str, str]]:
        """
        Analyze changes since last extraction.

        Returns:
            (ChangeSet, extraction_plan)
        """
        # Load last state
        state = self.planner.load_state()

        # Get changes
        if state and state.last_commit:
            changeset = self.git.get_changed_files(since_commit=state.last_commit)
            print(f"Changes since commit {state.last_commit[:8]}:")
        else:
            print("No previous extraction state, treating as initial extraction")
            changeset = ChangeSet(
                modified_files=[],
                added_files=[],
                deleted_files=[],
                modified_line_ranges={},
                commit_hash=self.git.get_current_commit(),
                timestamp=datetime.now().isoformat()
            )
            return changeset, {}

        # Display changes
        print(f"  Modified: {len(changeset.modified_files)} files")
        print(f"  Added: {len(changeset.added_files)} files")
        print(f"  Deleted: {len(changeset.deleted_files)} files")

        return changeset, {}

    def update_state(self, total_facts: int, artifact_hashes: Dict[str, str]):
        """Update extraction state after extraction"""
        state = ExtractionState(
            last_commit=self.git.get_current_commit(),
            last_timestamp=datetime.now().isoformat(),
            artifact_hashes=artifact_hashes,
            total_facts=total_facts
        )

        self.planner.save_state(state)


# CLI interface for testing
if __name__ == "__main__":
    import sys

    # Create incremental extractor
    try:
        extractor = IncrementalExtractor()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Analyze changes
    changeset, plan = extractor.analyze_changes()

    if not changeset.modified_files and not changeset.added_files:
        print("\n✓ No changes detected")
    else:
        print("\nChangeSet Summary:")
        print(f"  Commit: {changeset.commit_hash[:8]}")
        print(f"  Timestamp: {changeset.timestamp}")

        if changeset.modified_files:
            print(f"\n  Modified files ({len(changeset.modified_files)}):")
            for f in changeset.modified_files[:10]:
                ranges = changeset.modified_line_ranges.get(f, [])
                if ranges:
                    total_lines = sum(end - start for start, end in ranges)
                    print(f"    • {f} ({total_lines} lines changed)")
                else:
                    print(f"    • {f}")

        if changeset.added_files:
            print(f"\n  Added files ({len(changeset.added_files)}):")
            for f in changeset.added_files[:10]:
                print(f"    • {f}")

        if changeset.deleted_files:
            print(f"\n  Deleted files ({len(changeset.deleted_files)}):")
            for f in changeset.deleted_files[:10]:
                print(f"    • {f}")
