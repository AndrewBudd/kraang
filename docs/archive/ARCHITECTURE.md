# Kraang Architecture

## Core Thesis

> "The core activity of building software is rationalizing conflicting constraints."

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Kraang CLI                           │
│  (User interface for managing artifacts and facts)          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  KraangStore │   │  Extractor   │   │  Analyzer    │
│  (Persist)   │   │  (LLM)       │   │  (LLM)       │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────────────────────────────────────────────┐
│               .kraang/ JSON Storage                  │
│  - artifacts.json                                    │
│  - facts.json                                        │
│  - relationships.json                                │
│  - config.json                                       │
└──────────────────────────────────────────────────────┘
```

## Core Components

### 1. KraangStore
**Purpose:** Manages persistent storage of all project data

**Responsibilities:**
- Initialize project structure (.kraang/ directory)
- CRUD operations for artifacts, facts, relationships
- ID generation and management
- JSON serialization/deserialization

**Storage Format:** Git-friendly JSON files

### 2. KraangExtractor
**Purpose:** LLM-powered fact extraction and relationship analysis

**Key Operations:**

#### extract_facts(artifact) → List[Fact]
Uses Claude to:
1. Read artifact content
2. Identify facts, constraints, requirements
3. Determine fact type (requirement/implementation/design/constraint)
4. Extract source location (lines, functions, sections)
5. Assign confidence scores

**Prompt Strategy:**
- Provide full artifact content
- Request structured JSON output
- Focus on extractable, verifiable facts
- Include location references

#### analyze_relationships(fact1, fact2) → Relationship
Uses Claude to:
1. Compare two facts
2. Determine relationship type (supports/contradicts/extends/unrelated)
3. Provide reasoning
4. Assign confidence score

**Optimization Opportunity:** Could filter pairs before sending to LLM (e.g., don't compare facts from same artifact, or facts of very different types)

### 3. KraangCLI
**Purpose:** Command-line interface for user interaction

**Commands:**
- `init` - Initialize new project
- `add <path>` - Register artifact
- `extract <id>` - Extract facts from artifact
- `relate` - Analyze fact relationships
- `conflicts` - Show contradictions
- `impact <id>` - Impact analysis
- `list` - List artifacts/facts/relationships

## Data Model

### Entity-Relationship Diagram

```
┌────────────┐
│  Artifact  │
│  (Source)  │
└─────┬──────┘
      │
      │ extracted_from
      │ (1:N)
      ▼
┌────────────┐
│    Fact    │
│(Constraint)│
└─────┬──────┘
      │
      │ relates_to
      │ (N:N)
      │
      ▼
┌────────────────┐
│  Relationship  │
│  (Graph Edge)  │
└────────────────┘
```

### Artifact
```python
{
    "id": str,              # artifact_1, artifact_2, ...
    "type": str,            # code, doc, requirement, config
    "path": str,            # filesystem path
    "content": str          # full text content
}
```

**Design Notes:**
- Content stored for extraction, could be omitted later to save space
- Path is relative or absolute based on user input
- Type auto-detected from extension but can be overridden

### Fact (Constraint)
```python
{
    "id": str,              # fact_1, fact_2, ...
    "statement": str,       # human-readable constraint
    "type": str,            # requirement/implementation/design/constraint
    "extracted_from": [     # multiple sources can support one fact
        {
            "artifact_id": str,
            "location": str  # "lines 10-15", "function foo", etc.
        }
    ],
    "confidence": float     # 0.0 - 1.0
}
```

**Design Notes:**
- Statement is the core truth claim
- Type helps categorize and filter facts
- Multiple extraction sources allow fact aggregation
- Confidence helps rank importance/reliability

### Relationship
```python
{
    "fact_id_1": str,
    "fact_id_2": str,
    "type": str,            # supports, contradicts, extends
    "confidence": float,    # 0.0 - 1.0
    "reasoning": str        # explanation from LLM
}
```

**Design Notes:**
- Directed graph edge (could be treated as undirected)
- Reasoning provides human-readable explanation
- Confidence allows filtering weak relationships

## Workflow

### Typical Usage Flow

```
1. User: kraang init
   └─> Creates .kraang/ directory structure

2. User: kraang add docs/CLAUDE.md
   └─> Registers artifact, reads content
   └─> Saves to artifacts.json

3. User: kraang extract artifact_1
   └─> Reads artifact content
   └─> Sends to Claude API
   └─> Parses JSON response
   └─> Creates Fact objects
   └─> Saves to facts.json

4. User: kraang add src/memory.c
   └─> Registers second artifact

5. User: kraang extract artifact_2
   └─> Extracts implementation facts

6. User: kraang relate
   └─> For each pair of facts:
       ├─> Send both to Claude API
       ├─> Parse relationship response
       ├─> If not "unrelated", save to relationships.json
       └─> (Could be optimized with smarter pairing)

7. User: kraang conflicts
   └─> Filter relationships WHERE type = "contradicts"
   └─> Display with context

8. User: kraang impact fact_1
   └─> Load fact_1
   └─> Find all relationships involving fact_1
   └─> Display sources and related facts
```

## LLM Integration

### API Usage

**Model:** claude-sonnet-4-5-20250929
- Good balance of capability and cost
- Strong reasoning for relationship analysis
- Reliable JSON output

**Cost Considerations:**
- Extraction: ~500-2000 tokens input, ~1000-3000 tokens output per artifact
- Relationship: ~200-500 tokens input, ~100-200 tokens output per pair
- For 10 artifacts with 50 facts: ~50 + 1,225 relationship checks = ~1,275 API calls
  (Without optimization)

**Optimization Strategies:**
1. Cache responses (not yet implemented)
2. Batch operations (not yet implemented)
3. Smart pairing - only compare facts that might be related:
   - Same artifact → likely supports/extends
   - Different artifact types → might contradict
   - Similar keywords → potentially related
4. User-directed relationship analysis (only check specific pairs)

### Prompt Engineering

**Extraction Prompt:**
- Provides full artifact content
- Specifies output format (JSON)
- Gives examples of good facts
- Requests location information
- Asks for confidence scores

**Relationship Prompt:**
- Provides both facts with context
- Defines relationship types clearly
- Allows "unrelated" to filter noise
- Requests reasoning for transparency

## Scalability Considerations

### Current Limitations (MVP)

1. **O(n²) relationship analysis**
   - All pairs compared
   - No filtering or optimization
   - Could be expensive for large projects

2. **No incremental updates**
   - Changing artifact requires re-extraction
   - No change detection

3. **No caching**
   - Same extraction could be repeated
   - API costs not minimized

4. **In-memory processing**
   - Loads all data into memory
   - Fine for small projects, could scale poorly

### Future Optimizations

1. **Smart Relationship Pairing**
   ```python
   def should_compare(fact1: Fact, fact2: Fact) -> bool:
       # Same artifact → likely supports/extends
       # Different types → potentially contradicts
       # Keyword overlap → worth checking
       # Already checked → skip
   ```

2. **Incremental Extraction**
   ```python
   # Track file hashes
   # Only re-extract if content changed
   # Invalidate derived relationships
   ```

3. **Response Caching**
   ```python
   # Cache by (artifact_id, content_hash) → facts
   # Cache by (fact1_id, fact2_id) → relationship
   ```

4. **Batch Processing**
   ```python
   # Extract multiple artifacts in parallel
   # Send multiple relationship queries in one request
   ```

## Extension Points

### Custom Extractors
Could support domain-specific extractors:
```python
class TypeSystemExtractor(KraangExtractor):
    """Extract type constraints from code"""

class SecurityExtractor(KraangExtractor):
    """Extract security requirements"""
```

### Query Language
```python
# Future: Structured queries
kraang.query(
    fact_type="constraint",
    artifact_type="code",
    relationship="contradicts"
)
```

### Visualization
```python
# Future: Generate constraint graphs
kraang.visualize(
    output="constraint-graph.html",
    highlight_conflicts=True
)
```

### Git Integration
```python
# Future: Track constraint evolution
kraang.diff("HEAD~5", "HEAD")
# Show how constraints changed over time
```

## Design Decisions

### Why JSON?
- Human-readable
- Git-friendly (easy diffs)
- No database setup required
- Simple to process with external tools
- Easy to backup/restore

### Why Claude?
- Strong reasoning capabilities
- Reliable JSON output
- Good at understanding context
- Handles code and prose equally well

### Why CLI?
- Easy to integrate with workflows
- Scriptable and automatable
- No UI complexity for MVP
- Can add web UI later

### Why Python?
- Rapid prototyping
- Good Anthropic SDK
- Easy to extend
- Familiar to most developers

## Testing Strategy

See TESTING.md for detailed test plan.

**Key Test Scenarios:**
1. Extract facts from documentation
2. Extract facts from code
3. Detect contradictions between docs and code
4. Impact analysis for constraint changes

**Success Criteria:**
- Extraction accuracy: >80%
- Relationship accuracy: >70%
- Useful for real development tasks
- Reasonable performance (<1 min for 10 artifacts)

## Security Considerations

1. **API Key Management**
   - Uses ANTHROPIC_API_KEY environment variable
   - Never stored in code or data files

2. **Code Execution**
   - Never executes artifact code
   - Read-only analysis

3. **Data Privacy**
   - Artifact contents sent to Claude API
   - Consider for sensitive codebases

## Future Directions

1. **Visual Constraint Graph**
   - Interactive web UI
   - Highlight conflicts in red
   - Show impact radius

2. **Confidence Calibration**
   - Learn from user corrections
   - Adjust scoring based on feedback

3. **Team Collaboration**
   - Share .kraang/ in git
   - Review fact extractions in PRs
   - Collaborative constraint management

4. **IDE Integration**
   - VSCode extension
   - Inline constraint warnings
   - Quick impact analysis

5. **CI/CD Integration**
   - Pre-commit hook to check conflicts
   - Block merges that violate constraints
   - Automated constraint documentation
