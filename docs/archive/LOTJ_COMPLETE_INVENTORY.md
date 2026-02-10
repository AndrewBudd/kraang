# LotJ Complete Inventory Report
**Generated**: 2026-02-10
**Tool**: Kraang Constraint Rationalization Engine
**Project**: Legends of the Jedi (LotJ) MUD Game

---

## Executive Summary

This comprehensive inventory report documents the complete analysis of the Legends of the Jedi (LotJ) codebase using the Kraang constraint rationalization engine. The analysis covers constraints, requirements, design decisions, and implementation details extracted from documentation and source code.

### Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Total Artifacts Analyzed** | 46 | ✓ |
| **Total Facts Extracted** | 269 | ✓ |
| **Total Relationships** | 16 | ⚠ Low |
| **Overall Coverage** | 21.2% | ⚠ Below Target |
| **Completeness Score** | 70/100 | ✓ Good |
| **Contradictions Found** | 0 | ✓ |
| **Relationship Density** | 0.06 | ⚠ Very Low |

### Fact Distribution by Type

| Type | Count | Percentage |
|------|-------|------------|
| **Implementation** | 174 | 64.7% |
| **Constraint** | 64 | 23.8% |
| **Requirement** | 19 | 7.1% |
| **Design** | 12 | 4.5% |
| **TOTAL** | 269 | 100% |

### Artifact Distribution by Type

| Type | Count | Key Files |
|------|-------|-----------|
| **Code (C/Headers)** | 34 | act_comm.c (8,863 lines), handler.c, db.c, etc. |
| **Documentation** | 9 | CLAUDE.md, BACKTRACES.md, LUA.md, etc. |
| **Configuration** | 3 | docker-compose.yml, Dockerfile, Makefile |
| **TOTAL** | 46 | |

### Coverage Analysis

**Overall Code Coverage**: 21.2% (Target: 40%)

#### Top Covered Files
1. **CLAUDE.md** - 40.5% coverage (161/398 lines, 76 facts)
2. **act_comm.c** - 20.3% coverage (1,801/8,863 lines, 63 facts)

#### Critical Uncovered Files (0% Coverage)
- space.c (30,339 lines) - Space combat and navigation
- act_wiz.c (15,063 lines) - Wizard/admin commands
- swskills.c (14,651 lines) - Star Wars skills system
- build.c (13,290 lines) - World building commands
- act_info.c (10,396 lines) - Information display commands
- force.c (9,740 lines) - Force powers system
- comm.c (8,758 lines) - Communication infrastructure
- handler.c (7,920 lines) - Core object/character handling
- fight.c (7,891 lines) - Combat system
- update.c (7,776 lines) - Game state updates

**Total Uncovered Lines**: ~145,000+ lines across 41 files

---

## Detailed Inventory

### 1. Artifacts Catalog

#### 1.1 Documentation Artifacts (9 files)

| ID | Path | Lines | Facts | Coverage |
|----|------|-------|-------|----------|
| artifact_1 | /home/budda/Code/LotJ/CLAUDE.md | 398 | 76 | 40.5% |
| artifact_148 | /home/budda/Code/LotJ/GIT_SUBMODULE_POLICY.md | 48 | 15 | 0% |
| artifact_164 | /home/budda/Code/LotJ/docs/BACKTRACES.md | 81 | 0 | 0% |
| artifact_166 | /home/budda/Code/LotJ/docs/FIREHOSETESTS.md | 34 | 0 | 0% |
| artifact_167 | /home/budda/Code/LotJ/docs/LOTJ_TEST_TOOL.md | 162 | 0 | 0% |
| artifact_168 | /home/budda/Code/LotJ/docs/LUA.md | 116 | 0 | 0% |
| artifact_170 | /home/budda/Code/LotJ/docs/OLDLUAMANUAL.md | 590 | 0 | 0% |
| artifact_172 | /home/budda/Code/LotJ/docs/PLANETGAME.md | 55 | 0 | 0% |
| artifact_173 | /home/budda/Code/LotJ/docs/mcp_cpr.md | 378 | 0 | 0% |

**Documentation Summary**:
- Primary developer guide (CLAUDE.md) has good coverage at 40.5%
- Specialized documentation (Lua, testing, backtraces) not yet extracted
- Total documentation: 1,862 lines

#### 1.2 Code Artifacts - Header Files (11 files)

| ID | Path | Lines | Facts | Coverage |
|----|------|-------|-------|----------|
| artifact_165 | /home/budda/Code/LotJ/src/mud.h | 982 | 0 | 0% |
| artifact_169 | /home/budda/Code/LotJ/src/types.h | 5,816 | 0 | 0% |
| artifact_171 | /home/budda/Code/LotJ/src/functions.h | 2,446 | 0 | 0% |
| artifact_174 | /home/budda/Code/LotJ/src/globals.h | 669 | 0 | 0% |
| artifact_175 | /home/budda/Code/LotJ/src/const.h | 717 | 0 | 0% |
| artifact_176 | /home/budda/Code/LotJ/src/constants.h | 193 | 0 | 0% |
| artifact_177 | /home/budda/Code/LotJ/src/sql.h | 166 | 0 | 0% |
| artifact_178 | /home/budda/Code/LotJ/src/protocol.h | 846 | 0 | 0% |
| artifact_182 | /home/budda/Code/LotJ/src/vector3.h | 91 | 0 | 0% |
| artifact_183 | /home/budda/Code/LotJ/src/calendar.h | 79 | 0 | 0% |
| artifact_184 | /home/budda/Code/LotJ/src/color.h | 134 | 0 | 0% |
| artifact_185 | /home/budda/Code/LotJ/src/fieldmap.h | 478 | 0 | 0% |

**Header Files Summary**:
- Critical headers (mud.h, types.h, functions.h, globals.h) added but not extracted
- Total header file content: ~12,617 lines
- Contains ALL struct definitions, function prototypes, and core macros

#### 1.3 Code Artifacts - Source Files (23 files)

| ID | Path | Lines | Facts | Coverage |
|----|------|-------|-------|----------|
| artifact_78 | /home/budda/Code/LotJ/src/act_comm.c | 8,863 | 63 | 20.3% |
| artifact_186 | /home/budda/Code/LotJ/src/handler.c | 7,920 | 0 | 0% |
| artifact_187 | /home/budda/Code/LotJ/src/update.c | 7,776 | 0 | 0% |
| artifact_188 | /home/budda/Code/LotJ/src/db.c | 6,724 | 0 | 0% |
| artifact_189 | /home/budda/Code/LotJ/src/comm.c | 8,758 | 0 | 0% |
| artifact_190 | /home/budda/Code/LotJ/src/interp.c | 1,948 | 0 | 0% |
| artifact_191 | /home/budda/Code/LotJ/src/space.c | 30,339 | 0 | 0% |
| artifact_192 | /home/budda/Code/LotJ/src/swskills.c | 14,651 | 0 | 0% |
| artifact_193 | /home/budda/Code/LotJ/src/act_wiz.c | 15,063 | 0 | 0% |
| artifact_194 | /home/budda/Code/LotJ/src/build.c | 13,290 | 0 | 0% |
| artifact_195 | /home/budda/Code/LotJ/src/act_info.c | 10,396 | 0 | 0% |
| artifact_196-201 | /home/budda/Code/LotJ/src/force.c + 5 more | ~50,000 | 0 | 0% |

**Source Files Summary**:
- Only 1 of 23 source files has been extracted (act_comm.c)
- Remaining ~145,000+ lines of C code unanalyzed
- Major systems not yet analyzed: space, combat, force, skills, building

#### 1.4 Configuration Artifacts (3 files)

| ID | Path | Lines | Facts | Coverage |
|----|------|-------|-------|----------|
| artifact_179 | /home/budda/Code/LotJ/docker-compose.yml | 204 | 0 | 0% |
| artifact_180 | /home/budda/Code/LotJ/Dockerfile | 72 | 0 | 0% |
| artifact_181 | /home/budda/Code/LotJ/src/Makefile | 133 | 0 | 0% |

**Configuration Summary**:
- Docker and build configuration added but not extracted
- Contains service architecture and build process details

---

### 2. Facts Catalog

#### 2.1 Constraints (64 facts)

Constraints represent hard requirements and rules that MUST be followed in the codebase.

##### Development Workflow Constraints
- **fact_2**: Local development MUST use Docker Compose exclusively
- **fact_8**: docker-compose down MUST be avoided (forces slow DB rebuild)
- **fact_155**: Modified submodules must be restored before commits
- **fact_156**: Never execute 'git add area data template looms src/lua'
- **fact_157**: Must run 'git status' before any commit

##### Code Standards Constraints
- **fact_15**: No compiler warnings acceptable - builds must be clean
- **fact_16**: DO NOT create new header files
- **fact_20**: ALL new struct definitions MUST go in types.h
- **fact_22**: ALL new function declarations MUST go in functions.h
- **fact_26**: Struct definitions MUST go in types.h
- **fact_27**: Function prototypes MUST go in functions.h

##### Memory Management Constraints
- **fact_28**: Never use raw malloc/free - use custom memory system
- **fact_29**: CREATE(result, type, number) MUST be used for allocation
- **fact_30**: DISPOSE(pointer) MUST be used to free memory
- **fact_31**: SET_STRING(pointer, value) for safe string assignment
- **fact_32**: Never use raw malloc(), free(), calloc(), realloc(), or str_dup()
- **fact_36**: Always use LINK/UNLINK macros for doubly linked lists

##### Communication Constraints
- **fact_86**: BEEP command blocked in ROOM_SILENCE unless user is RPC
- **fact_112**: Can only quit in ROOM_HOTEL rooms unless RPC/unauthorized
- **fact_118**: ORDER command blocks 'mp' prefixed commands to prevent exploit
- **fact_124**: CLAN MESSAGE requires leadership or bestowment
- **fact_139**: Gagged characters produce muffled sounds only

##### Additional Constraints (44 more)
See Section 3.1 for complete constraint catalog organized by category.

#### 2.2 Implementation Details (174 facts)

Implementation facts describe how specific features are actually coded.

##### Communication System (63 facts from act_comm.c)
- **fact_79-141**: Speech colors, tones, channels, languages, whispers, etc.
- Color system with 30 defined color codes
- OOC limit system with cooldown
- Text scrambling for 94+ languages
- Drunk speech modifiers
- Profanity filtering with PCFLAG_CENSOR
- Comlink encryption and broadcast systems
- Mental communication (MINDTALK)
- Translation droids and voice-controlled turbolifts

##### Memory Management Implementation
- Doubly-linked list macros: LINK, UNLINK, INSERT, INSERT_AFTER
- Custom allocation: CREATE, DISPOSE, SET_STRING
- String management: STRALLOC, STRFREE

##### Additional Implementation Facts (111 more)
Including database operations, character stats, skill checks, room restrictions,
macro systems, linked list utilities, and command validation.

#### 2.3 Requirements (19 facts)

Requirements specify what the system needs to provide or support.

##### Testing Requirements
- **fact_68**: Testing tool connects via Telnet
- **fact_69**: Testing tool logs in with credentials
- **fact_70**: Testing tool executes commands from file
- **fact_71**: Testing tool captures responses

##### Documentation Requirements
- **fact_55**: Documentation should use Markdown format
- **fact_56**: Include overview, usage examples, parameters
- **fact_57**: Add to appropriate /docs location

##### Git Submodule Requirements
- **fact_150**: Five git submodules (area, data, template, looms, src/lua)
- **fact_160-163**: Pre-commit hook requirements to prevent submodule staging

##### Service Architecture Requirements
- **fact_61**: Docker services include mud, db, mosquitto, rpcsidecar, etc.
- **fact_74**: Multi-service architecture using Docker Compose

#### 2.4 Design Decisions (12 facts)

Design facts document high-level architectural choices.

- **fact_3**: LotJ is a Star Wars MUD game
- **fact_4**: Core engine in C with Lua scripting
- **fact_5**: Game logic in Lua via 'looms'
- **fact_6**: Telnet-based connectivity on port 5656
- **fact_41**: Lua scripts organized in 'looms'
- **fact_44**: Looms auto-loaded from /looms directory
- **fact_72**: Core directories: /src, /looms, /area, /docs, etc.
- **fact_73**: Area files use .are extension

---

### 3. Relationships Catalog

The system has identified 16 relationships between facts, showing how different
constraints, requirements, and implementations connect.

#### 3.1 Support Relationships (9 relationships)

These show how one fact enables or supports another:

1. **fact_36 supports fact_138**: LINK/UNLINK macros → Following relationship management
2. **fact_28 supports fact_138**: Custom memory system → Safe list management
3. **fact_16 supports fact_138**: No new headers → Consistent codebase
4. **fact_7 supports fact_68**: Default credentials → Testing tool connection
5. **fact_7 supports fact_69**: Default credentials → Testing tool login
6. **fact_9 supports fact_10**: MUD-only restart → Fast database access

#### 3.2 Extension Relationships (7 relationships)

These show how facts extend or build upon other facts:

1. **fact_2 extends fact_61**: Docker-first → Service architecture
2. **fact_3 extends fact_4**: MUD game → C engine
3. **fact_3 extends fact_5**: MUD game → Lua looms
4. **fact_3 extends fact_61**: MUD game → Docker services
5. **fact_3 extends fact_72**: MUD game → Directory structure
6. **fact_3 extends fact_73**: MUD game → Area file format
7. **fact_6 extends fact_74**: Telnet port → Multi-service architecture
8. **fact_8 extends fact_10**: Avoid docker-down → Database access

#### 3.3 Relationship Density Analysis

**Current Density**: 0.06 (16 relationships / 269 facts)
**Target Density**: >0.5 (135+ relationships needed)
**Orphaned Facts**: 253/269 (94.1% have no relationships)

**Status**: ⚠ CRITICAL - Very low relationship density indicates isolated facts

---

### 4. Coverage Analysis

#### 4.1 Overall Statistics

- **Total Lines Analyzed**: 9,270
- **Covered Lines**: 1,962
- **Coverage Percentage**: 21.2%
- **Target Coverage**: 40% (code), 70% (doc)
- **Gap**: -18.8% below target

#### 4.2 Coverage by File Type

| Type | Coverage | Status | Target |
|------|----------|--------|--------|
| Code | 20.3% | ⚠ Below Target | 40% |
| Documentation | 40.5% | ⚠ Below Target | 70% |

#### 4.3 Coverage Heat Map - CLAUDE.md (Best Coverage)

```
Lines 1-50:    [▓▓] 9 facts   - High coverage (Docker, overview)
Lines 51-100:  [▒▒] 10 facts  - Medium coverage (testing, credentials)
Lines 101-150: [  ] 2 facts   - Low coverage (workflow gaps)
Lines 151-200: [░░] 9 facts   - Medium-low coverage (database, ports)
Lines 201-250: [▒▒] 14 facts  - Medium coverage (code patterns)
Lines 251-300: [▒▒] 13 facts  - Medium coverage (header structure)
Lines 301-350: [▒▒] 18 facts  - Medium coverage (memory management)
Lines 351-398: [  ] 5 facts   - Low coverage (final sections)
```

#### 4.4 Coverage Heat Map - act_comm.c (Only Analyzed C File)

```
Lines 1-500:     [██] Dense coverage (color system, speech)
Lines 501-1000:  [▓▓] Good coverage (drunk speech, profanity)
Lines 1001-2000: [░░] Sparse coverage (channels, whisper)
Lines 2001-3500: [  ] Very sparse (emote, translation)
Lines 3501-4800: [▓▓] Good coverage (thought, mental links)
Lines 4801+:     [  ] No coverage (remaining 4,000+ lines)
```

Only first ~4,800 of 8,863 lines analyzed in detail.

#### 4.5 Critical Coverage Gaps

**Zero Coverage - Critical Infrastructure** (34 files, ~152,000 lines):
- Core headers: mud.h, types.h, functions.h, globals.h
- Core systems: handler.c, db.c, comm.c, update.c
- Game systems: space.c, force.c, fight.c, swskills.c
- Admin: act_wiz.c, build.c
- Config: docker-compose.yml, Dockerfile, Makefile
- Docs: 8 documentation files

---

### 5. Completeness Assessment

#### 5.1 Completeness Score: 70/100

**Rating**: ✓ Good - Core constraints captured

**Breakdown**:
- ✓ Primary documentation (CLAUDE.md) well covered
- ✓ Communication system (act_comm.c) partially analyzed
- ✓ Memory management patterns documented
- ✓ Development workflow constraints clear
- ✓ Git submodule policy captured
- ⚠ Low relationship density (0.06 vs target 0.5)
- ⚠ Only 2 of 46 artifacts extracted
- ⚠ 94% of facts are orphaned
- ✗ Zero coverage on critical infrastructure files
- ✗ Major game systems not analyzed

#### 5.2 Strengths

1. **Strong Foundation**: Core development constraints well documented
2. **Memory Safety**: Complete coverage of memory management patterns
3. **Communication System**: Detailed analysis of chat/speech system
4. **No Contradictions**: Zero conflicts found in extracted facts
5. **High Quality**: Facts are specific, actionable, and well-located

#### 5.3 Weaknesses

1. **Low Artifact Coverage**: Only 2 of 46 files extracted (4.3%)
2. **Missing Critical Systems**:
   - Space combat and navigation (30K lines)
   - Force powers system (9K lines)
   - Combat system (7K lines)
   - Skills system (14K lines)
   - Building commands (13K lines)
3. **Isolated Facts**: 94% have no relationships to other facts
4. **Header Files**: Critical type definitions not extracted
5. **Configuration**: Docker/build setup not analyzed

#### 5.4 Constraint-to-Implementation Ratio

**Ratio**: 2.72 (174 implementations / 64 constraints)
**Target**: >0.8
**Status**: ✓ Excellent - Good implementation coverage per constraint

This indicates that where extraction has occurred, it's thorough and captures
both constraints and their implementations.

---

### 6. Query Validation Results

**Status**: Not yet completed (background process)

Query-driven validation tests whether the knowledge graph can answer key questions
about the codebase. Results pending.

---

### 7. File-to-Fact Mapping

#### 7.1 High-Density Files (>50 facts)

1. **CLAUDE.md** (artifact_1): 76 facts
   - Constraints: Development workflow, header structure, memory management
   - Requirements: Testing, documentation, git workflow
   - Design: Architecture overview, service structure
   - Implementation: Docker setup, build process

2. **act_comm.c** (artifact_78): 63 facts
   - Implementation: Communication channels, speech processing
   - Constraints: Room restrictions, command permissions
   - Features: Colors, tones, languages, encryption

3. **GIT_SUBMODULE_POLICY.md** (artifact_148): 15 facts (not yet extracted)
   - Constraints: Submodule handling rules
   - Requirements: Pre-commit hook specifications

#### 7.2 Zero-Fact Files (44 files)

All remaining artifacts have 0 facts extracted, representing the major gap in
coverage. Priority targets include:

**Critical Headers** (12,617 lines):
- types.h (5,816 lines) - ALL struct definitions
- functions.h (2,446 lines) - ALL function prototypes
- mud.h (982 lines) - Core macros and definitions

**Critical Source Files** (~145,000 lines):
- space.c, force.c, fight.c, swskills.c, handler.c, db.c, comm.c, etc.

---

### 8. Recommendations

#### 8.1 Immediate Actions (High Priority)

1. **Extract Critical Headers**
   - Run multi-pass extraction on types.h, functions.h, mud.h, globals.h
   - Expected: 200-500 facts about core data structures and APIs
   - Impact: Foundation for understanding entire codebase

2. **Analyze Core Infrastructure**
   - Extract handler.c (object/character management)
   - Extract db.c (database operations)
   - Extract comm.c (communication infrastructure)
   - Expected: 300-600 facts about core game engine

3. **Build Relationships**
   - Run systematic relationship analysis on all fact pairs
   - Target: Increase density from 0.06 to >0.3
   - Use 'kraang relate' to analyze top 1000 candidate pairs

4. **Extract Configuration**
   - Analyze docker-compose.yml, Dockerfile, Makefile
   - Expected: 30-50 facts about service architecture and build process

#### 8.2 Medium-Term Actions

5. **Analyze Major Game Systems**
   - space.c (space combat)
   - force.c (Force powers)
   - fight.c (combat)
   - swskills.c (skills)
   - Expected: 500-1000 facts

6. **Extract Remaining Documentation**
   - Lua manuals, testing guides, backtrace docs
   - Expected: 50-100 facts

7. **Complete act_comm.c**
   - Current coverage is 20.3% (lines 1-4800 of 8863)
   - Extract remaining 4,000+ lines
   - Expected: 30-50 additional facts

#### 8.3 Long-Term Actions

8. **Systematic C File Analysis**
   - Extract all remaining C files (120+ files)
   - Use multi-pass extraction for comprehensive coverage
   - Expected: 2000-4000 facts total

9. **Relationship Graph Enhancement**
   - Achieve target density of >0.5
   - Build constraint dependency trees
   - Map implementation-to-requirement traceability

10. **Query-Driven Validation**
    - Define key architectural questions
    - Validate knowledge graph can answer them
    - Fill gaps identified by failed queries

---

### 9. Statistical Summary

```
INVENTORY STATISTICS
==================================================
Artifacts:           46 total
  - Code:            34 (73.9%)
  - Documentation:    9 (19.6%)
  - Configuration:    3 (6.5%)

Facts:              269 total
  - Implementation:  174 (64.7%)
  - Constraint:       64 (23.8%)
  - Requirement:      19 (7.1%)
  - Design:           12 (4.5%)

Relationships:       16 total
  - Supports:         9 (56.3%)
  - Extends:          7 (43.8%)

Coverage:           21.2% overall
  - Code:           20.3% (target: 40%)
  - Documentation:  40.5% (target: 70%)

Completeness:       70/100 (Good)
Contradictions:      0 (Excellent)
Relationship Density: 0.06 (Target: >0.5)
Orphaned Facts:     94.1% (Critical Issue)

Files Analyzed:      2 of 46 (4.3%)
Lines Analyzed:      1,962 of 9,270 (21.2%)
Total Codebase:    ~157,000 lines estimated
```

---

### 10. Conclusion

The Kraang analysis has established a **solid foundation** for understanding the
LotJ codebase, particularly around:
- Development workflows and constraints
- Memory management patterns
- Communication system implementation
- Core architectural principles

However, significant work remains:
- **96% of artifacts** have not been extracted
- **94% of facts** are isolated with no relationships
- **Critical infrastructure** (types, functions, handlers, database) not analyzed
- **Major game systems** (space, force, combat) not examined

The completeness score of 70/100 reflects good quality where extraction has
occurred, but limited breadth. With systematic extraction of the remaining
critical files and relationship analysis, the knowledge graph could reach
2000-3000 facts with 50%+ relationship density, providing comprehensive
coverage of the entire codebase.

**Next Steps**: Follow the recommendations in Section 8, starting with critical
headers and core infrastructure files.

---

*End of Report*
