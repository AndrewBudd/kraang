# Kraang Testing Plan

## Initial Prototype Test Strategy

### Test Hypothesis
Can we extract and link constraints from heterogeneous artifacts in a way that reveals conflicts and enables impact analysis?

### Test Artifacts (From LotJ)

1. **CLAUDE.md** (documentation)
   - Explicit constraints about development practices
   - Memory management rules
   - Header file structure rules
   - Docker usage requirements

2. **C Source Files** (implementation)
   - Actual memory allocation patterns
   - Header includes
   - Function implementations

3. **README.md** (documentation)
   - High-level setup requirements
   - Developer workflow

### Expected Extractions from CLAUDE.md

#### Constraint Facts:
1. "Docker-compose MUST be used for local development, never build directly"
   - Type: constraint
   - Location: lines 5-7, "IMPORTANT: Docker-First Development"

2. "Memory allocation MUST use CREATE macro, not raw malloc"
   - Type: constraint
   - Location: lines 255-270, "Memory Management"

3. "Never create new header files, use existing structure"
   - Type: constraint
   - Location: lines 207-208

4. "All builds MUST have zero compiler warnings"
   - Type: constraint
   - Location: line 203

5. "Use LINK/UNLINK macros for doubly linked lists, never manual pointer management"
   - Type: constraint
   - Location: lines 283-310

#### Implementation Facts:
6. "Header files are: mud.h, types.h, functions.h, globals.h"
   - Type: design
   - Location: lines 209-229

7. "Testing available via tools/tester with credentials legend/password"
   - Type: implementation
   - Location: lines 88-91

### Expected Extractions from C Source

Example from hypothetical act_comm.c:

8. "Function do_say allocates memory for message buffer"
   - Type: implementation
   - Location: function do_say, lines 150-170

9. "Includes mud.h and functions.h"
   - Type: implementation
   - Location: lines 1-10

### Expected Relationships

#### SUPPORTS:
- Fact 2 SUPPORTS Fact 5: Both enforce structured memory/pointer management
- Fact 6 SUPPORTS Fact 3: Existing headers reinforce no-new-headers rule

#### CONTRADICTS:
- If we find `malloc()` in code: Implementation would CONTRADICT Fact 2
- If we find new header file: Would CONTRADICT Fact 3
- If we find manual `next`/`prev` pointer assignment: Would CONTRADICT Fact 5

### Impact Analysis Example

**Query:** "What if we remove the CREATE macro requirement?"

**Expected Output:**
```
Impact analysis for: "Memory allocation MUST use CREATE macro, not malloc"

Source artifacts:
  - ~/Code/LotJ/CLAUDE.md (lines 255-270)

Related facts (5):
  [supports] Use DISPOSE to free memory allocated with CREATE
  [extends] STRALLOC/STRFREE for string memory management
  [contradicts] File src/legacy.c uses raw malloc (confidence: 0.85)

Affected artifacts:
  - All C source files using CREATE (~200 files)
  - mud.h header with CREATE macro definition
  - Developer documentation in CLAUDE.md

Risks:
  - Would require rewriting all allocation code
  - Could introduce memory leaks if not careful
  - Violates documented development standards
```

## Manual Test Steps

### Test 1: Fact Extraction Accuracy
```bash
./kraang.py init
./kraang.py add ~/Code/LotJ/CLAUDE.md doc
./kraang.py extract artifact_1
./kraang.py list facts
```

**Success Criteria:**
- Extract at least 5 constraint facts from CLAUDE.md
- Each fact has clear statement, type, and location
- Confidence scores are reasonable (0.7-1.0)

### Test 2: Code Analysis
```bash
./kraang.py add ~/Code/LotJ/src/act_comm.c code
./kraang.py extract artifact_2
```

**Success Criteria:**
- Extract implementation facts about memory usage, functions, patterns
- Facts reference specific line numbers or function names

### Test 3: Relationship Detection
```bash
./kraang.py relate
./kraang.py conflicts
```

**Success Criteria:**
- Identify at least one SUPPORTS relationship
- If code violates documented constraints, identify CONTRADICTS relationship
- Reasoning for each relationship makes sense

### Test 4: Impact Analysis
```bash
./kraang.py impact fact_1
```

**Success Criteria:**
- Shows source artifacts with locations
- Lists related facts with relationship types
- Provides actionable information about change consequences

## Validation Questions

After running tests, evaluate:

1. **Extraction Quality:**
   - Are the extracted facts accurate?
   - Are they at the right level of abstraction?
   - Do locations correctly point to source?

2. **Relationship Accuracy:**
   - Do the relationships make sense?
   - Are contradictions real conflicts?
   - Is the reasoning sound?

3. **Usefulness:**
   - Would this help a developer understand constraints?
   - Would this catch documentation drift?
   - Would this help with refactoring decisions?

4. **Performance:**
   - How long does extraction take?
   - How many API calls are needed?
   - Is the cost reasonable?

## Expected Limitations (MVP)

1. No batch processing yet (one artifact at a time)
2. No incremental updates (re-extracts everything)
3. No caching of LLM responses
4. No visualization of constraint graph
5. Relationship analysis is O(n²) for n facts
6. No query language for complex questions
7. No integration with git history

## Next Steps After Validation

If tests pass:
1. Add batch extraction for directories
2. Optimize relationship analysis (don't compare unrelated facts)
3. Add confidence calibration based on feedback
4. Build simple web UI for visualization
5. Add more artifact types (test files, configs)
6. Implement incremental updates
7. Add query DSL for impact analysis

## Metrics to Track

- Extraction time per artifact
- Number of facts per artifact (should be 3-15 typically)
- Accuracy of contradictions (manual review)
- API cost per analysis
- Storage size of .kraang directory
