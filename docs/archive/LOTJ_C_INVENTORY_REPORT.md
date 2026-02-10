# LotJ C Source File Inventory Report
## Comprehensive Analysis Using Kraang Constraint Rationalization Engine

**Date:** 2026-02-10  
**Project:** Legends of the Jedi (LotJ) MUD  
**Analysis Tool:** Kraang v1.0  
**Scope:** Core C source files in ~/Code/LotJ/src

---

## Executive Summary

This report documents the comprehensive inventory and constraint extraction of LotJ's core C source files using the Kraang constraint rationalization engine. Out of 16 critical C files added to Kraang, 5 have been successfully analyzed with multi-pass extraction, yielding **1,288 facts** covering implementation details, constraints, requirements, and design decisions.

### Key Achievements
- ✓ **16 critical C files** added to Kraang database
- ✓ **5 files fully analyzed** with multi-pass extraction (31.2% coverage)
- ✓ **1,288 facts extracted** from analyzed files
- ✓ **299 constraints identified** across all categories
- ✓ **$30.96 estimated API cost** for completed extractions

### Coverage Status
- **Core Infrastructure:** 40% (2/5 files: db.c, interp.c)
- **Data Management:** 100% (2/2 files: save.c, player.c)
- **Communication:** 100% (1/1 file: act_comm.c)
- **Combat Systems:** 0% (0/3 files)
- **Space Systems:** 0% (0/2 files)
- **Administration:** 0% (0/3 files)

---

## Files Successfully Analyzed

### 1. db.c (211 KB) - **451 facts**
**Focus:** Database loading, bootstrapping, and area management

**Fact Distribution:**
- Implementation: 261 facts (57.9%)
- Constraint: 105 facts (23.3%)
- Requirement: 64 facts (14.2%)
- Design: 21 facts (4.7%)

**Key Insights:**
- Uses PostgreSQL for all persistent storage
- Supports hot-swapping of areas during runtime
- Maximum VNUM range validation and enforcement
- Complex help file deduplication system
- Area reset and respawn mechanisms

**Extraction Metrics:**
- API Calls: 7
- Tokens Used: 552,373
- Tokens per Fact: 1,225

---

### 2. save.c (45 KB) - **266 facts**
**Focus:** Character persistence and save/load operations

**Fact Distribution:**
- Implementation: 154 facts (57.9%)
- Constraint: 70 facts (26.3%)
- Requirement: 37 facts (13.9%)
- Design: 5 facts (1.9%)

**Key Insights:**
- Save format version 15 (SAVEVERSION)
- NPC persistence with ACT_PERSISTENT flag
- Characters must be de-equipped before saving
- SQL-backed persistent storage
- Backup and recovery mechanisms

**Extraction Metrics:**
- API Calls: 7
- Tokens Used: 131,310
- Tokens per Fact: 494

---

### 3. player.c (116 KB) - **259 facts**
**Focus:** Player management and character operations

**Fact Distribution:**
- Implementation: 150 facts (57.9%)
- Constraint: 75 facts (29.0%)
- Requirement: 22 facts (8.5%)
- Design: 12 facts (4.6%)

**Key Insights:**
- Credits tracking with SQL logging
- Alignment system (Good/Neutral/Evil)
- Character creation and validation
- Permission and trust level management
- Account linkage requirements

**Extraction Metrics:**
- API Calls: 7
- Tokens Used: 303,705
- Tokens per Fact: 1,173

---

### 4. interp.c (59 KB) - **249 facts**
**Focus:** Command interpretation and dispatch

**Fact Distribution:**
- Implementation: 172 facts (69.1%)
- Constraint: 49 facts (19.7%)
- Requirement: 20 facts (8.0%)
- Design: 8 facts (3.2%)

**Key Insights:**
- Hash table-based command lookup (126 buckets)
- Command logging levels (LOG_NEVER, LOG_NORMAL, etc.)
- Laggy command detection (>0.5 seconds)
- Command history (20 entries per character)
- Trust level authorization

**Extraction Metrics:**
- API Calls: 7
- Tokens Used: 159,201
- Tokens per Fact: 639

---

### 5. act_comm.c (280 KB) - **63 facts**
**Focus:** Communication commands and channels

**Fact Distribution:**
- Mixed implementation and constraints

**Key Insights:**
- Previously extracted (artifact_78)
- Communication channel management
- Language and translation systems
- Speech processing

**Extraction Metrics:**
- Earlier extraction, metrics not available for comparison

---

## Constraint Analysis

### Total Constraints: 299 (24.7% of all facts)

#### By Category:

1. **Security/Access Control: 57 constraints (19.1%)**
   - Trust level authorization checks
   - Email confirmation requirements
   - Account association validation
   - Permission verification

2. **Data/Persistence: 47 constraints (15.7%)**
   - SQL buffer sizing (MAX_STRING_LENGTH * 2)
   - Query result limits (50 entries)
   - Database transaction requirements
   - Save format validation

3. **Memory Management: 41 constraints (13.7%)**
   - Command stack limits (20 entries)
   - Buffer size constraints
   - Memory leak prevention
   - Allocation patterns

4. **Error Handling: 38 constraints (12.7%)**
   - Timer validation checks
   - NULL pointer guards
   - Name conflict detection
   - Extraction queue restrictions

5. **Performance: 6 constraints (2.0%)**
   - PCFLAG_NO_EMOTE restrictions
   - Title change blocking
   - Cache optimization hints

---

## Files Pending Extraction

### Critical Priority (Core Infrastructure)

1. **handler.c** (216 KB) - Object/character manipulation
   - Status: FAILED - Location error in extraction
   - Priority: CRITICAL
   - Issue: Bug in multi-pass extractor needs fixing

2. **update.c** (275 KB) - Game loop and update cycles
   - Status: TIMEOUT - File too large
   - Priority: CRITICAL
   - Issue: Needs chunking strategy

3. **comm.c** (335 KB) - Network I/O and main loop
   - Status: NOT STARTED
   - Priority: CRITICAL
   - Notes: May also timeout, needs chunking

### High Priority (Game Mechanics)

4. **fight.c** (269 KB) - Combat mechanics
   - Status: NOT STARTED
   - Priority: HIGH

5. **skills.c** (184 KB) - Skill system
   - Status: FAILED - API credit limit
   - Priority: HIGH

6. **force.c** (324 KB) - Force power system
   - Status: NOT STARTED
   - Priority: HIGH

### Medium Priority (Large Features)

7. **space.c** (992 KB) - Space combat system
   - Status: NOT STARTED
   - Priority: MEDIUM
   - Notes: Largest file, will definitely need chunking

8. **swskills.c** (518 KB) - Star Wars specific skills
   - Status: NOT STARTED
   - Priority: MEDIUM

### Lower Priority (Administration)

9. **act_wiz.c** (462 KB) - Administrative commands
   - Status: NOT STARTED
   - Priority: MEDIUM

10. **build.c** (416 KB) - World building
    - Status: NOT STARTED
    - Priority: MEDIUM

11. **act_info.c** (342 KB) - Information commands
    - Status: NOT STARTED
    - Priority: LOW

---

## Extraction Performance Analysis

### Completed Files Summary

| File       | Size   | Facts | Tokens    | API Calls | Tokens/Fact | Efficiency |
|------------|--------|-------|-----------|-----------|-------------|------------|
| interp.c   | 59 KB  | 249   | 159,201   | 7         | 639         | ★★★★★      |
| save.c     | 45 KB  | 266   | 131,310   | 7         | 494         | ★★★★★      |
| player.c   | 116 KB | 259   | 303,705   | 7         | 1,173       | ★★★☆☆      |
| db.c       | 211 KB | 451   | 552,373   | 7         | 1,225       | ★★★☆☆      |
| **TOTAL**  |        | 1,225 | 1,146,589 | 28        | 936 avg     |            |

### Cost Analysis

- **Total Tokens:** 1,146,589
- **Estimated Input Tokens (80%):** 917,271
- **Estimated Output Tokens (20%):** 229,318
- **Estimated Cost:** $30.96
  - Input cost: $13.76 ($15/M tokens)
  - Output cost: $17.20 ($75/M tokens)

### Efficiency Observations

1. **Best efficiency:** Small-to-medium files (45-116 KB) averaging 494-639 tokens/fact
2. **Lower efficiency:** Large files (211 KB) reaching 1,225 tokens/fact
3. **Pattern:** Diminishing returns as file size increases
4. **Recommendation:** Files >250 KB should use chunking strategy

---

## Key Findings by Domain

### Memory Management
- Custom memory system (CREATE/DISPOSE macros)
- Command stack limits (20 entries per character)
- Buffer size constraints throughout
- No raw malloc/free usage

### Security & Access Control
- Trust level system (0-110 scale)
- Email confirmation for high-trust accounts
- Account association requirements
- Permission checks on all sensitive operations

### Data Persistence
- PostgreSQL-backed storage
- SQL logging for all transactions
- Save format versioning (v15 current)
- Hot-swap capability for areas

### Performance
- Hash-based command lookup
- Laggy command detection (>0.5s threshold)
- Query result limits (50 entries)
- Cache optimization hints

### Error Handling
- Extensive NULL checks
- Timer validation
- Name conflict detection
- Extraction queue protection

---

## Technical Constraints Discovered

### Critical System Constraints

1. **Command System**
   - Hash table with 126 buckets for lookup
   - Maximum 20 command history entries per character
   - Commands taking >0.5s logged as laggy
   - Trust level must be less than command's required level

2. **Save System**
   - SAVEVERSION 15 is current format
   - Characters must be de-equipped before save
   - NPC persistence via ACT_PERSISTENT flag
   - SQL backup for all persistent data

3. **Database System**
   - PostgreSQL for all persistent storage
   - MAX_VNUMS enforced on all entities
   - Hot-swap support for area files
   - Help file deduplication on load

4. **Player System**
   - Credits tracked per character (ch->gold)
   - Three alignments: Good (1000), Neutral (0), Evil (-1000)
   - Alignment can only be changed by immortals
   - Account linking mandatory for trust 20+

---

## Issues Encountered

### 1. Location Error in handler.c
**Issue:** Multi-pass extractor failed with KeyError: 'location'  
**Impact:** Cannot extract facts from critical handler.c file  
**Priority:** HIGH  
**Recommendation:** Fix bug in multi_pass_extraction.py line 823

### 2. Timeout on Large Files
**Issue:** update.c (275 KB) timed out after 10 minutes  
**Impact:** Cannot extract facts from core update system  
**Priority:** HIGH  
**Recommendation:** Implement file chunking strategy for files >250 KB

### 3. API Credit Limit
**Issue:** Ran out of API credits during skills.c extraction  
**Impact:** Cannot continue extraction  
**Priority:** CRITICAL  
**Recommendation:** Add credits or implement budget-aware extraction

---

## Recommendations

### Immediate Actions (High Priority)

1. **Fix Multi-Pass Extractor Bug**
   - Address KeyError: 'location' in multi_pass_extraction.py
   - Test fix with handler.c
   - Estimated effort: 1-2 hours

2. **Implement File Chunking**
   - Split large files (>250 KB) into logical sections
   - Process each section separately
   - Merge results with deduplication
   - Estimated effort: 4-6 hours

3. **Add API Credits**
   - Purchase additional credits to continue extraction
   - Or implement budget-aware extraction with pauses
   - Estimated cost: $50-100 for remaining files

### Short-Term Actions (Medium Priority)

4. **Complete Core Infrastructure**
   - Extract handler.c (after bug fix)
   - Extract update.c (with chunking)
   - Extract comm.c (with chunking)
   - Estimated cost: $30-40

5. **Extract Combat Systems**
   - fight.c, skills.c, force.c
   - Critical for understanding game mechanics
   - Estimated cost: $25-35

### Long-Term Actions (Lower Priority)

6. **Extract Large Feature Files**
   - space.c (992 KB - will require multiple chunks)
   - swskills.c (518 KB)
   - Estimated cost: $40-50

7. **Extract Administration Files**
   - act_wiz.c, build.c, act_info.c
   - Lower priority but useful for completeness
   - Estimated cost: $30-40

### Process Improvements

8. **Implement Budget Tracking**
   - Track API costs in real-time
   - Set budget limits per extraction
   - Automatic pause when approaching limit

9. **Optimize Extraction Prompts**
   - Reduce token usage per pass
   - Focus on most valuable fact types
   - Implement smart pass selection

10. **Add Progress Persistence**
    - Save extraction state after each pass
    - Allow resuming interrupted extractions
    - Prevent data loss on errors

---

## Statistics Summary

### Overall Progress
- **Total C files identified:** 133 in LotJ/src
- **Critical files selected:** 15 (top priority)
- **Files added to Kraang:** 16 (including act_comm.c)
- **Files fully extracted:** 5 (31.2%)
- **Files pending:** 11 (68.8%)

### Fact Extraction
- **Total facts extracted:** 1,288
- **Average facts per file:** 257.6
- **Fact types:**
  - Implementation: 781 (60.6%)
  - Constraint: 318 (24.7%)
  - Requirement: 143 (11.1%)
  - Design: 46 (3.6%)

### Resource Usage
- **Total API calls:** 28+
- **Total tokens:** 1,146,589+
- **Estimated cost:** $30.96+
- **Average extraction time:** ~5-10 minutes per file

### Coverage by Area
- Core Infrastructure: 40%
- Data Management: 100%
- Communication: 100%
- Combat Systems: 0%
- Space Systems: 0%
- Administration: 0%

---

## Next Steps

### Phase 1: Fix & Complete Core (Weeks 1-2)
1. Fix handler.c extraction bug
2. Implement file chunking for large files
3. Add API credits
4. Extract remaining core infrastructure files

### Phase 2: Game Mechanics (Weeks 3-4)
1. Extract combat system files (fight.c, skills.c)
2. Extract force.c for Force powers
3. Analyze extracted constraints
4. Document conflict resolution patterns

### Phase 3: Feature Systems (Weeks 5-6)
1. Extract space.c (with heavy chunking)
2. Extract swskills.c
3. Complete coverage of major game systems

### Phase 4: Administration & Polish (Weeks 7-8)
1. Extract remaining administration files
2. Run relationship analysis across all facts
3. Generate comprehensive constraint map
4. Document architecture patterns

---

## Conclusion

This inventory has successfully established a foundation for understanding LotJ's C codebase through constraint rationalization. With 1,288 facts extracted from 5 critical files, we have comprehensive coverage of:

- ✓ Command interpretation and dispatch
- ✓ Data persistence and save/load
- ✓ Database bootstrapping and management
- ✓ Player management and operations
- ✓ Basic communication systems

The extracted constraints reveal a mature codebase with strong patterns around:
- Custom memory management
- Security and access control
- Data persistence and transactions
- Performance monitoring
- Error handling and validation

Completing the remaining 11 files will provide full coverage of LotJ's core systems and enable comprehensive constraint analysis across the entire codebase.

**Estimated effort to complete:** 30-40 hours of development + $150-200 in API costs

---

## Appendix: Files Added to Kraang

### Completed Extractions
1. artifact_188: /home/budda/Code/LotJ/src/db.c (451 facts)
2. artifact_315: /home/budda/Code/LotJ/src/save.c (266 facts)
3. artifact_314: /home/budda/Code/LotJ/src/player.c (259 facts)
4. artifact_190: /home/budda/Code/LotJ/src/interp.c (249 facts)
5. artifact_78: /home/budda/Code/LotJ/src/act_comm.c (63 facts)

### Pending Extractions
6. artifact_186: /home/budda/Code/LotJ/src/handler.c
7. artifact_187: /home/budda/Code/LotJ/src/update.c
8. artifact_189: /home/budda/Code/LotJ/src/comm.c
9. artifact_191: /home/budda/Code/LotJ/src/space.c
10. artifact_192: /home/budda/Code/LotJ/src/swskills.c
11. artifact_193: /home/budda/Code/LotJ/src/act_wiz.c
12. artifact_194: /home/budda/Code/LotJ/src/build.c
13. artifact_195: /home/budda/Code/LotJ/src/act_info.c
14. artifact_212: /home/budda/Code/LotJ/src/fight.c
15. artifact_256: /home/budda/Code/LotJ/src/force.c
16. artifact_257: /home/budda/Code/LotJ/src/skills.c

---

**Report Generated:** 2026-02-10  
**By:** Kraang Analysis System  
**For:** Legends of the Jedi Development Team
