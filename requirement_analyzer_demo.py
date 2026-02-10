#!/usr/bin/env python3
"""
Requirement Analyzer Demo - Demonstrates analysis without API calls

This demo version shows how the requirement analyzer works by using
pre-computed analysis results based on actual LotJ constraints.
"""

import json
import sys
from pathlib import Path
from requirement_analyzer import (
    RequirementFact, Conflict, Dependency, ImpactArea, FeasibilityReport,
    ConflictSeverity, print_report
)
from kraang import KraangStore, Fact


def analyze_new_header_files(store: KraangStore) -> FeasibilityReport:
    """Scenario 1: Add ability to create new header files"""

    requirement = "Add ability to create new header files for better code organization and modularity"

    # Extract facts from requirement
    req_facts = [
        RequirementFact(
            statement="System should allow developers to create new header files",
            type="requirement",
            confidence=1.0
        ),
        RequirementFact(
            statement="Code organization would benefit from additional header files",
            type="design",
            confidence=0.9
        ),
        RequirementFact(
            statement="Modular design requires flexible header file structure",
            type="design",
            confidence=0.8
        ),
        RequirementFact(
            statement="Developers need ability to organize code into new headers",
            type="capability",
            confidence=0.95
        )
    ]

    # Find the actual facts from LotJ
    all_facts = store.get_facts()

    # Find the critical constraint
    no_new_headers = None
    for fact in all_facts:
        if "DO NOT create new header files" in fact.statement:
            no_new_headers = fact
            break

    # Create conflicts
    conflicts = []
    if no_new_headers:
        conflicts.append(Conflict(
            requirement_fact=req_facts[0],
            existing_fact=no_new_headers,
            severity=ConflictSeverity.CRITICAL,
            reasoning="Direct contradiction: Requirement wants to create new headers, but existing constraint explicitly forbids it",
            confidence=1.0
        ))

    # Find related facts about header organization
    types_h_fact = None
    functions_h_fact = None
    for fact in all_facts:
        if "struct definitions MUST be placed in types.h" in fact.statement:
            types_h_fact = fact
        elif "function declarations MUST be placed in functions.h" in fact.statement:
            functions_h_fact = fact

    if types_h_fact:
        conflicts.append(Conflict(
            requirement_fact=req_facts[1],
            existing_fact=types_h_fact,
            severity=ConflictSeverity.HIGH,
            reasoning="New headers would conflict with established pattern of centralizing structs in types.h",
            confidence=0.9
        ))

    if functions_h_fact:
        conflicts.append(Conflict(
            requirement_fact=req_facts[3],
            existing_fact=functions_h_fact,
            severity=ConflictSeverity.HIGH,
            reasoning="New headers would conflict with established pattern of centralizing functions in functions.h",
            confidence=0.9
        ))

    # Dependencies
    dependencies = []

    # Impact areas
    impact_areas = []
    if no_new_headers and no_new_headers.extracted_from:
        ref = no_new_headers.extracted_from[0]
        artifact = store.get_artifact(ref['artifact_id'])
        if artifact:
            impact_areas.append(ImpactArea(
                artifact_id=ref['artifact_id'],
                artifact_path=artifact.path,
                location=ref['location'],
                change_type="remove_or_modify",
                description="Would need to remove or significantly modify the 'no new headers' constraint"
            ))

    # Would need to update build system
    impact_areas.append(ImpactArea(
        artifact_id="hypothetical_makefile",
        artifact_path="Makefile",
        location="Header dependencies",
        change_type="modify",
        description="Build system would need to track additional header dependencies"
    ))

    # Would need to update documentation
    impact_areas.append(ImpactArea(
        artifact_id="hypothetical_docs",
        artifact_path="docs/CODING_STANDARDS.md",
        location="Header file guidelines",
        change_type="modify",
        description="Documentation would need complete rewrite of header organization guidelines"
    ))

    feasibility_score = 0.15  # Very low due to critical conflict
    assessment = "VERY LOW - Critical constraint violation makes this infeasible without major policy change"

    recommendations = [
        "CRITICAL: This requirement directly violates a documented architectural constraint",
        "The existing constraint exists for good reasons: maintainability, consistency, avoiding header proliferation",
        "Alternative: Work within existing header structure (types.h, functions.h)",
        "Alternative: Use better code organization within .c files rather than splitting headers",
        "Alternative: If truly necessary, first get architectural approval to change the constraint",
        "Impact: Would require policy change + documentation rewrite + build system updates",
        "Recommendation: REJECT this requirement and work within existing header structure"
    ]

    return FeasibilityReport(
        requirement=requirement,
        extracted_facts=req_facts,
        conflicts=conflicts,
        dependencies=dependencies,
        impact_areas=impact_areas,
        feasibility_score=feasibility_score,
        overall_assessment=assessment,
        recommendations=recommendations
    )


def analyze_malloc_requirement(store: KraangStore) -> FeasibilityReport:
    """Scenario 2: Allow malloc() in new memory subsystem"""

    requirement = "Allow malloc() in new memory subsystem for performance optimization and compatibility with external libraries"

    req_facts = [
        RequirementFact(
            statement="New memory subsystem should be allowed to use malloc() directly",
            type="requirement",
            confidence=1.0
        ),
        RequirementFact(
            statement="malloc() provides performance benefits over CREATE macro",
            type="design",
            confidence=0.7
        ),
        RequirementFact(
            statement="External library integration requires malloc() compatibility",
            type="constraint",
            confidence=0.85
        ),
        RequirementFact(
            statement="Custom memory subsystem needs low-level memory control",
            type="implementation",
            confidence=0.9
        )
    ]

    all_facts = store.get_facts()

    # Find memory management constraints
    no_malloc = None
    must_use_create = None
    must_use_dispose = None

    for fact in all_facts:
        if "Never use raw malloc" in fact.statement or "never use raw malloc" in fact.statement:
            no_malloc = fact
        elif "CREATE" in fact.statement and "MUST be used to allocate" in fact.statement:
            must_use_create = fact
        elif "DISPOSE" in fact.statement and "MUST be used to free" in fact.statement:
            must_use_dispose = fact

    conflicts = []

    if no_malloc:
        conflicts.append(Conflict(
            requirement_fact=req_facts[0],
            existing_fact=no_malloc,
            severity=ConflictSeverity.CRITICAL,
            reasoning="Direct violation of core memory management policy forbidding raw malloc()",
            confidence=1.0
        ))

    if must_use_create:
        conflicts.append(Conflict(
            requirement_fact=req_facts[0],
            existing_fact=must_use_create,
            severity=ConflictSeverity.HIGH,
            reasoning="Bypasses mandatory CREATE macro, breaking memory tracking and debugging",
            confidence=0.95
        ))

    if must_use_dispose:
        conflicts.append(Conflict(
            requirement_fact=req_facts[0],
            existing_fact=must_use_dispose,
            severity=ConflictSeverity.HIGH,
            reasoning="malloc() without DISPOSE breaks memory cleanup patterns and NULL-setting guarantees",
            confidence=0.9
        ))

    dependencies = []

    # Would need to modify memory tracking
    impact_areas = []
    if no_malloc and no_malloc.extracted_from:
        ref = no_malloc.extracted_from[0]
        artifact = store.get_artifact(ref['artifact_id'])
        if artifact:
            impact_areas.append(ImpactArea(
                artifact_id=ref['artifact_id'],
                artifact_path=artifact.path,
                location=ref['location'],
                change_type="modify",
                description="Memory management documentation would need exception clause"
            ))

    impact_areas.extend([
        ImpactArea(
            artifact_id="hypothetical_mud_h",
            artifact_path="src/mud.h",
            location="Memory macros",
            change_type="modify",
            description="Would need new macros or wrappers for malloc-based code"
        ),
        ImpactArea(
            artifact_id="hypothetical_memory_c",
            artifact_path="src/memory.c",
            location="Entire file",
            change_type="modify",
            description="Memory tracking system would need updates to handle raw malloc"
        ),
        ImpactArea(
            artifact_id="hypothetical_debug",
            artifact_path="src/debug.c",
            location="Memory debugging",
            change_type="modify",
            description="Memory leak detection would not work for malloc-allocated memory"
        )
    ])

    feasibility_score = 0.25
    assessment = "VERY LOW - Core architectural constraint violation with widespread impact"

    recommendations = [
        "CRITICAL: This violates fundamental memory management architecture",
        "The CREATE/DISPOSE system exists for: memory tracking, leak detection, NULL-safety, debugging",
        "Using raw malloc() bypasses all these protections",
        "Alternative: Extend CREATE macro to support performance optimizations",
        "Alternative: Create MALLOC_EXTERNAL/FREE_EXTERNAL for library integration only",
        "Alternative: Wrap external library calls to use CREATE internally",
        "If approved: Require strict isolation - only in dedicated subsystem",
        "If approved: Must maintain memory tracking for malloc'd memory",
        "Recommendation: REJECT unless absolutely critical, then isolate heavily"
    ]

    return FeasibilityReport(
        requirement=requirement,
        extracted_facts=req_facts,
        conflicts=conflicts,
        dependencies=dependencies,
        impact_areas=impact_areas,
        feasibility_score=feasibility_score,
        overall_assessment=assessment,
        recommendations=recommendations
    )


def analyze_non_docker_dev(store: KraangStore) -> FeasibilityReport:
    """Scenario 3: Support non-Docker local development"""

    requirement = "Support non-Docker local development for developers who prefer native tooling and faster iteration cycles"

    req_facts = [
        RequirementFact(
            statement="Developers should be able to build and run without Docker",
            type="requirement",
            confidence=1.0
        ),
        RequirementFact(
            statement="Native builds provide faster compilation and debugging",
            type="design",
            confidence=0.8
        ),
        RequirementFact(
            statement="Some developers prefer native IDE integration over containers",
            type="requirement",
            confidence=0.75
        ),
        RequirementFact(
            statement="Would require documenting native dependency installation",
            type="implementation",
            confidence=0.95
        ),
        RequirementFact(
            statement="Build system needs to work both in Docker and natively",
            type="constraint",
            confidence=0.9
        )
    ]

    all_facts = store.get_facts()

    # Find Docker constraints
    docker_required = None
    docker_exclusive = None

    for fact in all_facts:
        if "Docker Compose exclusively" in fact.statement or "MUST use Docker" in fact.statement:
            docker_exclusive = fact
        elif "docker-compose down MUST be avoided" in fact.statement:
            docker_required = fact

    conflicts = []

    if docker_exclusive:
        conflicts.append(Conflict(
            requirement_fact=req_facts[0],
            existing_fact=docker_exclusive,
            severity=ConflictSeverity.HIGH,
            reasoning="Contradicts Docker-exclusive policy, though less severe than other constraints as this is process policy not code architecture",
            confidence=0.85
        ))

    dependencies = []

    # Actually depends on maintaining Docker as the primary method
    if docker_exclusive:
        dependencies.append(Dependency(
            requirement_fact=req_facts[4],
            existing_fact=docker_exclusive,
            dependency_type="extends",
            reasoning="Would extend the build system to support both Docker and native, keeping Docker as primary supported method"
        ))

    impact_areas = []
    if docker_exclusive and docker_exclusive.extracted_from:
        ref = docker_exclusive.extracted_from[0]
        artifact = store.get_artifact(ref['artifact_id'])
        if artifact:
            impact_areas.append(ImpactArea(
                artifact_id=ref['artifact_id'],
                artifact_path=artifact.path,
                location=ref['location'],
                change_type="modify",
                description="Documentation would need to add native development as optional alternative"
            ))

    impact_areas.extend([
        ImpactArea(
            artifact_id="hypothetical_readme",
            artifact_path="README.md",
            location="Setup instructions",
            change_type="add",
            description="Would need comprehensive native setup documentation"
        ),
        ImpactArea(
            artifact_id="hypothetical_makefile",
            artifact_path="Makefile",
            location="Build targets",
            change_type="modify",
            description="Build system would need native-friendly targets"
        ),
        ImpactArea(
            artifact_id="hypothetical_ci",
            artifact_path=".github/workflows/ci.yml",
            location="Test matrix",
            change_type="add",
            description="CI would need to test both Docker and native builds"
        )
    ])

    feasibility_score = 0.60
    assessment = "MODERATE - Feasible as optional alternative but requires significant documentation and testing effort"

    recommendations = [
        "This is more feasible than other scenarios - Docker policy is about process not architecture",
        "Keep Docker as PRIMARY and SUPPORTED method",
        "Native development can be OPTIONAL and COMMUNITY-SUPPORTED",
        "Document native dependencies clearly (databases, libraries, versions)",
        "Add Makefile targets for native builds",
        "Clearly state: 'Native development is unsupported - use at your own risk'",
        "Keep Docker-compose as the official development workflow",
        "Support matrix: Docker (primary), native (community/optional)",
        "This won't break existing code, just adds an optional path",
        "Recommendation: APPROVE as optional/unsupported path with clear documentation"
    ]

    return FeasibilityReport(
        requirement=requirement,
        extracted_facts=req_facts,
        conflicts=conflicts,
        dependencies=dependencies,
        impact_areas=impact_areas,
        feasibility_score=feasibility_score,
        overall_assessment=assessment,
        recommendations=recommendations
    )


def main():
    """Run demo scenarios"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Demo: Analyze proposed requirements against LotJ constraints"
    )
    parser.add_argument(
        'scenario',
        choices=['1', '2', '3', 'all'],
        help='Scenario to run: 1=new headers, 2=malloc, 3=non-docker, all=run all'
    )
    parser.add_argument(
        '--output', '-o',
        help='Save report to JSON file (only for single scenario)'
    )

    args = parser.parse_args()

    store = KraangStore()

    scenarios = {
        '1': ('New Header Files', analyze_new_header_files),
        '2': ('Allow malloc()', analyze_malloc_requirement),
        '3': ('Non-Docker Development', analyze_non_docker_dev)
    }

    if args.scenario == 'all':
        for num, (name, func) in scenarios.items():
            print(f"\n{'='*80}")
            print(f"SCENARIO {num}: {name}")
            print(f"{'='*80}\n")
            report = func(store)
            print_report(report)
            print("\n" * 2)
    else:
        name, func = scenarios[args.scenario]
        print(f"\nSCENARIO {args.scenario}: {name}\n")
        report = func(store)
        print_report(report)

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)
            print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
