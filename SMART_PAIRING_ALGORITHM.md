# Smart Pairing Algorithm for Relationship Analysis

## Problem Summary

**Current State:**
- 139 facts extracted from 2 artifacts
- Full relationship analysis = C(139, 2) = 9,591 comparisons
- At $0.003/call = $28.77 and ~5 hours
- Only 3 relationships analyzed manually so far

**Goal:** Reduce comparisons from 9,591 to <500 while maintaining high relationship discovery quality.

## Algorithm Design

### Core Insight

Not all fact pairs are equally likely to have relationships. We can use multiple filtering heuristics to identify the most promising candidate pairs before sending them to the LLM for analysis.

### Fact Distribution Analysis

From the codebase:
- **Constraints:** 40 facts (29%)
- **Implementation:** 88 facts (63%)
- **Requirements:** 8 facts (6%)
- **Design:** 3 facts (2%)

**Artifacts:**
- artifact_1: 76 facts (documentation)
- artifact_78: 63 facts (code)

---

## Filtering Rules & Heuristics

### Rule 1: Type-Based Pairing Priority

**Principle:** Certain fact type combinations are more likely to have relationships than others.

**Priority Matrix:**

| Type 1         | Type 2         | Priority | Reason                                           |
|----------------|----------------|----------|--------------------------------------------------|
| constraint     | implementation | HIGH     | Constraints should be implemented in code        |
| constraint     | constraint     | MEDIUM   | Constraints can conflict or reinforce each other |
| requirement    | implementation | HIGH     | Requirements should be implemented               |
| design         | implementation | HIGH     | Design principles guide implementation           |
| implementation | implementation | LOW      | Most pairs are unrelated unless same domain      |
| requirement    | requirement    | LOW      | Usually independent                              |
| design         | design         | LOW      | Usually independent                              |

**Filtering Strategy:**
```python
def get_type_priority(fact1_type, fact2_type):
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
    }

    pair = (fact1_type, fact2_type)
    if pair in high_priority:
        return 'HIGH'
    elif pair in medium_priority:
        return 'MEDIUM'
    else:
        return 'LOW'
```

**Expected Reduction:**
- Skip LOW priority pairs = eliminates ~60% of implementation-implementation pairs
- Estimated: 9,591 → ~4,500 pairs

---

### Rule 2: Artifact Type Pairing

**Principle:** Cross-artifact relationships (doc ↔ code) are more valuable than same-artifact relationships.

**Strategy:**
```python
def get_artifact_priority(fact1_artifacts, fact2_artifacts):
    # Check if facts come from different artifact types
    artifacts1 = set(e['artifact_id'] for e in fact1_artifacts)
    artifacts2 = set(e['artifact_id'] for e in fact2_artifacts)

    # If one is from artifact_1 (doc) and other from artifact_78 (code)
    has_doc = 'artifact_1' in artifacts1 or 'artifact_1' in artifacts2
    has_code = 'artifact_78' in artifacts1 or 'artifact_78' in artifacts2

    if has_doc and has_code:
        return 'HIGH'  # Cross-artifact: doc ↔ code
    else:
        return 'MEDIUM'  # Same artifact type
```

**Expected Reduction:**
- Prioritize 76 × 63 = 4,788 cross-artifact pairs
- De-prioritize C(76,2) + C(63,2) = 2,850 + 1,953 = 4,803 same-artifact pairs
- Can skip ~50% of same-artifact LOW priority pairs
- Estimated: 4,500 → ~2,700 pairs

---

### Rule 3: Keyword/Domain Similarity

**Principle:** Facts sharing domain keywords are more likely to be related.

**Domain Categories:**

```python
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

def extract_domains(statement):
    """Extract all domain categories for a fact statement."""
    statement_lower = statement.lower()
    domains = set()

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in statement_lower:
                domains.add(domain)
                break

    return domains

def calculate_domain_similarity(fact1, fact2):
    """Calculate Jaccard similarity between fact domains."""
    domains1 = extract_domains(fact1['statement'])
    domains2 = extract_domains(fact2['statement'])

    if not domains1 or not domains2:
        return 0.0

    intersection = len(domains1 & domains2)
    union = len(domains1 | domains2)

    return intersection / union if union > 0 else 0.0
```

**Filtering Strategy:**
```python
def should_analyze_by_domain(fact1, fact2):
    similarity = calculate_domain_similarity(fact1, fact2)

    # HIGH: Share at least one domain category
    if similarity > 0.0:
        return True

    # Special case: Always check constraint facts against implementation
    if (fact1['type'] == 'constraint' and fact2['type'] == 'implementation') or \
       (fact1['type'] == 'implementation' and fact2['type'] == 'constraint'):
        return True

    # Skip pairs with no domain overlap
    return False
```

**Expected Reduction:**
- Skip pairs with zero domain overlap (except high-priority type pairs)
- Estimated: 2,700 → ~1,200 pairs

---

### Rule 4: Confidence-Based Filtering

**Principle:** Low-confidence facts are less reliable for establishing relationships.

**Strategy:**
```python
def should_analyze_by_confidence(fact1, fact2):
    # Skip if both facts have low confidence
    if fact1['confidence'] < 0.85 and fact2['confidence'] < 0.85:
        return False

    # Skip if either fact has very low confidence
    if fact1['confidence'] < 0.75 or fact2['confidence'] < 0.75:
        return False

    return True
```

**Expected Reduction:**
- From our data: Most facts have confidence 1.0, few have 0.9
- Minimal reduction, but improves quality
- Estimated: 1,200 → ~1,150 pairs

---

### Rule 5: Location-Based Proximity (for same-artifact pairs)

**Principle:** Facts from nearby code locations are more likely to be related.

**Strategy:**
```python
def calculate_location_proximity(fact1, fact2):
    """Calculate proximity score for facts from the same artifact."""
    for e1 in fact1['extracted_from']:
        for e2 in fact2['extracted_from']:
            if e1['artifact_id'] == e2['artifact_id']:
                # Parse line numbers
                lines1 = parse_line_numbers(e1['location'])
                lines2 = parse_line_numbers(e2['location'])

                if lines1 and lines2:
                    # Calculate distance between line ranges
                    distance = min(abs(l1 - l2)
                                 for l1 in lines1
                                 for l2 in lines2)

                    # Close proximity: within 50 lines
                    if distance <= 50:
                        return 'HIGH'
                    # Medium proximity: within 200 lines
                    elif distance <= 200:
                        return 'MEDIUM'

    return 'LOW'

def parse_line_numbers(location):
    """Extract line numbers from location string."""
    import re
    # Match patterns like "Lines 85-118" or "Line 24"
    match = re.search(r'Lines? (\d+)(?:-(\d+))?', location)
    if match:
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        return range(start, end + 1)
    return None
```

**Filtering Strategy:**
```python
def should_analyze_by_proximity(fact1, fact2):
    # Only apply to same-artifact pairs
    artifacts1 = set(e['artifact_id'] for e in fact1['extracted_from'])
    artifacts2 = set(e['artifact_id'] for e in fact2['extracted_from'])

    if artifacts1 & artifacts2:  # Same artifact
        proximity = calculate_location_proximity(fact1, fact2)

        # For implementation-implementation pairs, require proximity
        if fact1['type'] == 'implementation' and fact2['type'] == 'implementation':
            return proximity in ['HIGH', 'MEDIUM']

        # For other types, proximity is a bonus but not required
        return True

    # Different artifacts: proximity doesn't apply
    return True
```

**Expected Reduction:**
- Reduces distant implementation-implementation pairs
- Estimated: 1,150 → ~700 pairs

---

### Rule 6: Semantic Name Similarity

**Principle:** Facts mentioning the same functions, structs, or variables are likely related.

**Strategy:**
```python
import re

def extract_code_entities(statement):
    """Extract function names, struct names, macros, and variables."""
    entities = set()

    # Function names (snake_case with parentheses)
    entities.update(re.findall(r'\b([a-z_][a-z0-9_]*)\(\)', statement.lower()))

    # Macros (ALL_CAPS)
    entities.update(re.findall(r'\b([A-Z][A-Z0-9_]{2,})\b', statement))

    # Struct/type names (camelCase or PascalCase)
    entities.update(re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b', statement))

    # Header files
    entities.update(re.findall(r'\b([a-z_]+\.h)\b', statement.lower()))

    # Common variables/fields
    entities.update(re.findall(r'\b(next|prev|head|tail|value)\b', statement.lower()))

    return entities

def calculate_entity_overlap(fact1, fact2):
    """Calculate overlap in code entities mentioned."""
    entities1 = extract_code_entities(fact1['statement'])
    entities2 = extract_code_entities(fact2['statement'])

    if not entities1 or not entities2:
        return 0.0

    intersection = len(entities1 & entities2)
    return intersection / min(len(entities1), len(entities2))

def should_analyze_by_entities(fact1, fact2):
    overlap = calculate_entity_overlap(fact1, fact2)

    # HIGH: Share at least one code entity
    return overlap > 0.0
```

**Expected Reduction:**
- Significant for implementation facts
- Estimated: 700 → ~500 pairs

---

## Complete Algorithm

### Step-by-Step Process

```python
def smart_pairing_algorithm(facts):
    """
    Intelligent fact pairing that reduces O(n²) to practical subset.

    Returns: List of fact pairs prioritized for relationship analysis.
    """
    candidate_pairs = []

    # Generate all possible pairs
    for i in range(len(facts)):
        for j in range(i + 1, len(facts)):
            fact1, fact2 = facts[i], facts[j]

            # Apply filtering rules in order (cheapest to most expensive)

            # Rule 4: Confidence filter (fastest check)
            if not should_analyze_by_confidence(fact1, fact2):
                continue

            # Rule 1: Type-based priority
            type_priority = get_type_priority(fact1['type'], fact2['type'])
            if type_priority == 'LOW':
                # Apply stricter criteria for LOW priority type pairs
                pass  # Continue to other filters

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

                # Must have domain overlap OR entity overlap
                if has_domain_overlap:
                    score += 5
                    reasons.append('domain_overlap')
                elif has_entity_overlap:
                    score += 3
                    reasons.append('entity_overlap')
                else:
                    # Skip even high-priority pairs with no overlap
                    continue

            # Cross-artifact pairs (doc ↔ code)
            elif artifact_priority == 'HIGH':
                score += 8
                reasons.append('cross_artifact')

                # Require domain or entity overlap
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

                # Require strong overlap
                if has_domain_overlap and has_entity_overlap:
                    score += 5
                    reasons.append('strong_overlap')
                else:
                    continue

            # Low priority type pairs (implementation ↔ implementation)
            else:
                # Very strict criteria
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


def execute_analysis(facts, budget_limit=500):
    """
    Execute relationship analysis with budget constraint.
    """
    candidate_pairs = smart_pairing_algorithm(facts)

    print(f"Generated {len(candidate_pairs)} candidate pairs from {len(facts)} facts")
    print(f"Reduction: {len(facts) * (len(facts) - 1) // 2} → {len(candidate_pairs)}")
    print(f"Reduction ratio: {len(candidate_pairs) / (len(facts) * (len(facts) - 1) // 2) * 100:.1f}%")

    # Take top N pairs within budget
    pairs_to_analyze = candidate_pairs[:budget_limit]

    print(f"\nAnalyzing top {len(pairs_to_analyze)} pairs")

    # Score distribution
    score_dist = {}
    for pair in pairs_to_analyze:
        score = pair['score']
        score_dist[score] = score_dist.get(score, 0) + 1

    print("\nScore distribution:")
    for score in sorted(score_dist.keys(), reverse=True):
        print(f"  Score {score}: {score_dist[score]} pairs")

    return pairs_to_analyze
```

---

## Estimated Reduction

### Filtering Pipeline

| Stage | Description | Pairs Remaining | Reduction |
|-------|-------------|-----------------|-----------|
| 0 | All possible pairs | 9,591 | 0% |
| 1 | Type-based filtering | 4,500 | 53% |
| 2 | Artifact priority | 2,700 | 72% |
| 3 | Domain similarity | 1,200 | 87% |
| 4 | Confidence filtering | 1,150 | 88% |
| 5 | Location proximity | 700 | 93% |
| 6 | Entity overlap | **~500** | **95%** |

### Final Estimates

**Target: 500 pairs**
- Cost: 500 × $0.003 = **$1.50** (vs $28.77)
- Time: 500 × 30s = **~4 hours** (vs 80 hours)
- **Savings: 95% cost reduction, 95% time reduction**

---

## Quality Assurance

### Ensuring High-Value Relationships Aren't Missed

**Multi-Pass Strategy:**

1. **Pass 1: High-confidence pairs (score ≥ 15)**
   - Constraint ↔ implementation with domain overlap
   - Cross-artifact pairs with strong signals
   - ~150 pairs

2. **Pass 2: Medium-confidence pairs (score 10-14)**
   - Medium priority types with overlap
   - Cross-artifact with entity overlap
   - ~200 pairs

3. **Pass 3: Lower-confidence pairs (score 5-9)**
   - Same-artifact with strong proximity
   - Specific domain-focused pairs
   - ~150 pairs

### Validation Strategy

After running the algorithm:

1. **Spot-check skipped pairs:** Randomly sample 50 pairs that were filtered out and manually verify they shouldn't have relationships.

2. **Domain coverage:** Ensure each domain category has sufficient pair coverage.

3. **Relationship density:** Target relationship density of 0.5+ (each fact should have ~1 relationship on average).

4. **Manual review:** Review any constraints that don't have implementation relationships found.

---

## Implementation Priority

### Phase 1: Core Implementation (Week 1)
1. Implement type-based filtering
2. Implement domain keyword extraction
3. Implement entity extraction
4. Basic scoring algorithm

### Phase 2: Optimization (Week 2)
1. Add proximity calculation
2. Add artifact priority
3. Tune scoring weights
4. Add confidence filtering

### Phase 3: Validation (Week 3)
1. Run on full dataset
2. Validate results
3. Adjust thresholds
4. Document patterns

---

## Future Enhancements

### Active Learning
After initial analysis, use discovered relationships to improve filtering:

```python
def learn_from_relationships(existing_relationships):
    """
    Analyze existing relationships to improve filtering.
    """
    patterns = []

    for rel in existing_relationships:
        fact1 = get_fact(rel['fact_id_1'])
        fact2 = get_fact(rel['fact_id_2'])

        pattern = {
            'type_pair': (fact1['type'], fact2['type']),
            'domains': extract_domains(fact1['statement']) &
                      extract_domains(fact2['statement']),
            'entities': extract_code_entities(fact1['statement']) &
                       extract_code_entities(fact2['statement']),
            'relationship_type': rel['type'],
        }
        patterns.append(pattern)

    # Use patterns to adjust scoring weights
    return patterns
```

### Incremental Analysis
For new facts added to the system:

```python
def analyze_new_fact(new_fact, existing_facts):
    """
    Only analyze new fact against existing facts, not all pairs.
    """
    pairs_to_analyze = []

    for existing_fact in existing_facts:
        # Apply same filtering logic
        if should_analyze_pair(new_fact, existing_fact):
            pairs_to_analyze.append((new_fact, existing_fact))

    return pairs_to_analyze
```

---

## Python Implementation

See complete implementation in `smart_pairing.py`:

```python
#!/usr/bin/env python3
"""
Smart Pairing Algorithm for Kraang Fact Relationship Analysis

Reduces O(n²) relationship analysis from 9,591 comparisons to ~500
using intelligent filtering heuristics.
"""

import json
import re
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

    # Macros (ALL_CAPS)
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


def smart_pairing_algorithm(facts: List[Dict]) -> List[Dict]:
    """
    Intelligent fact pairing that reduces O(n²) to practical subset.

    Returns: List of fact pairs prioritized for relationship analysis.
    """
    candidate_pairs = []

    print(f"Analyzing {len(facts)} facts...")
    print(f"Total possible pairs: {len(facts) * (len(facts) - 1) // 2}")

    # Generate all possible pairs with filtering
    for i in range(len(facts)):
        if i % 20 == 0:
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


def analyze_results(candidate_pairs: List[Dict], budget_limit: int = 500):
    """Analyze and report on candidate pairs."""
    print(f"\n{'='*60}")
    print(f"SMART PAIRING RESULTS")
    print(f"{'='*60}")

    print(f"\nGenerated {len(candidate_pairs)} candidate pairs")
    print(f"Reduction ratio: {len(candidate_pairs) / 9591 * 100:.1f}%")

    # Take top N pairs within budget
    pairs_to_analyze = candidate_pairs[:budget_limit]

    print(f"\nTop {len(pairs_to_analyze)} pairs for analysis:")
    print(f"  Cost: ${len(pairs_to_analyze) * 0.003:.2f} (vs $28.77)")
    print(f"  Time: ~{len(pairs_to_analyze) * 30 / 3600:.1f} hours (vs 80 hours)")

    # Score distribution
    score_dist = defaultdict(int)
    for pair in pairs_to_analyze:
        score_dist[pair['score']] += 1

    print("\nScore distribution:")
    for score in sorted(score_dist.keys(), reverse=True):
        print(f"  Score {score}: {score_dist[score]} pairs")

    # Reason distribution
    reason_dist = defaultdict(int)
    for pair in pairs_to_analyze:
        for reason in pair['reasons']:
            reason_dist[reason] += 1

    print("\nReason distribution:")
    for reason, count in sorted(reason_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"  {reason}: {count} pairs")

    return pairs_to_analyze


def main():
    """Main execution function."""
    # Load facts
    with open('.kraang/facts.json') as f:
        facts = json.load(f)

    print(f"Loaded {len(facts)} facts")

    # Run smart pairing algorithm
    candidate_pairs = smart_pairing_algorithm(facts)

    # Analyze results
    top_pairs = analyze_results(candidate_pairs, budget_limit=500)

    # Save results
    output_file = '.kraang/candidate_pairs.json'
    with open(output_file, 'w') as f:
        json.dump(top_pairs, f, indent=2)

    print(f"\nSaved top pairs to {output_file}")

    # Show sample high-priority pairs
    print(f"\n{'='*60}")
    print("SAMPLE HIGH-PRIORITY PAIRS:")
    print(f"{'='*60}\n")

    for pair in top_pairs[:5]:
        print(f"Pair: {pair['fact1_id']} ↔ {pair['fact2_id']}")
        print(f"  Score: {pair['score']}")
        print(f"  Reasons: {', '.join(pair['reasons'])}")
        print(f"  Type priority: {pair['type_priority']}")
        print(f"  Artifact priority: {pair['artifact_priority']}")
        print()


if __name__ == '__main__':
    main()
```

---

## Summary

This smart pairing algorithm reduces relationship analysis from **9,591 comparisons to ~500** through intelligent filtering based on:

1. **Type combinations** (constraint ↔ implementation is high priority)
2. **Artifact sources** (documentation ↔ code cross-references)
3. **Domain similarity** (shared keywords indicate related concepts)
4. **Confidence scores** (skip low-confidence facts)
5. **Location proximity** (nearby code is more likely related)
6. **Entity overlap** (shared function/struct names)

**Results:**
- **95% reduction** in comparisons
- **$1.50 cost** instead of $28.77
- **~4 hours** instead of 80 hours
- **High confidence** in discovering valuable relationships through prioritized analysis

The algorithm is designed to be tunable, allowing threshold adjustments based on initial results to optimize the balance between coverage and efficiency.
