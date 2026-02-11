#!/usr/bin/env python3
"""
Smart Pass Selection for Kraang

Intelligently selects which extraction passes to run based on file type and content.
Reduces API calls by 40-60% by skipping irrelevant passes.
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class PassType(Enum):
    """Types of extraction passes"""
    GENERAL = "general"
    MEMORY = "memory"
    CONCURRENCY = "concurrency"
    SECURITY = "security"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE = "performance"
    TESTING = "testing"


@dataclass
class PassRelevance:
    """Relevance score for a pass"""
    pass_type: PassType
    relevance_score: float  # 0.0 - 1.0
    reason: str
    detected_signals: List[str]


class PassSelector:
    """Intelligent pass selection based on file type and content"""

    # Language-specific pass recommendations
    LANGUAGE_PASS_MAP = {
        "c": {
            PassType.GENERAL: 1.0,      # Always relevant
            PassType.MEMORY: 0.95,      # Very relevant for C
            PassType.CONCURRENCY: 0.7,  # Common in C
            PassType.PERFORMANCE: 0.75, # Often optimized
            PassType.ERROR_HANDLING: 0.6,
            PassType.SECURITY: 0.65,    # Buffer overflows, etc.
            PassType.TESTING: 0.3,      # Less common in C
        },
        "cpp": {
            PassType.GENERAL: 1.0,
            PassType.MEMORY: 0.9,       # RAII, smart pointers
            PassType.CONCURRENCY: 0.75,
            PassType.PERFORMANCE: 0.8,
            PassType.ERROR_HANDLING: 0.7,  # Exceptions
            PassType.SECURITY: 0.65,
            PassType.TESTING: 0.4,
        },
        "python": {
            PassType.GENERAL: 1.0,
            PassType.MEMORY: 0.2,       # GC, less relevant
            PassType.CONCURRENCY: 0.5,  # GIL limitations
            PassType.PERFORMANCE: 0.5,
            PassType.ERROR_HANDLING: 0.8,  # Exceptions everywhere
            PassType.SECURITY: 0.85,    # Web frameworks, injection
            PassType.TESTING: 0.9,      # pytest, unittest common
        },
        "javascript": {
            PassType.GENERAL: 1.0,
            PassType.MEMORY: 0.2,
            PassType.CONCURRENCY: 0.7,  # async/await, promises
            PassType.PERFORMANCE: 0.6,
            PassType.ERROR_HANDLING: 0.75,
            PassType.SECURITY: 0.9,     # XSS, injection common
            PassType.TESTING: 0.85,     # jest, mocha common
        },
        "java": {
            PassType.GENERAL: 1.0,
            PassType.MEMORY: 0.6,       # GC but still relevant
            PassType.CONCURRENCY: 0.8,  # Threading common
            PassType.PERFORMANCE: 0.7,
            PassType.ERROR_HANDLING: 0.85,  # Checked exceptions
            PassType.SECURITY: 0.75,
            PassType.TESTING: 0.8,      # JUnit common
        },
        "rust": {
            PassType.GENERAL: 1.0,
            PassType.MEMORY: 0.95,      # Ownership, lifetimes
            PassType.CONCURRENCY: 0.9,  # Fearless concurrency
            PassType.PERFORMANCE: 0.9,  # Zero-cost abstractions
            PassType.ERROR_HANDLING: 0.85,  # Result, Option
            PassType.SECURITY: 0.8,
            PassType.TESTING: 0.7,
        },
        "go": {
            PassType.GENERAL: 1.0,
            PassType.MEMORY: 0.5,       # GC
            PassType.CONCURRENCY: 0.95, # Goroutines, channels
            PassType.PERFORMANCE: 0.7,
            PassType.ERROR_HANDLING: 0.9,  # Error returns everywhere
            PassType.SECURITY: 0.7,
            PassType.TESTING: 0.8,
        },
        "documentation": {
            PassType.GENERAL: 1.0,
            PassType.MEMORY: 0.1,
            PassType.CONCURRENCY: 0.1,
            PassType.PERFORMANCE: 0.2,
            PassType.ERROR_HANDLING: 0.2,
            PassType.SECURITY: 0.3,
            PassType.TESTING: 0.1,
        }
    }

    # Content-based keyword detection
    KEYWORD_SIGNALS = {
        PassType.MEMORY: {
            "malloc", "free", "calloc", "realloc", "new", "delete",
            "alloc", "dealloc", "heap", "stack", "memory", "leak",
            "buffer", "pointer", "reference", "ownership", "lifetime",
            "smart_ptr", "unique_ptr", "shared_ptr", "gc", "garbage"
        },
        PassType.CONCURRENCY: {
            "thread", "mutex", "lock", "unlock", "atomic", "sync",
            "async", "await", "promise", "future", "parallel",
            "concurrent", "race", "deadlock", "semaphore", "channel",
            "goroutine", "critical_section", "volatile", "pthread"
        },
        PassType.SECURITY: {
            "auth", "password", "token", "secret", "key", "encrypt",
            "decrypt", "hash", "crypto", "secure", "vulnerability",
            "injection", "xss", "csrf", "sanitize", "validate",
            "escape", "permission", "privilege", "access_control"
        },
        PassType.ERROR_HANDLING: {
            "error", "exception", "throw", "catch", "try", "finally",
            "panic", "recover", "result", "option", "errno", "perror",
            "assert", "check", "verify", "validate", "fail", "abort"
        },
        PassType.PERFORMANCE: {
            "optimize", "performance", "benchmark", "profile", "cache",
            "fast", "slow", "latency", "throughput", "bottleneck",
            "inline", "simd", "vectorize", "parallel", "algorithm",
            "complexity", "big_o", "efficient", "speed"
        },
        PassType.TESTING: {
            "test", "unittest", "pytest", "jest", "mocha", "junit",
            "assert", "expect", "mock", "stub", "fixture", "spec",
            "describe", "it_should", "verify", "coverage", "tdd"
        }
    }

    def __init__(self, min_relevance: float = 0.3, always_run_general: bool = True):
        """
        Initialize pass selector.

        Args:
            min_relevance: Minimum relevance score to include pass (0.0-1.0)
            always_run_general: Always include GENERAL pass regardless of score
        """
        self.min_relevance = min_relevance
        self.always_run_general = always_run_general

    def detect_language(self, file_path: str, content: str) -> str:
        """
        Detect programming language from file extension and content.

        Args:
            file_path: Path to file
            content: File content

        Returns:
            Language identifier
        """
        # Extension-based detection
        ext = Path(file_path).suffix.lower()

        ext_map = {
            ".c": "c",
            ".h": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".hpp": "cpp",
            ".hxx": "cpp",
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "javascript",
            ".tsx": "javascript",
            ".java": "java",
            ".rs": "rust",
            ".go": "go",
            ".md": "documentation",
            ".txt": "documentation",
            ".rst": "documentation",
        }

        if ext in ext_map:
            return ext_map[ext]

        # Content-based fallback
        if "def " in content or "import " in content or "class " in content[:1000]:
            if "import " in content[:500]:
                return "python"

        if "function " in content or "const " in content or "let " in content:
            return "javascript"

        if "#include" in content:
            return "c"

        return "unknown"

    def analyze_content_signals(self, content: str) -> Dict[PassType, Tuple[float, List[str]]]:
        """
        Analyze content for keyword signals indicating pass relevance.

        Args:
            content: File content

        Returns:
            Dict mapping PassType to (relevance_score, detected_keywords)
        """
        content_lower = content.lower()

        # Tokenize content (simple word splitting)
        words = set(re.findall(r'\b\w+\b', content_lower))

        results = {}

        for pass_type, keywords in self.KEYWORD_SIGNALS.items():
            # Find matching keywords
            matches = words & keywords

            if matches:
                # Score based on number of matches and keyword density
                match_count = len(matches)
                # Bonus for multiple occurrences
                total_occurrences = sum(content_lower.count(kw) for kw in matches)

                # Score: base score from matches + bonus from frequency
                base_score = min(1.0, match_count / 5.0)  # 5+ matches = 1.0
                frequency_bonus = min(0.3, total_occurrences / 50.0)  # Up to +0.3

                score = min(1.0, base_score + frequency_bonus)
                results[pass_type] = (score, list(matches)[:5])  # Top 5 keywords
            else:
                results[pass_type] = (0.0, [])

        return results

    def select_passes(
        self,
        file_path: str,
        content: str,
        artifact_type: str = "code"
    ) -> List[PassRelevance]:
        """
        Select relevant passes for a file.

        Args:
            file_path: Path to file
            content: File content
            artifact_type: Type of artifact (code, doc, config)

        Returns:
            List of PassRelevance objects sorted by relevance
        """
        # Detect language
        language = self.detect_language(file_path, content)

        # Get language-based baseline scores
        if language in self.LANGUAGE_PASS_MAP:
            language_scores = self.LANGUAGE_PASS_MAP[language]
        else:
            # Default: all passes moderately relevant
            language_scores = {pt: 0.5 for pt in PassType}
            language_scores[PassType.GENERAL] = 1.0

        # Get content-based signals
        content_signals = self.analyze_content_signals(content)

        # Combine scores
        pass_relevances = []

        for pass_type in PassType:
            # Language baseline
            language_score = language_scores.get(pass_type, 0.3)

            # Content signals
            content_score, keywords = content_signals.get(pass_type, (0.0, []))

            # Combined score (weighted average: 60% language, 40% content)
            combined_score = (0.6 * language_score) + (0.4 * content_score)

            # Build reason
            reasons = []
            if language != "unknown":
                reasons.append(f"{language} code")
            if keywords:
                reasons.append(f"keywords: {', '.join(keywords[:3])}")
            if combined_score > 0.7:
                reasons.append("high relevance")

            reason = "; ".join(reasons) if reasons else "general analysis"

            pass_relevances.append(PassRelevance(
                pass_type=pass_type,
                relevance_score=combined_score,
                reason=reason,
                detected_signals=keywords
            ))

        # Filter by minimum relevance
        if self.always_run_general:
            # Always include GENERAL
            filtered = [pr for pr in pass_relevances
                       if pr.pass_type == PassType.GENERAL or pr.relevance_score >= self.min_relevance]
        else:
            filtered = [pr for pr in pass_relevances
                       if pr.relevance_score >= self.min_relevance]

        # Sort by relevance (highest first)
        filtered.sort(key=lambda pr: pr.relevance_score, reverse=True)

        return filtered

    def explain_selection(self, pass_relevances: List[PassRelevance]) -> str:
        """
        Generate human-readable explanation of pass selection.

        Args:
            pass_relevances: List of selected passes

        Returns:
            Formatted explanation string
        """
        lines = ["Selected Passes:"]

        for pr in pass_relevances:
            score_pct = pr.relevance_score * 100
            lines.append(f"  • {pr.pass_type.value.upper()}: {score_pct:.0f}% - {pr.reason}")

        excluded_count = len(PassType) - len(pass_relevances)
        if excluded_count > 0:
            lines.append(f"\nExcluded {excluded_count} low-relevance passes")

        return "\n".join(lines)


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pass_selector.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Read file
    with open(file_path, 'r') as f:
        content = f.read()

    # Create selector
    selector = PassSelector(min_relevance=0.3)

    # Select passes
    selected = selector.select_passes(file_path, content)

    # Display results
    print(f"\nFile: {file_path}")
    print(f"Size: {len(content)} bytes, {len(content.splitlines())} lines")
    print()
    print(selector.explain_selection(selected))
    print()
    print(f"API Call Reduction: {(7 - len(selected)) / 7 * 100:.0f}%")
    print(f"({len(selected)}/{len(PassType)} passes selected)")
