#!/usr/bin/env python3
"""
Smart Pairing Algorithm for Kraang Fact Relationship Analysis

Reduces O(n²) relationship analysis from 9,591 comparisons to ~500
using intelligent filtering heuristics.

Usage:
    python smart_pairing.py [--budget BUDGET] [--threshold THRESHOLD]

Options:
    --budget BUDGET        Maximum number of pairs to analyze (default: 500)
    --threshold THRESHOLD  Minimum score threshold (default: 0)
    --output FILE         Output file for candidate pairs (default: .kraang/candidate_pairs.json)
    --verbose             Show detailed progress
"""

import json
import re
import argparse
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Any

# Domain keywords for categorization
DOMAIN_KEYWORDS = {
    'memory_management': [
        'memory', 'malloc', 'free', 'CREATE', 'DISPOSE', 'allocate',
        'allocation', 'deallocation', 'pointer', 'SET_STRING'
    ],
    'linked_lists': [
        'linked list', 'LINK', 'UNLINK', 'INSERT', 'INSERT_AFTER',
        'head', 'tail', 'next', 'prev', 'node'
    ],
    'communication': [
        'speech', 'talk', 'channel', 'comlink', 'broadcast', 'message',
        'whisper', 'yell', 'emote', 'say', 'language', 'tone'
    ],
    'database': [
        'database', 'PostgreSQL', 'SQL', 'DB_DATA', 'migration',
        'query', 'table', 'db'
    ],
    'docker_dev': [
        'Docker', 'docker-compose', 'container', 'service', 'port',
        'localhost', 'environment'
    ],
    'code_structure': [
        'header', 'function', 'struct', 'types.h', 'functions.h',
        'mud.h', 'const.h', 'globals.h', 'prototype'
    ],
    'game_mechanics': [
        'character', 'player', 'NPC', 'room', 'MUD', 'game',
        'quest', 'skill', 'inventory'
    ],
    'security_auth': [
        'security', 'authentication', 'authorization', 'permission',
        'access', 'credentials', 'password', 'RPC', 'trust'
    ],
    'networking': [
        'telnet', 'port', 'connection', 'socket', 'network',
        'TCP', 'MQTT', 'firehose'
    ],
    'lua_scripting': [
        'Lua', 'loom', 'script', 'callback', 'trigger',
        'mprog', 'oprog', 'rprog'
    ],
    'testing_debug': [
        'test', 'debug', 'GDB', 'Valgrind', 'log', 'backtrace',
        'crash', 'error'
    ],
}


def extract_domains(statement: str) -> Set[str]:
    """Extract all domain categories for a fact statement."""
    statement_lower = statement.lower()
    domains = set()

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in statement_lower:
                domains.add(domain)
                break

    return domains


def extract_code_entities(statement: str) -> Set[str]:
    """Extract function names, struct names, macros, and variables."""
    entities = set()

    # Function names (snake_case with parentheses)
    entities.update(re.findall(r'\b([a-z_][a-z0-9_]*)\(\)', statement.lower()))

    # Macros (ALL_CAPS with at least 3 characters)
    entities.update(re.findall(r'\b([A-Z][A-Z0-9_]{2,})\b', statement))

    # Struct/type names (camelCase or PascalCase)
    entities.update(re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b', statement))

    # Header files
    entities.update(re.findall(r'\b([a-z_]+\.h)\b', statement.lower()))

    return entities


def parse_line_numbers(location: str) -> range:
    """Extract line numbers from location string."""
    match = re.search(r'Lines? (\d+)(?:-(\d+))?', location)
    if match:
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        return range(start, end + 1)
    return None


def get_type_priority(fact1_type: str, fact2_type: str) -> str:
    """Determine priority based on fact type combination."""
    high_priority = {
        ('constraint', 'implementation'),
        ('implementation', 'constraint'),
        ('requirement', 'implementation'),
        ('implementation', 'requirement'),
        ('design', 'implementation'),
        ('implementation', 'design'),
    }

    medium_priority = {
        ('constraint', 'constraint'),
        ('constraint', 'requirement'),
        ('requirement', 'constraint'),
        ('design', 'constraint'),
        ('constraint', 'design'),
        ('design', 'design'),
        ('requirement', 'requirement'),
    }

    pair = (fact1_type, fact2_type)
    if pair in high_priority:
        return 'HIGH'
    elif pair in medium_priority:
        return 'MEDIUM'
    else:
        return 'LOW'


def get_artifact_priority(fact1_artifacts: List[Dict], fact2_artifacts: List[Dict]) -> str:
    """Determine priority based on artifact sources."""
    artifacts1 = set(e['artifact_id'] for e in fact1_artifacts)
    artifacts2 = set(e['artifact_id'] for e in fact2_artifacts)

    # Check if one is from doc and other from code
    has_doc = 'artifact_1' in artifacts1 or 'artifact_1' in artifacts2
    has_code = 'artifact_78' in artifacts1 or 'artifact_78' in artifacts2

    if has_doc and has_code:
        return 'HIGH'  # Cross-artifact: doc ↔ code
    else:
        return 'MEDIUM'  # Same artifact type


def calculate_domain_similarity(fact1: Dict, fact2: Dict) -> float:
    """Calculate Jaccard similarity between fact domains."""
    domains1 = extract_domains(fact1['statement'])
    domains2 = extract_domains(fact2['statement'])

    if not domains1 or not domains2:
        return 0.0

    intersection = len(domains1 & domains2)
    union = len(domains1 | domains2)

    return intersection / union if union > 0 else 0.0


def calculate_entity_overlap(fact1: Dict, fact2: Dict) -> float:
    """Calculate overlap in code entities mentioned."""
    entities1 = extract_code_entities(fact1['statement'])
    entities2 = extract_code_entities(fact2['statement'])

    if not entities1 or not entities2:
        return 0.0

    intersection = len(entities1 & entities2)
    return intersection / min(len(entities1), len(entities2))


def calculate_location_proximity(fact1: Dict, fact2: Dict) -> str:
    """Calculate proximity score for facts from the same artifact."""
    for e1 in fact1['extracted_from']:
        for e2 in fact2['extracted_from']:
            if e1['artifact_id'] == e2['artifact_id']:
                lines1 = parse_line_numbers(e1['location'])
                lines2 = parse_line_numbers(e2['location'])

                if lines1 and lines2:
                    distance = min(abs(l1 - l2) for l1 in lines1 for l2 in lines2)

                    if distance <= 50:
                        return 'HIGH'
                    elif distance <= 200:
                        return 'MEDIUM'

    return 'LOW'


def should_analyze_by_confidence(fact1: Dict, fact2: Dict) -> bool:
    """Filter based on fact confidence scores."""
    if fact1['confidence'] < 0.85 and fact2['confidence'] < 0.85:
        return False
    if fact1['confidence'] < 0.75 or fact2['confidence'] < 0.75:
        return False
    return True


def smart_pairing_algorithm(facts: List[Dict], verbose: bool = False) -> List[Dict]:
    """
    Intelligent fact pairing that reduces O(n²) to practical subset.

    Returns: List of fact pairs prioritized for relationship analysis.
    """
    candidate_pairs = []

    n_facts = len(facts)
    total_pairs = n_facts * (n_facts - 1) // 2

    print(f"Analyzing {n_facts} facts...")
    print(f"Total possible pairs: {total_pairs:,}")

    # Generate all possible pairs with filtering
    for i in range(len(facts)):
        if verbose and i % 20 == 0:
            print(f"  Processing fact {i}/{len(facts)}...")

        for j in range(i + 1, len(facts)):
            fact1, fact2 = facts[i], facts[j]

            # Rule 4: Confidence filter (fastest check)
            if not should_analyze_by_confidence(fact1, fact2):
                continue

            # Rule 1: Type-based priority
            type_priority = get_type_priority(fact1['type'], fact2['type'])

            # Rule 2: Artifact type priority
            artifact_priority = get_artifact_priority(
                fact1['extracted_from'],
                fact2['extracted_from']
            )

            # Rule 3: Domain similarity
            domain_sim = calculate_domain_similarity(fact1, fact2)
            has_domain_overlap = domain_sim > 0.0

            # Rule 6: Entity overlap
            entity_overlap = calculate_entity_overlap(fact1, fact2)
            has_entity_overlap = entity_overlap > 0.0

            # Rule 5: Proximity (for same-artifact pairs)
            proximity = calculate_location_proximity(fact1, fact2)

            # DECISION LOGIC
            score = 0
            reasons = []

            # High priority type pairs (constraint ↔ implementation)
            if type_priority == 'HIGH':
                score += 10
                reasons.append('high_priority_types')

                if has_domain_overlap:
                    score += 5
                    reasons.append('domain_overlap')
                elif has_entity_overlap:
                    score += 3
                    reasons.append('entity_overlap')
                else:
                    continue

            # Cross-artifact pairs (doc ↔ code)
            elif artifact_priority == 'HIGH':
                score += 8
                reasons.append('cross_artifact')

                if has_domain_overlap:
                    score += 5
                    reasons.append('domain_overlap')
                elif has_entity_overlap:
                    score += 3
                    reasons.append('entity_overlap')
                else:
                    continue

            # Same-artifact, medium priority types
            elif type_priority == 'MEDIUM':
                score += 5
                reasons.append('medium_priority_types')

                if has_domain_overlap and has_entity_overlap:
                    score += 5
                    reasons.append('strong_overlap')
                else:
                    continue

            # Low priority type pairs
            else:
                if proximity == 'HIGH' and has_domain_overlap and has_entity_overlap:
                    score += 3
                    reasons.append('low_priority_but_strong_signals')
                else:
                    continue

            # Add bonus for proximity
            if proximity == 'HIGH':
                score += 2
            elif proximity == 'MEDIUM':
                score += 1

            # Store candidate pair with score
            candidate_pairs.append({
                'fact1_id': fact1['id'],
                'fact2_id': fact2['id'],
                'score': score,
                'reasons': reasons,
                'type_priority': type_priority,
                'artifact_priority': artifact_priority,
                'domain_similarity': domain_sim,
                'entity_overlap': entity_overlap,
                'proximity': proximity,
            })

    # Sort by score (highest first)
    candidate_pairs.sort(key=lambda x: x['score'], reverse=True)

    return candidate_pairs


def analyze_results(candidate_pairs: List[Dict], budget_limit: int = 500, threshold: int = 0):
    """Analyze and report on candidate pairs."""
    print(f"\n{'='*60}")
    print(f"SMART PAIRING RESULTS")
    print(f"{'='*60}")

    print(f"\nGenerated {len(candidate_pairs):,} candidate pairs")
    print(f"Reduction: 9,591 → {len(candidate_pairs):,}")
    print(f"Reduction ratio: {len(candidate_pairs) / 9591 * 100:.1f}%")

    # Apply threshold
    if threshold > 0:
        candidate_pairs = [p for p in candidate_pairs if p['score'] >= threshold]
        print(f"After score threshold >= {threshold}: {len(candidate_pairs):,} pairs")

    # Take top N pairs within budget
    pairs_to_analyze = candidate_pairs[:budget_limit]

    print(f"\n{'='*60}")
    print(f"TOP {len(pairs_to_analyze)} PAIRS FOR ANALYSIS:")
    print(f"{'='*60}")
    print(f"  Cost: ${len(pairs_to_analyze) * 0.003:.2f} (vs $28.77 for full analysis)")
    print(f"  Cost savings: ${28.77 - len(pairs_to_analyze) * 0.003:.2f} (95% reduction)")
    print(f"  Time estimate: ~{len(pairs_to_analyze) * 30 / 3600:.1f} hours (vs 80 hours)")

    # Score distribution
    score_dist = defaultdict(int)
    for pair in pairs_to_analyze:
        score_dist[pair['score']] += 1

    print("\nScore distribution:")
    for score in sorted(score_dist.keys(), reverse=True):
        print(f"  Score {score:2d}: {score_dist[score]:3d} pairs")

    # Reason distribution
    reason_dist = defaultdict(int)
    for pair in pairs_to_analyze:
        for reason in pair['reasons']:
            reason_dist[reason] += 1

    print("\nReason distribution:")
    for reason, count in sorted(reason_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"  {reason}: {count} pairs")

    # Type priority distribution
    type_dist = defaultdict(int)
    for pair in pairs_to_analyze:
        type_dist[pair['type_priority']] += 1

    print("\nType priority distribution:")
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        if priority in type_dist:
            print(f"  {priority}: {type_dist[priority]} pairs")

    # Artifact priority distribution
    artifact_dist = defaultdict(int)
    for pair in pairs_to_analyze:
        artifact_dist[pair['artifact_priority']] += 1

    print("\nArtifact priority distribution:")
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        if priority in artifact_dist:
            print(f"  {priority}: {artifact_dist[priority]} pairs")

    return pairs_to_analyze


def show_sample_pairs(pairs: List[Dict], facts_map: Dict[str, Dict], n: int = 5):
    """Show sample high-priority pairs with fact details."""
    print(f"\n{'='*60}")
    print(f"SAMPLE HIGH-PRIORITY PAIRS (Top {n}):")
    print(f"{'='*60}\n")

    for i, pair in enumerate(pairs[:n], 1):
        fact1 = facts_map[pair['fact1_id']]
        fact2 = facts_map[pair['fact2_id']]

        print(f"{i}. {pair['fact1_id']} ↔ {pair['fact2_id']}")
        print(f"   Score: {pair['score']}")
        print(f"   Reasons: {', '.join(pair['reasons'])}")
        print(f"   Type priority: {pair['type_priority']}")
        print(f"   Artifact priority: {pair['artifact_priority']}")
        print(f"\n   Fact 1 ({fact1['type']}):")
        print(f"   {fact1['statement'][:100]}...")
        print(f"\n   Fact 2 ({fact2['type']}):")
        print(f"   {fact2['statement'][:100]}...")
        print()


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Smart Pairing Algorithm for Kraang Fact Relationship Analysis'
    )
    parser.add_argument(
        '--budget',
        type=int,
        default=500,
        help='Maximum number of pairs to analyze (default: 500)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=0,
        help='Minimum score threshold (default: 0)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='.kraang/candidate_pairs.json',
        help='Output file for candidate pairs (default: .kraang/candidate_pairs.json)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    args = parser.parse_args()

    # Load facts
    try:
        with open('.kraang/facts.json') as f:
            facts = json.load(f)
    except FileNotFoundError:
        print("Error: .kraang/facts.json not found")
        print("Please run Kraang fact extraction first")
        return 1

    print(f"Loaded {len(facts)} facts from .kraang/facts.json")

    # Create facts map for lookups
    facts_map = {f['id']: f for f in facts}

    # Run smart pairing algorithm
    candidate_pairs = smart_pairing_algorithm(facts, verbose=args.verbose)

    # Analyze results
    top_pairs = analyze_results(
        candidate_pairs,
        budget_limit=args.budget,
        threshold=args.threshold
    )

    # Save results
    with open(args.output, 'w') as f:
        json.dump(top_pairs, f, indent=2)

    print(f"\nSaved {len(top_pairs)} pairs to {args.output}")

    # Show sample high-priority pairs
    show_sample_pairs(top_pairs, facts_map, n=5)

    print(f"\n{'='*60}")
    print("NEXT STEPS:")
    print(f"{'='*60}")
    print("\n1. Review the candidate pairs in the output file")
    print("2. Adjust --budget or --threshold if needed")
    print("3. Use these pairs for relationship analysis with your LLM")
    print("4. Monitor relationship density: aim for 0.5+ (each fact has ~1 relationship)")
    print("\nTo analyze a different budget:")
    print(f"  python smart_pairing.py --budget 300")
    print("\nTo apply a minimum score threshold:")
    print(f"  python smart_pairing.py --budget 500 --threshold 10")
    print()

    return 0


class SmartPairingAlgorithm:
    """
    Object-oriented interface for smart pairing algorithm.

    Usage as a module:
        from smart_pairing import SmartPairingAlgorithm

        algorithm = SmartPairingAlgorithm(facts)
        pairs = algorithm.generate_pairs(budget=500, threshold=10)
        stats = algorithm.get_statistics()
    """

    def __init__(self, facts: List[Dict]):
        """Initialize with a list of facts."""
        self.facts = facts
        self.facts_map = {f['id']: f for f in facts}
        self.candidate_pairs = None
        self.total_possible_pairs = len(facts) * (len(facts) - 1) // 2

    def generate_pairs(self, budget: int = 500, threshold: int = 0, verbose: bool = False) -> List[Dict]:
        """
        Generate candidate pairs using smart pairing algorithm.

        Args:
            budget: Maximum number of pairs to return
            threshold: Minimum score threshold
            verbose: Show progress during generation

        Returns:
            List of candidate pairs sorted by score
        """
        self.candidate_pairs = smart_pairing_algorithm(self.facts, verbose=verbose)

        # Apply threshold
        if threshold > 0:
            self.candidate_pairs = [p for p in self.candidate_pairs if p['score'] >= threshold]

        # Apply budget
        return self.candidate_pairs[:budget]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the pairing results.

        Returns:
            Dictionary with statistics
        """
        if self.candidate_pairs is None:
            return {'error': 'No pairs generated yet. Call generate_pairs() first.'}

        pairs = self.candidate_pairs

        # Score distribution
        score_dist = defaultdict(int)
        for pair in pairs:
            score_dist[pair['score']] += 1

        # Reason distribution
        reason_dist = defaultdict(int)
        for pair in pairs:
            for reason in pair['reasons']:
                reason_dist[reason] += 1

        # Type priority distribution
        type_dist = defaultdict(int)
        for pair in pairs:
            type_dist[pair['type_priority']] += 1

        # Artifact priority distribution
        artifact_dist = defaultdict(int)
        for pair in pairs:
            artifact_dist[pair['artifact_priority']] += 1

        return {
            'total_facts': len(self.facts),
            'total_possible_pairs': self.total_possible_pairs,
            'candidate_pairs': len(pairs),
            'reduction_ratio': len(pairs) / self.total_possible_pairs if self.total_possible_pairs > 0 else 0,
            'score_distribution': dict(score_dist),
            'reason_distribution': dict(reason_dist),
            'type_priority_distribution': dict(type_dist),
            'artifact_priority_distribution': dict(artifact_dist),
            'score_range': {
                'min': min((p['score'] for p in pairs), default=0),
                'max': max((p['score'] for p in pairs), default=0),
            }
        }

    def get_pair_details(self, fact1_id: str, fact2_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific pair.

        Args:
            fact1_id: ID of first fact
            fact2_id: ID of second fact

        Returns:
            Dictionary with pair details including facts
        """
        if self.candidate_pairs is None:
            return {'error': 'No pairs generated yet. Call generate_pairs() first.'}

        # Find the pair
        for pair in self.candidate_pairs:
            if (pair['fact1_id'] == fact1_id and pair['fact2_id'] == fact2_id) or \
               (pair['fact1_id'] == fact2_id and pair['fact2_id'] == fact1_id):
                return {
                    'pair': pair,
                    'fact1': self.facts_map.get(pair['fact1_id']),
                    'fact2': self.facts_map.get(pair['fact2_id']),
                }

        return {'error': f'Pair not found: {fact1_id} ↔ {fact2_id}'}


if __name__ == '__main__':
    exit(main())
