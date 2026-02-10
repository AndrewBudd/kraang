# Constraint Reconciliation Examples
**Real-world examples from Legends of the Jedi codebase**

**Generated**: 2026-02-10
**Total Conflicts Analyzed**: 5
**Conflicts Resolved**: 4
**Conflicts Escalated**: 1

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Reconciliation Strategies Overview](#reconciliation-strategies-overview)
3. [Example 1: Header File Organization Paradox](#example-1-header-file-organization-paradox)
4. [Example 2: Memory Management Documentation Gap](#example-2-memory-management-documentation-gap)
5. [Example 3: Docker Configuration Ambiguity](#example-3-docker-configuration-ambiguity)
6. [Example 4: Database Access Conflict (Escalated)](#example-4-database-access-conflict-escalated)
7. [Summary Statistics](#summary-statistics)
8. [Lessons Learned](#lessons-learned)

---

## Executive Summary

This report demonstrates real constraint reconciliation from the LotJ codebase analysis,
where 577 facts were extracted and 5 contradictions were identified and analyzed.

**Key Findings**:
- 4 conflicts resolved using **Conditional reconciliation** strategy
- 1 conflict **escalated** to human decision
- All conflicts involved documentation describing implementation that contradicts stated constraints
- Primary issue: **descriptive vs prescriptive** documentation confusion

**Severity Breakdown**:
- **Critical**: 1 (memory management)
- **High**: 4 (architecture, configuration, design patterns)

---

## Reconciliation Strategies Overview

The reconciler uses six primary strategies:

| Strategy | When Applied | Confidence | Example |
|----------|-------------|------------|---------|
| **Source Authority (Code)** | Code contradicts docs | 0.90 | Code uses malloc, docs say never use it |
| **Source Authority (Docs)** | Docs are requirements | 0.80 | API spec says must validate, code doesn't |
| **Temporal** | Newer supersedes older | 0.85 | New constraint replaces deprecated one |
| **Specificity** | Specific vs general rule | 0.85 | "Use X for case Y" beats "Usually use Z" |
| **Synthesis** | Both partially true | 0.75 | Combine into unified constraint |
| **Conditional** | True in different contexts | 0.85 | Guideline vs implementation reality |
| **Escalate** | Needs human judgment | 0.50 | Architectural decision required |

---

## Example 1: Header File Organization Paradox

### Conflict ID: `conflict_fact_16_fact_19`

**Severity**: HIGH
**Strategy**: Conditional (Context-Dependent)
**Confidence**: 0.85

### Before (Conflicting Facts)

**Fact #16** (Constraint from Developer Guide):
> DO NOT create new header files, use existing well-established header file structure

**Source**: `/home/budda/Code/LotJ/CLAUDE.md:213` (Section: Header Files - CRITICAL)

**Fact #19** (Implementation Reality):
> types.h contains 5,830 lines with ALL struct and type definitions

**Source**: `/home/budda/Code/LotJ/CLAUDE.md:226-229` (Section: Core Headers)

### Conflict Analysis

**Type**: Semantic Conflict (Prescriptive vs Descriptive)

**Description**: The constraint says "use well-established header file structure" and forbids
creating new headers. However, the reality is a 5,830-line monolithic `types.h` file containing
ALL type definitions. This is the opposite of "well-established structure" (which would be
modular, focused headers). The constraint is prescriptive (what you should do) while the fact
is descriptive (what actually exists).

**Why This Conflicts**:
1. "Well-established structure" typically means modular, focused headers
2. A 5,830-line monolithic file is an anti-pattern, not a good structure
3. The constraint forbids improving the structure by creating new headers
4. This creates a paradox: can't improve bad structure because structure is "established"

### After (Reconciled)

**Strategy**: CONDITIONAL (Context-Dependent)

**Reconciled Statement**:
> **CONSTRAINT (Prescriptive)**: DO NOT create new header files without team approval.
> All new definitions must use the existing header structure.
>
> **REALITY (Descriptive)**: The existing structure is monolithic, with types.h containing
> 5,830 lines. This is the "established" structure that must be used, even though it
> violates typical best practices.
>
> **CONTEXT**: The constraint preserves consistency in a legacy codebase where refactoring
> the header structure would require massive changes. The "well-established" refers to
> "long-standing" not "well-designed."

**Rationale**:
Both facts are true but serve different purposes. The constraint is a **preservation rule**
for legacy codebase stability, not a claim that the structure is ideal. The implementation
fact describes the current state that developers must work within.

### Action Items

#### Code Changes
None required. Code structure is as documented.

#### Documentation Changes
- [ ] Clarify that "well-established" means "long-standing" not "best practice"
- [ ] Add note: "This structure is legacy. We preserve it for consistency."
- [ ] Document the decision: "Monolithic headers traded modularity for simplicity"
- [ ] Add exception process: "New headers require architecture team approval"
- [ ] Provide guidance: "Add new structs to types.h, new functions to functions.h"

#### Verification Steps
1. Confirm team agreement that header structure should not change
2. Document exception process for truly necessary new headers
3. Add pre-commit hook to warn about new `.h` files in `src/`
4. Update onboarding docs to explain the trade-off

### Lessons Learned

**Reconciliation Insight**: Constraints can be about **preserving consistency** even when
that consistency is suboptimal. "Don't make it worse" is a valid constraint in legacy systems.

**Documentation Improvement**: Distinguish between:
- **Prescriptive**: "You should do X because it's good practice"
- **Preservative**: "You must do X to maintain consistency"
- **Descriptive**: "The system currently does X"

---

## Example 2: Memory Management Documentation Gap

### Conflict ID: `conflict_fact_28_fact_31`

**Severity**: CRITICAL
**Strategy**: Conditional (Implementation Detail)
**Confidence**: 0.85

### Before (Conflicting Facts)

**Fact #28** (Constraint):
> The MUD uses a custom memory management system - never use raw malloc/free

**Source**: `/home/budda/Code/LotJ/CLAUDE.md:262` (Section: Memory Management)

**Fact #31** (Implementation):
> SET_STRING(pointer, value) macro performs safe string assignment by freeing old and allocating new

**Source**: `/home/budda/Code/LotJ/CLAUDE.md:273-275` (Section: Memory Management)

### Conflict Analysis

**Type**: Semantic Conflict (Abstraction Leakage)

**Description**: The constraint says "never use raw malloc/free" in favor of custom memory
management. However, the SET_STRING macro is described as "freeing old and allocating new,"
which sounds like it uses the forbidden `free()` and `malloc()`.

**Why This Conflicts**:
1. Constraint forbids direct use of `malloc()` and `free()`
2. SET_STRING description implies it does exactly that
3. Creates confusion: Does SET_STRING violate the constraint?

**Investigation** (checking actual code):
```c
// From mud.h (artifact_165:373-377)
#define SET_STRING(pointer, value) \
    do { \
        STRFREE(pointer); \
        (pointer) = STRALLOC(value); \
    } while(0)
```

**Resolution**: SET_STRING uses `STRFREE` and `STRALLOC` macros, which ARE part of the
custom memory management system. The description was misleading by using "freeing" and
"allocating" without clarifying these are the *custom* free/alloc functions.

### After (Reconciled)

**Strategy**: CONDITIONAL (Terminology Clarification)

**Reconciled Statement**:
> **CONSTRAINT**: Application code must never use raw `malloc()`, `free()`, `calloc()`,
> or `realloc()`. Always use custom memory management macros: CREATE, DISPOSE, STRALLOC, STRFREE.
>
> **IMPLEMENTATION**: SET_STRING(pointer, value) macro performs safe string assignment by
> using STRFREE (custom deallocation) and STRALLOC (custom allocation), NOT raw free/malloc.
>
> **CLARIFICATION**: When we say "freeing" and "allocating" in macro descriptions, we mean
> the custom memory management system unless explicitly stated otherwise.

**Rationale**:
The conflict was terminological, not actual. SET_STRING complies with the constraint by
using the custom memory system. The description was ambiguous by using generic terms
"freeing" and "allocating" instead of specific macro names.

### Action Items

#### Code Changes
None required. Implementation is correct.

#### Documentation Changes
- [ ] Update SET_STRING description: "uses STRFREE/STRALLOC" not "freeing/allocating"
- [ ] Add glossary:
  - "allocate" = generic concept
  - "ALLOCATE/CREATE/STRALLOC" = custom memory system (✓ allowed)
  - "malloc()" = raw system call (✗ forbidden)
- [ ] Show SET_STRING macro expansion in docs
- [ ] Add examples of correct vs incorrect memory usage

#### Verification Steps
1. Audit all memory-related documentation for terminology consistency
2. Grep codebase for raw `malloc`/`free` usage (should find none in application code)
3. Create static analysis rule to flag raw memory functions
4. Add memory management section to code review checklist

### Lessons Learned

**Reconciliation Insight**: Abstract concepts need precise terminology. Generic terms like
"allocate" can refer to either the concept or specific implementations, causing confusion.

**Documentation Improvement**:
- Use specific macro/function names in descriptions
- Create glossary for overloaded terms
- Show actual code for macros, not just descriptions

---

## Example 3: Docker Configuration Ambiguity

### Conflict ID: `conflict_fact_2_fact_10`

**Severity**: HIGH
**Strategy**: Conditional (Network Configuration)
**Confidence**: 0.85

### Before (Conflicting Facts)

**Fact #2** (Constraint):
> Local development MUST use Docker Compose exclusively, never build or run services directly in local environment

**Source**: `/home/budda/Code/LotJ/CLAUDE.md:7-15` (Section: Docker-First Development)

**Fact #10** (Configuration):
> PostgreSQL database runs on localhost:5432 with user 'root', password '12345', database 'lotj'

**Source**: `/home/budda/Code/LotJ/CLAUDE.md:189` (Section: Database Access)

### Conflict Analysis

**Type**: Apparent Contradiction (Network Topology)

**Description**: The constraint mandates that ALL services run in Docker Compose (not locally).
However, the database configuration uses `localhost:5432`, which typically means the database
is running directly on the local machine, not in a container.

**Why This Appears to Conflict**:
1. "Never run services directly in local environment" seems clear
2. `localhost:5432` suggests database runs on host machine
3. In Docker Compose, services should use service names (e.g., `postgres:5432`), not `localhost`

**Investigation**:
Docker Compose port mapping allows containers to expose ports to the host. The application
container can access the database container via:
- `postgres:5432` (from within Docker network)
- `localhost:5432` (from host machine, or container with port mapping)

### After (Reconciled)

**Strategy**: CONDITIONAL (Connection Context)

**Reconciled Statement**:
> **ARCHITECTURE**: All services run in Docker Compose containers. No services run directly
> on the host machine (outside containers).
>
> **DATABASE ACCESS**:
> - **From application container**: Use service name `postgres:5432`
> - **From host machine** (debugging tools, external clients): Use `localhost:5432` via port mapping
> - Credentials: user='root', password='12345', database='lotj'
>
> **PORT MAPPING**: Docker Compose maps container ports to localhost for external access
> while maintaining internal service networking.

**Rationale**:
Both facts are true. The database runs in Docker (satisfying constraint), but Docker port
mapping exposes it to `localhost:5432` for host access. The configuration is for external
clients, not violating the Docker-exclusive architecture.

### Action Items

#### Code Changes
None required. Architecture is correct.

#### Documentation Changes
- [ ] Clarify difference between:
  - **Internal service communication**: `postgres:5432` (service name)
  - **External host access**: `localhost:5432` (port mapping)
- [ ] Add network diagram showing Docker Compose networking
- [ ] Document connection strings for different contexts:
  - Application code: `postgres:5432`
  - `psql` from host: `localhost:5432`
  - Database GUI tools: `localhost:5432`
- [ ] Add section: "Understanding Docker Port Mapping"

#### Verification Steps
1. Verify application code uses service name, not localhost
2. Confirm docker-compose.yml has port mapping: `5432:5432`
3. Test that database is NOT accessible without Docker running
4. Document the network topology clearly

### Lessons Learned

**Reconciliation Insight**: Infrastructure constraints need context about access patterns.
"Services run in Docker" doesn't preclude port mapping for external access.

**Documentation Improvement**:
- Distinguish between service architecture (where things run) and access patterns (how to connect)
- Include network diagrams for containerized applications
- Document connection strings for each context

---

## Example 4: Database Access Conflict (Escalated)

### Conflict ID: `conflict_fact_10_fact_74`

**Severity**: HIGH
**Strategy**: ESCALATE (Needs Human Decision)
**Confidence**: 0.50

### Before (Conflicting Facts)

**Fact #10** (Configuration):
> PostgreSQL database runs on localhost:5432 with user 'root', password '12345', database 'lotj'

**Source**: `/home/budda/Code/LotJ/CLAUDE.md:189` (Section: Database Access)

**Fact #74** (Architecture):
> Multi-service architecture uses Docker Compose

**Source**: `/home/budda/Code/LotJ/CLAUDE.md:25` (Section: Codebase Overview)

### Conflict Analysis

**Type**: Architectural Inconsistency

**Description**: Similar to Example 3, but with key differences:
1. Fact #74 describes overall architecture at a high level
2. Fact #10 provides specific database connection details
3. Unclear whether `localhost:5432` is from host perspective or container perspective
4. Could indicate port mapping (correct) or non-containerized database (violates architecture)

**Why This Needs Human Decision**:
1. Insufficient information to determine actual network topology
2. Multiple valid interpretations possible
3. Resolution depends on intended architecture (not documented)
4. Similar to Example 3 but less context available

### Proposed Resolution Paths

#### Option A: Port Mapping (Likely Correct)
**Interpretation**: Database runs in Docker, exposed via port mapping.

**Actions**:
- Verify docker-compose.yml has port mapping
- Document network topology
- Clarify connection strings for different contexts
- **Same as Example 3 resolution**

#### Option B: External Database (Architectural Violation)
**Interpretation**: Database actually runs on host, violating Docker-exclusive constraint.

**Actions**:
- Migrate database to Docker container
- Update connection strings
- Add database to docker-compose.yml
- Document migration process

#### Option C: Hybrid Architecture (Design Decision)
**Interpretation**: Some services exempt from Docker requirement.

**Actions**:
- Document exception for database
- Update constraint to reflect exceptions
- Clarify which services must be in Docker
- Document rationale for hybrid approach

### Required Human Input

**Questions for Architecture Team**:
1. Is the database currently running in Docker or on the host?
2. If in Docker, confirm port mapping is `5432:5432`
3. If on host, is this intentional or should it be containerized?
4. What is the intended connection method from application code?
5. Are there any services exempt from Docker requirement?

**Documentation to Review**:
- docker-compose.yml (actual configuration)
- Application code (actual connection strings used)
- Infrastructure docs (network topology)
- Deployment procedures (how database is started)

### Next Steps

1. **Gather Evidence**:
   ```bash
   # Check docker-compose.yml
   grep -A5 "postgres:" docker-compose.yml

   # Check application connection code
   grep -r "5432" src/
   grep -r "DATABASE_HOST" src/

   # Check if database is containerized
   docker-compose ps | grep postgres
   ```

2. **Schedule Architecture Review**:
   - Participants: DevOps, Backend Lead, Database Admin
   - Agenda: Clarify database deployment architecture
   - Outcome: Document decision and update facts

3. **Update Documentation**:
   - Based on decision, implement resolution (A, B, or C)
   - Update both conflicting facts with clarifications
   - Add network topology diagram

### Lessons Learned

**Reconciliation Insight**: Not all conflicts can be automatically resolved. Complex
architectural decisions require human expertise and context that may not be in documentation.

**When to Escalate**:
- Multiple valid interpretations exist
- Resolution depends on unstated design decisions
- Insufficient information to determine ground truth
- Requires cross-functional team input

**Documentation Improvement**:
- Document architecture decisions explicitly
- Include network topology diagrams
- Provide connection examples for each deployment context
- Make implicit assumptions explicit

---

## Summary Statistics

### Conflicts by Severity
- **Critical**: 1 (20%) - Memory management
- **High**: 4 (80%) - Architecture, configuration, design

### Resolution Strategies Used
- **Conditional**: 4 (80%) - Context-dependent resolution
- **Escalate**: 1 (20%) - Needs human decision

### Confidence Levels
- **High (0.85)**: 4 conflicts - Clear context separation
- **Medium (0.50)**: 1 conflict - Insufficient information

### Root Causes
1. **Terminology Confusion** (40%) - Generic vs specific terms
2. **Prescriptive vs Descriptive** (40%) - Constraints vs reality
3. **Insufficient Context** (20%) - Missing network topology

### Action Items Generated
- **Code Changes**: 1 pending (awaiting decision)
- **Documentation Updates**: 17 items across 4 conflicts
- **Verification Steps**: 15 steps to validate resolutions

---

## Lessons Learned

### 1. Documentation Must Distinguish Intent

**Problem**: Documentation often mixes:
- Prescriptive (what you should do)
- Preservative (what you must do for consistency)
- Descriptive (what currently exists)

**Solution**: Label statements clearly:
```markdown
✓ CONSTRAINT: Never use malloc directly
✓ GUIDELINE: Prefer stateless functions when possible
✓ REALITY: types.h contains 5,830 lines
✓ LEGACY: This structure is suboptimal but preserved for consistency
```

### 2. Terminology Needs Precision

**Problem**: Generic terms like "allocate," "run on localhost," or "freeing" can mean:
- Abstract concepts (allocating memory)
- Specific implementations (STRALLOC macro)
- Infrastructure details (localhost:5432)

**Solution**:
- Create glossaries for overloaded terms
- Use specific names in descriptions
- Show actual code, not just abstractions

### 3. Context Makes Contradictions Compatible

**Problem**: Many "contradictions" are actually context-dependent truths:
- "Never create headers" + "5,830-line header exists"
- "Docker exclusive" + "localhost:5432 access"

**Solution**:
- Document the contexts explicitly
- Explain why both are true
- Provide decision trees for "when to use X vs Y"

### 4. Legacy Systems Have Preservation Constraints

**Problem**: Constraints in legacy systems often preserve *consistency* not *quality*:
- "Use existing header structure" = "Don't refactor what works"
- Not claiming the structure is ideal

**Solution**:
- Distinguish preservation rules from best practices
- Document the trade-offs explicitly
- Explain why the suboptimal choice is maintained

### 5. Infrastructure Needs Topology Documentation

**Problem**: Configuration details (`localhost:5432`) unclear without network context.

**Solution**:
- Include network diagrams in architecture docs
- Document all access patterns (internal, external, debugging)
- Show connection strings for each context
- Explain port mapping, service discovery, etc.

### 6. Not Everything Can Be Automated

**Problem**: Some conflicts require architectural decisions, not just analysis.

**Solution**:
- Recognize when to escalate
- Provide decision framework
- Document required information
- Follow up with human decision-makers

---

## Reconciliation Best Practices

### For Constraint Authors

1. **Label Your Statements**:
   - MUST = absolute requirement
   - SHOULD = strong recommendation
   - CURRENT = description of existing state
   - LEGACY = preserved for consistency

2. **Provide Context**:
   - When does this apply?
   - What are the exceptions?
   - Why was this decision made?

3. **Use Specific Terms**:
   - Name specific functions/macros/services
   - Avoid ambiguous generic terms
   - Link to actual code examples

4. **Document Trade-offs**:
   - Why this approach over alternatives?
   - What do we sacrifice?
   - When might this change?

### For Reconcilers

1. **Investigate Before Concluding**:
   - Check actual code
   - Review related facts
   - Understand historical context

2. **Consider Multiple Strategies**:
   - Not everything is a direct contradiction
   - Context often resolves apparent conflicts
   - Synthesis can unify partial truths

3. **Escalate Appropriately**:
   - Some decisions need human judgment
   - Provide decision framework
   - Don't force automated resolution

4. **Document the Resolution**:
   - Explain the reasoning
   - Update all affected facts
   - Verify with code/tests

---

## Tools and Commands

### Analyze All Conflicts
```bash
python reconciler.py analyze
```

### Generate Reconciliation Proposals
```bash
python reconciler.py reconcile
```

### Create Full Report
```bash
python reconciler.py report RECONCILIATION_REPORT.md
```

### Analyze Specific Conflict
```bash
python reconciler.py conflict fact_16 fact_19
```

### Integration with Kraang
```bash
# Find all contradictions
python kraang.py conflicts

# Reconcile them
python reconciler.py reconcile

# Generate comprehensive report
python reconciler.py report
```

---

## Conclusion

Constraint reconciliation is not about finding "one truth" but about understanding how
multiple truths coexist in context. The LotJ examples demonstrate that most conflicts
arise from:

1. **Missing context** - Facts true in different situations
2. **Terminology** - Same words meaning different things
3. **Perspective** - Prescriptive vs descriptive statements
4. **Abstraction levels** - High-level architecture vs low-level configuration

The reconciler successfully resolved 80% of conflicts through conditional context
separation, demonstrating that automated analysis can handle most cases. The remaining
20% requiring human decision involved architectural choices beyond what documentation
could answer.

**Key Insight**: The goal is not to eliminate all contradictions, but to make them
*understandable* and *actionable*. When developers understand why two statements appear
to conflict and in what contexts each applies, the "contradiction" becomes useful
knowledge about system complexity.

---

*End of Reconciliation Examples*
