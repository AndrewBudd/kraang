# Kraang Example Output

This document shows example outputs from analyzing the LotJ codebase.

## Example: .kraang/artifacts.json

```json
[
  {
    "id": "artifact_1",
    "type": "doc",
    "path": "/home/budda/Code/LotJ/CLAUDE.md",
    "content": "# Claude Code Helper Guide for LotJ\n\n..."
  },
  {
    "id": "artifact_2",
    "type": "code",
    "path": "/home/budda/Code/LotJ/src/act_comm.c",
    "content": "#include \"mud.h\"\n#include \"functions.h\"\n..."
  }
]
```

## Example: .kraang/facts.json

```json
[
  {
    "id": "fact_1",
    "statement": "For local development, ALWAYS use Docker Compose. Never attempt to build or run services directly in the local environment.",
    "type": "constraint",
    "extracted_from": [
      {
        "artifact_id": "artifact_1",
        "location": "lines 5-13, Docker-First Development section"
      }
    ],
    "confidence": 1.0
  },
  {
    "id": "fact_2",
    "statement": "Memory allocation must use CREATE macro instead of raw malloc()",
    "type": "constraint",
    "extracted_from": [
      {
        "artifact_id": "artifact_1",
        "location": "lines 255-270, Memory Management section"
      }
    ],
    "confidence": 1.0
  },
  {
    "id": "fact_3",
    "statement": "Never create new header files - use existing structure (mud.h, types.h, functions.h, globals.h)",
    "type": "constraint",
    "extracted_from": [
      {
        "artifact_id": "artifact_1",
        "location": "lines 207-208, Header Files section"
      }
    ],
    "confidence": 1.0
  },
  {
    "id": "fact_4",
    "statement": "All struct definitions must be placed in types.h",
    "type": "constraint",
    "extracted_from": [
      {
        "artifact_id": "artifact_1",
        "location": "lines 220-224, types.h description"
      }
    ],
    "confidence": 1.0
  },
  {
    "id": "fact_5",
    "statement": "Function do_say() uses DISPOSE() for memory cleanup",
    "type": "implementation",
    "extracted_from": [
      {
        "artifact_id": "artifact_2",
        "location": "function do_say, line 245"
      }
    ],
    "confidence": 0.95
  },
  {
    "id": "fact_6",
    "statement": "act_comm.c includes mud.h and functions.h headers",
    "type": "implementation",
    "extracted_from": [
      {
        "artifact_id": "artifact_2",
        "location": "lines 1-5, header includes"
      }
    ],
    "confidence": 1.0
  },
  {
    "id": "fact_7",
    "statement": "Linked lists must use LINK/UNLINK macros, never manual pointer manipulation",
    "type": "constraint",
    "extracted_from": [
      {
        "artifact_id": "artifact_1",
        "location": "lines 283-310, Linked Lists section"
      }
    ],
    "confidence": 1.0
  }
]
```

## Example: .kraang/relationships.json

```json
[
  {
    "fact_id_1": "fact_2",
    "fact_id_2": "fact_5",
    "type": "supports",
    "confidence": 0.9,
    "reasoning": "The implementation in do_say() using DISPOSE() follows the documented constraint to use custom memory management macros instead of raw free()"
  },
  {
    "fact_id_1": "fact_2",
    "fact_id_2": "fact_7",
    "type": "supports",
    "confidence": 0.85,
    "reasoning": "Both constraints enforce the pattern of using project-specific macros instead of raw pointer manipulation or standard library functions"
  },
  {
    "fact_id_1": "fact_3",
    "fact_id_2": "fact_6",
    "type": "supports",
    "confidence": 0.95,
    "reasoning": "The implementation includes only existing headers (mud.h, functions.h) which aligns with the constraint to never create new header files"
  }
]
```

## Example CLI Output

### Extracting Facts

```
$ ./kraang.py extract artifact_1
Extracting facts from /home/budda/Code/LotJ/CLAUDE.md...
✓ Extracted 12 facts:
  fact_1: For local development, ALWAYS use Docker Compose. Never attempt to bui...
  fact_2: Memory allocation must use CREATE macro instead of raw malloc()...
  fact_3: Never create new header files - use existing structure (mud.h, types.h...
  fact_4: All struct definitions must be placed in types.h...
  fact_5: All function prototypes must be placed in functions.h...
  fact_6: Global variable extern declarations must be placed in globals.h...
  fact_7: Linked lists must use LINK/UNLINK macros, never manual pointer manipul...
  fact_8: All builds MUST have zero compiler warnings...
  fact_9: Use DISPOSE() to free memory, never raw free()...
  fact_10: String memory management uses STRALLOC/STRFREE...
  fact_11: Docker-compose down rebuilds database which takes 10+ minutes...
  fact_12: Testing credentials are username: legend, password: password...
```

### Analyzing Relationships

```
$ ./kraang.py relate
Analyzing relationships between 12 facts...
  fact_2 <-> fact_5: supports
  fact_2 <-> fact_7: supports
  fact_2 <-> fact_9: extends
  fact_3 <-> fact_6: supports
  fact_4 <-> fact_3: supports
  fact_5 <-> fact_3: supports
  fact_9 <-> fact_2: extends
  fact_10 <-> fact_2: extends
✓ Found 8 relationships
```

### Checking Conflicts

```
$ ./kraang.py conflicts
✓ No contradictions found

# (This means the documentation and code are consistent!)
```

### Impact Analysis

```
$ ./kraang.py impact fact_2
Impact analysis for: Memory allocation must use CREATE macro instead of raw malloc()

Source artifacts:
  - /home/budda/Code/LotJ/CLAUDE.md (lines 255-270, Memory Management section)

Related facts (4):
  [extends] fact_9: Use DISPOSE() to free memory, never raw free()
  [extends] fact_10: String memory management uses STRALLOC/STRFREE
  [supports] fact_7: Linked lists must use LINK/UNLINK macros, never manual pointer manipulation
  [supports] fact_5: Function do_say() uses DISPOSE() for memory cleanup
```

## Example: Finding a Real Contradiction

If we were to analyze a legacy file that violates the constraints:

### .kraang/facts.json (additional fact)
```json
{
  "id": "fact_20",
  "statement": "legacy_code.c uses malloc() for buffer allocation",
  "type": "implementation",
  "extracted_from": [
    {
      "artifact_id": "artifact_5",
      "location": "function old_parser, line 123"
    }
  ],
  "confidence": 1.0
}
```

### .kraang/relationships.json (contradiction)
```json
{
  "fact_id_1": "fact_2",
  "fact_id_2": "fact_20",
  "type": "contradicts",
  "confidence": 0.95,
  "reasoning": "The documented constraint requires using CREATE macro, but the implementation uses raw malloc() which is explicitly forbidden"
}
```

### CLI Output
```
$ ./kraang.py conflicts
Found 1 contradictions:

CONTRADICTION (confidence: 0.95)
  Fact 1 (fact_2): Memory allocation must use CREATE macro instead of raw malloc()
  Fact 2 (fact_20): legacy_code.c uses malloc() for buffer allocation
  Reasoning: The documented constraint requires using CREATE macro, but the
  implementation uses raw malloc() which is explicitly forbidden

```

## Storage Structure

```
.kraang/
├── config.json          # Project config (next_id counter, etc.)
├── artifacts.json       # All registered artifacts
├── facts.json          # All extracted facts
└── relationships.json  # All fact relationships
```

Each file is human-readable JSON, making it easy to:
- Review in text editor
- Diff in git
- Process with jq or other tools
- Import into other systems

## Query Examples (Future)

While not implemented in MVP, here are example queries that would be useful:

```
# Find all constraints about memory
./kraang.py query "type:constraint AND statement:*memory*"

# Find all contradictions involving code artifacts
./kraang.py query "relationship:contradicts AND artifact_type:code"

# Show facts from a specific file
./kraang.py query "artifact:src/act_comm.c"

# Impact of changing any memory-related constraint
./kraang.py impact --filter "statement:*memory*"
```

## Visualization (Future)

The constraint graph could be visualized as:

```
[CLAUDE.md Documentation]
    ↓ (extracted from)
[fact_2: Use CREATE macro]
    ↓ (extends)
[fact_9: Use DISPOSE macro]
    ↓ (supports)
[fact_5: do_say() uses DISPOSE()]
    ↑ (extracted from)
[act_comm.c Implementation]
```

With contradictions highlighted in red and supports in green.
