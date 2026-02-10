#!/usr/bin/env python3
"""
Coverage analyzer for Kraang - measures which parts of codebase are referenced by facts.
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
from enum import Enum


class CoverageLevel(Enum):
    """Coverage level categories"""
    NONE = "none"           # 0-10%
    LOW = "low"             # 10-30%
    MODERATE = "moderate"   # 30-60%
    GOOD = "good"           # 60-80%
    EXCELLENT = "excellent" # 80-100%


@dataclass
class FileCoverage:
    """Coverage information for a single artifact"""
    artifact_id: str
    artifact_type: str
    path: str
    total_lines: int
    covered_lines: Set[int]
    facts_by_line: Dict[int, List[str]]
    total_facts: int

    def coverage_percentage(self) -> float:
        """Calculate percentage of lines covered"""
        if self.total_lines == 0:
            return 0.0
        return (len(self.covered_lines) / self.total_lines) * 100

    def density(self) -> float:
        """Calculate average facts per covered line"""
        if not self.covered_lines:
            return 0.0
        total_fact_refs = sum(len(fids) for fids in self.facts_by_line.values())
        return total_fact_refs / len(self.covered_lines)

    def coverage_level(self) -> CoverageLevel:
        """Categorize coverage level"""
        pct = self.coverage_percentage()
        if pct >= 80:
            return CoverageLevel.EXCELLENT
        elif pct >= 60:
            return CoverageLevel.GOOD
        elif pct >= 30:
            return CoverageLevel.MODERATE
        elif pct >= 10:
            return CoverageLevel.LOW
        else:
            return CoverageLevel.NONE

    def is_below_target(self, target: float) -> bool:
        """Check if coverage is below target percentage"""
        return self.coverage_percentage() < target


@dataclass
class CoverageReport:
    """Overall coverage report"""
    file_coverages: List[FileCoverage]
    total_lines: int
    total_covered_lines: int
    total_facts: int

    def overall_percentage(self) -> float:
        """Calculate overall coverage percentage"""
        if self.total_lines == 0:
            return 0.0
        return (self.total_covered_lines / self.total_lines) * 100

    def by_type(self, artifact_type: str) -> List[FileCoverage]:
        """Get coverage for specific artifact type"""
        return [fc for fc in self.file_coverages if fc.artifact_type == artifact_type]

    def uncovered_files(self) -> List[FileCoverage]:
        """Get files with 0% coverage"""
        return [fc for fc in self.file_coverages if fc.coverage_percentage() == 0]

    def low_coverage_files(self, threshold: float = 20.0) -> List[FileCoverage]:
        """Get files below coverage threshold"""
        return [fc for fc in self.file_coverages
                if 0 < fc.coverage_percentage() < threshold]


class LocationParser:
    """Parses fact locations to extract line numbers"""

    # Patterns for different location formats
    LINE_RANGE_PATTERN = re.compile(r'Lines? (\d+)-(\d+)')
    SINGLE_LINE_PATTERN = re.compile(r'Line (\d+)(?:\D|$)')

    def parse_location(self, location: str) -> Set[int]:
        """
        Parse location string and return set of line numbers.

        Supported formats:
        - "Lines 100-120" -> {100, 101, ..., 120}
        - "Line 50" -> {50}
        - "Lines 100-120, Section: Foo" -> {100, 101, ..., 120}

        Unsupported (returns empty set):
        - "function do_command"
        - "Section: Architecture"
        """
        lines = set()

        # Try line range pattern first (more specific)
        match = self.LINE_RANGE_PATTERN.search(location)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            return set(range(start, end + 1))

        # Try single line pattern
        match = self.SINGLE_LINE_PATTERN.search(location)
        if match:
            line_num = int(match.group(1))
            return {line_num}

        # No line numbers found
        return set()


class CoverageAnalyzer:
    """Analyzes coverage of facts across artifacts"""

    # Default coverage targets by file type
    TARGETS = {
        'doc': 70.0,      # Documentation should be well-covered
        'code': 40.0,     # Code needs selective coverage
        'config': 80.0,   # Config should be comprehensive
        'requirement': 90.0,  # Requirements must be thorough
    }

    def __init__(self, store):
        """Initialize with a KraangStore"""
        self.store = store
        self.parser = LocationParser()

    def analyze_artifact(self, artifact) -> FileCoverage:
        """Analyze coverage for a single artifact"""

        # Count total lines in artifact
        total_lines = 0
        if artifact.content:
            total_lines = artifact.content.count('\n') + 1

        # Find all facts referencing this artifact
        all_facts = self.store.get_facts()
        relevant_facts = []
        for fact in all_facts:
            for ref in fact.extracted_from:
                if ref['artifact_id'] == artifact.id:
                    relevant_facts.append(fact)
                    break

        # Parse locations to get covered lines
        covered_lines = set()
        facts_by_line = defaultdict(list)

        for fact in relevant_facts:
            for ref in fact.extracted_from:
                if ref['artifact_id'] == artifact.id:
                    lines = self.parser.parse_location(ref['location'])
                    covered_lines.update(lines)
                    for line in lines:
                        facts_by_line[line].append(fact.id)

        return FileCoverage(
            artifact_id=artifact.id,
            artifact_type=artifact.type,
            path=artifact.path,
            total_lines=total_lines,
            covered_lines=covered_lines,
            facts_by_line=dict(facts_by_line),
            total_facts=len(relevant_facts)
        )

    def analyze_all(self) -> CoverageReport:
        """Analyze coverage for all artifacts"""
        artifacts = self.store.get_artifacts()
        file_coverages = [self.analyze_artifact(a) for a in artifacts]

        total_lines = sum(fc.total_lines for fc in file_coverages)
        total_covered = sum(len(fc.covered_lines) for fc in file_coverages)
        total_facts = self.store.get_facts()

        return CoverageReport(
            file_coverages=file_coverages,
            total_lines=total_lines,
            total_covered_lines=total_covered,
            total_facts=len(total_facts)
        )

    def generate_heatmap(self, coverage: FileCoverage, bucket_size: int = 50) -> str:
        """
        Generate ASCII heat map visualization.

        Groups lines into buckets and shows coverage density.
        """
        output = []
        output.append(f"Coverage Heat Map: {coverage.path}")
        output.append(f"Lines: 1-{coverage.total_lines} | Coverage: {coverage.coverage_percentage():.1f}%")
        output.append("")
        output.append("Legend: [  ] 0-20% | [░░] 20-40% | [▒▒] 40-60% | [▓▓] 60-80% | [██] 80-100%")
        output.append("")

        # Group lines into buckets
        num_buckets = (coverage.total_lines + bucket_size - 1) // bucket_size

        for i in range(num_buckets):
            start_line = i * bucket_size + 1
            end_line = min((i + 1) * bucket_size, coverage.total_lines)

            # Count covered lines in this bucket
            bucket_covered = sum(1 for line in range(start_line, end_line + 1)
                               if line in coverage.covered_lines)
            bucket_total = end_line - start_line + 1

            # Calculate percentage for this bucket
            bucket_pct = (bucket_covered / bucket_total) * 100 if bucket_total > 0 else 0

            # Choose visualization symbol
            if bucket_pct >= 80:
                symbol = "██"
            elif bucket_pct >= 60:
                symbol = "▓▓"
            elif bucket_pct >= 40:
                symbol = "▒▒"
            elif bucket_pct >= 20:
                symbol = "░░"
            else:
                symbol = "  "

            # Count facts in this bucket
            bucket_facts = set()
            for line in range(start_line, end_line + 1):
                if line in coverage.facts_by_line:
                    bucket_facts.update(coverage.facts_by_line[line])

            # Format line range
            line_range = f"{start_line:5d}-{end_line:5d}"

            if bucket_facts:
                output.append(f"  {line_range}: [{symbol}] {len(bucket_facts)} facts")
            else:
                output.append(f"  {line_range}: [{symbol}] no facts")

        return "\n".join(output)

    def get_target(self, artifact_type: str) -> float:
        """Get coverage target for artifact type"""
        return self.TARGETS.get(artifact_type, 50.0)

    def print_summary(self, report: CoverageReport):
        """Print comprehensive coverage summary"""
        print("=" * 70)
        print("CODE COVERAGE ANALYSIS")
        print("=" * 70)
        print()

        # Overall statistics
        print("OVERALL STATISTICS")
        print("-" * 70)
        print(f"Total Artifacts:     {len(report.file_coverages)}")
        print(f"Total Lines:         {report.total_lines:,}")
        print(f"Covered Lines:       {report.total_covered_lines:,}")
        print(f"Overall Coverage:    {report.overall_percentage():.1f}%")
        print(f"Total Facts:         {report.total_facts}")
        print()

        # Coverage by type
        print("COVERAGE BY ARTIFACT TYPE")
        print("-" * 70)

        type_stats = defaultdict(lambda: {'lines': 0, 'covered': 0, 'files': 0})
        for fc in report.file_coverages:
            type_stats[fc.artifact_type]['lines'] += fc.total_lines
            type_stats[fc.artifact_type]['covered'] += len(fc.covered_lines)
            type_stats[fc.artifact_type]['files'] += 1

        for artifact_type in sorted(type_stats.keys()):
            stats = type_stats[artifact_type]
            pct = (stats['covered'] / stats['lines'] * 100) if stats['lines'] > 0 else 0
            target = self.get_target(artifact_type)

            status = "✓" if pct >= target else "⚠"
            print(f"{artifact_type:15s} {pct:6.1f}% {status}  "
                  f"(target: {target:.0f}%, files: {stats['files']})")
        print()

        # Top covered files
        print("TOP 5 COVERED FILES")
        print("-" * 70)
        sorted_by_coverage = sorted(report.file_coverages,
                                   key=lambda x: x.coverage_percentage(),
                                   reverse=True)
        for i, fc in enumerate(sorted_by_coverage[:5], 1):
            pct = fc.coverage_percentage()
            print(f"{i}. {Path(fc.path).name:30s} {pct:6.1f}% "
                  f"({len(fc.covered_lines):,}/{fc.total_lines:,} lines, "
                  f"{fc.total_facts} facts)")
        print()

        # Files needing attention
        low_coverage = [fc for fc in report.file_coverages
                       if fc.is_below_target(self.get_target(fc.artifact_type))]

        if low_coverage:
            print("FILES NEEDING ATTENTION")
            print("-" * 70)
            sorted_by_coverage = sorted(low_coverage,
                                      key=lambda x: x.coverage_percentage())
            for i, fc in enumerate(sorted_by_coverage[:5], 1):
                pct = fc.coverage_percentage()
                target = self.get_target(fc.artifact_type)
                gap = target - pct

                if pct == 0:
                    urgency = "⚠⚠⚠"
                elif gap > 40:
                    urgency = "⚠⚠"
                else:
                    urgency = "⚠"

                print(f"{i}. {Path(fc.path).name:30s} {pct:6.1f}% {urgency} "
                      f"(target: {target:.0f}%, gap: {gap:.0f}%)")
            print()

        # Critical gaps
        print("CRITICAL GAPS")
        print("-" * 70)
        uncovered = report.uncovered_files()
        print(f"• {len(uncovered)} files with 0% coverage")

        low = report.low_coverage_files(20.0)
        print(f"• {len(low)} files with <20% coverage")

        # Calculate unparseable locations
        all_facts = self.store.get_facts()
        total_refs = sum(len(f.extracted_from) for f in all_facts)
        parseable_refs = 0
        for fact in all_facts:
            for ref in fact.extracted_from:
                if self.parser.parse_location(ref['location']):
                    parseable_refs += 1

        unparseable = total_refs - parseable_refs
        unparseable_pct = (unparseable / total_refs * 100) if total_refs > 0 else 0
        print(f"• {unparseable}/{total_refs} fact references with unparseable locations "
              f"({unparseable_pct:.0f}%)")
        print()

        # Recommendations
        print("RECOMMENDATIONS")
        print("-" * 70)

        if uncovered:
            print(f"• Extract facts from {len(uncovered)} uncovered files")
        if low:
            print(f"• Increase coverage on {len(low)} low-coverage files")
        if unparseable_pct > 30:
            print(f"• Many locations lack line numbers - consider more specific references")

        if report.overall_percentage() >= 60:
            print("• Coverage is good - focus on quality and relationships")
        elif report.overall_percentage() >= 40:
            print("• Coverage is moderate - extract from critical gaps")
        else:
            print("• Coverage is low - more extraction work needed")

        print()

    def print_artifact_detail(self, artifact_id: str):
        """Print detailed coverage for specific artifact"""
        artifact = self.store.get_artifact(artifact_id)
        if not artifact:
            print(f"✗ Artifact not found: {artifact_id}")
            return

        coverage = self.analyze_artifact(artifact)

        print("=" * 70)
        print(f"COVERAGE DETAIL: {artifact.id}")
        print("=" * 70)
        print(f"Path: {coverage.path}")
        print(f"Type: {coverage.artifact_type}")
        print(f"Total Lines: {coverage.total_lines:,}")
        print(f"Covered Lines: {len(coverage.covered_lines):,}")
        print(f"Coverage: {coverage.coverage_percentage():.1f}%")
        print(f"Facts: {coverage.total_facts}")
        print(f"Density: {coverage.density():.2f} facts/covered-line")
        print()

        target = self.get_target(coverage.artifact_type)
        print(f"Target: {target:.0f}%")
        if coverage.coverage_percentage() >= target:
            print("Status: ✓ Meets target")
        else:
            gap = target - coverage.coverage_percentage()
            print(f"Status: ⚠ Below target by {gap:.0f}%")
        print()

        # Show facts
        print("EXTRACTED FACTS")
        print("-" * 70)
        all_facts = self.store.get_facts()
        relevant_facts = [f for f in all_facts
                         if any(ref['artifact_id'] == artifact.id
                               for ref in f.extracted_from)]

        for fact in relevant_facts[:10]:  # Show first 10
            # Find location for this artifact
            locations = [ref['location'] for ref in fact.extracted_from
                        if ref['artifact_id'] == artifact.id]
            print(f"• {fact.id}: {fact.statement[:60]}...")
            if locations:
                print(f"  Location: {locations[0]}")

        if len(relevant_facts) > 10:
            print(f"  ... and {len(relevant_facts) - 10} more facts")
        print()

    def print_gaps(self, report: CoverageReport):
        """Print detailed gap analysis"""
        print("=" * 70)
        print("COVERAGE GAPS ANALYSIS")
        print("=" * 70)
        print()

        # Uncovered files
        uncovered = report.uncovered_files()
        if uncovered:
            print("UNCOVERED FILES (0% coverage)")
            print("-" * 70)
            for fc in sorted(uncovered, key=lambda x: x.total_lines, reverse=True):
                print(f"• {fc.path}")
                print(f"  {fc.total_lines:,} lines, type: {fc.artifact_type}")
            print()

        # Low coverage files
        low = report.low_coverage_files(20.0)
        if low:
            print("LOW COVERAGE FILES (<20%)")
            print("-" * 70)
            for fc in sorted(low, key=lambda x: x.coverage_percentage()):
                pct = fc.coverage_percentage()
                print(f"• {fc.path} - {pct:.1f}%")
                print(f"  {len(fc.covered_lines):,}/{fc.total_lines:,} lines, "
                      f"{fc.total_facts} facts")
            print()

        # Files below target
        below_target = [fc for fc in report.file_coverages
                       if fc.is_below_target(self.get_target(fc.artifact_type))
                       and fc.coverage_percentage() >= 20]
        if below_target:
            print("FILES BELOW TARGET (>20% but under target)")
            print("-" * 70)
            for fc in sorted(below_target, key=lambda x: x.coverage_percentage()):
                pct = fc.coverage_percentage()
                target = self.get_target(fc.artifact_type)
                gap = target - pct
                print(f"• {fc.path} - {pct:.1f}% (target: {target:.0f}%, gap: {gap:.0f}%)")
            print()
