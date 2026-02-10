# LotJ System Architecture
**Generated**: 2026-02-10
**Extracted from**: Kraang Knowledge Graph
**Source Artifacts**: 46 files analyzed

---

## Executive Summary

This document describes the system architecture of Legends of the Jedi (LotJ), a
Star Wars-themed MUD (Multi-User Dungeon) game. The architecture has been extracted
from documentation and source code analysis using the Kraang constraint rationalization
engine.

### Architecture Overview

LotJ follows a **monolithic C application** architecture with **Lua scripting extensions**,
running in a **multi-service Docker environment**. The core game engine is written in C,
with game logic implemented in Lua "looms" that extend the core functionality.

---

## 1. High-Level Architecture

### 1.1 System Type
- **Classification**: MUD (Multi-User Dungeon) Game
- **Domain**: Star Wars themed multiplayer RPG
- **Deployment**: Docker Compose multi-service architecture
- **Primary Language**: C (core engine)
- **Scripting Language**: Lua (game logic extensions)
- **Network Protocol**: Telnet (port 5656)

### 1.2 Architectural Style
- **Core Pattern**: Monolithic application with plugin architecture
- **Extension Mechanism**: Lua scripting via "looms"
- **Data Model**: Object-oriented C structs with procedural logic
- **Communication**: Telnet-based text protocol with MQTT for inter-service messaging
- **Persistence**: PostgreSQL database with area file definitions

---

## 2. Service Architecture

### 2.1 Docker Services

LotJ runs as a collection of Docker services defined in docker-compose.yml:

| Service | Purpose | Language | Ports |
|---------|---------|----------|-------|
| **mud** | Core game server | C/Lua | 5656 (telnet), 5666 (firehose), 4444 (debug) |
| **db** | PostgreSQL database | - | 5432 |
| **mosquitto** | MQTT message broker | - | 1883, 9001 |
| **rpcsidecar** | RPC API service | Node.js | 3000 |
| **discord2mqtt** | Discord integration | Node.js | - |
| **lotjwebbuffer** | Web interface | - | 3001 |
| **nginx** | Web server (website profile) | - | 80, 443 |
| **mysql** | MySQL (website profile) | - | 3306 |
| **wordpress** | CMS (website profile) | PHP | - |

### 2.2 Service Communication

```
┌─────────────┐
│   Players   │
│  (Telnet)   │
└──────┬──────┘
       │ Port 5656
       ▼
┌─────────────────┐         ┌──────────────┐
│   MUD Server    │◄────────┤  PostgreSQL  │
│   (C + Lua)     │  SQL    │   Database   │
└────────┬────────┘         └──────────────┘
         │
         │ MQTT Messages
         ▼
┌─────────────────┐         ┌──────────────┐
│   Mosquitto     │◄────────┤  Discord     │
│  MQTT Broker    │  MQTT   │  Integration │
└────────┬────────┘         └──────────────┘
         │
         ├──────►┌──────────────┐
         │       │ RPC Sidecar  │
         │       │  (Node.js)   │
         │       └──────────────┘
         │
         └──────►┌──────────────┐
                 │ Web Buffer   │
                 │   Service    │
                 └──────────────┘
```

---

## 3. Code Architecture

### 3.1 Directory Structure

```
LotJ/
├── src/              # C source code (core game engine)
│   ├── *.c           # ~133 source files
│   ├── *.h           # ~24 header files
│   └── Makefile      # Build configuration
├── looms/            # Lua scripts (game logic extensions)
├── area/             # Game world definitions (.are files)
├── docs/             # Documentation
├── data/             # Runtime data (logs, player files)
│   └── log/          # Server logs
├── backtraces/       # Crash information
├── tools/            # Development tools
│   └── tester/       # Testing framework
├── migrations/       # Database migrations
├── rocksdbs/         # RocksDB database files
├── mosquitto/        # MQTT configuration
├── rpcsidecar/       # RPC service (Node.js)
├── discord2mqtt/     # Discord integration
├── webbuffer/        # Web buffer service
└── www/              # Website files
```

### 3.2 C Code Organization

#### 3.2.1 Header File Hierarchy (Strict Order)

LotJ uses a **well-established header file structure** that MUST NOT be modified:

```
1. mud.h (981 lines)
   ├─ Memory management macros (CREATE, DISPOSE, SET_STRING)
   ├─ Core constants and basic types
   └─ Primary header included by most files

2. const.h (716 lines)
   └─ Constants and #defines only (no types or functions)

3. types.h (5,830 lines) - ALL STRUCT DEFINITIONS
   ├─ CHAR_DATA, OBJ_DATA, ROOM_DATA
   ├─ All game entity structs
   └─ Custom types and enums

4. functions.h (2,437 lines) - ALL FUNCTION PROTOTYPES
   ├─ DECLARE_DO_FUN declarations
   ├─ DECLARE_SPEC_FUN declarations
   └─ External function prototypes

5. globals.h (668 lines)
   └─ Global variable extern declarations only
```

**Specialized Headers**:
- constants.h - File paths and system constants
- sql.h - Database functionality
- fieldmap.h - Database field mapping
- protocol.h - Network protocol definitions
- lua_header.h - Lua integration
- vector3.h, calendar.h, color.h - Domain-specific utilities

#### 3.2.2 Critical Architectural Rules

1. **DO NOT create new header files** - Use existing structure
2. **All new structs → types.h**
3. **All new function prototypes → functions.h**
4. **Include order**: mud.h → types.h → specialized headers → functions.h

### 3.3 Source File Organization

Major source files by subsystem:

**Communication** (~8,863 lines):
- act_comm.c - Chat, speech, channels, colors, tones, languages

**Core Infrastructure** (~30,000+ lines):
- handler.c (7,920 lines) - Object/character handling
- db.c (6,724 lines) - Database operations
- comm.c (8,758 lines) - Communication infrastructure
- update.c (7,776 lines) - Game state updates

**Game Systems** (~90,000+ lines):
- space.c (30,339 lines) - Space combat and navigation
- force.c (9,740 lines) - Force powers system
- fight.c (7,891 lines) - Combat system
- swskills.c (14,651 lines) - Star Wars skills
- build.c (13,290 lines) - World building commands

**Administration** (~25,000+ lines):
- act_wiz.c (15,063 lines) - Wizard/admin commands
- act_info.c (10,396 lines) - Information display
- interp.c (1,948 lines) - Command interpreter

**Total C Codebase**: ~157,000+ lines estimated

---

## 4. Data Architecture

### 4.1 Core Data Structures (types.h)

Key structs defined in types.h:

```c
// Character data (players and NPCs)
struct char_data {
    // Identity and state
    // Skills and abilities
    // Equipment and inventory
    // Position and location
    // Social relationships
};

// Object data (items)
struct obj_data {
    // Object properties
    // Value fields (type-specific)
    // Affects and modifiers
    // Owner and location
};

// Room data (locations)
struct room_data {
    // Room properties and flags
    // Exits and connections
    // Objects and characters present
    // Area and planet references
};

// Area data (world regions)
struct area_data {
    // Area properties
    // Room ranges
    // Reset information
};
```

### 4.2 Memory Management Model

**Custom Memory System** (defined in mud.h):

```c
// Allocation - NEVER use malloc()
CREATE(result, type, number)  // Allocates 'number' items of 'type'

// Deallocation - NEVER use free()
DISPOSE(pointer)  // Frees and sets to NULL

// String management - NEVER use strdup() directly
SET_STRING(pointer, value)  // Safe string assignment
STRALLOC(string)  // Allocate string
STRFREE(pointer)  // Free string
```

**Purpose**: Memory safety, automatic NULL setting, tracking

### 4.3 Linked List Architecture

**Doubly-Linked List System** (macros in mud.h):

```c
// Add to list tail
LINK(node, head, tail, next, prev)

// Remove from list
UNLINK(node, head, tail, next, prev)

// Insert before node
INSERT(node, other, head, next, prev)

// Insert after node
INSERT_AFTER(node, other, tail, next, prev)
```

**Usage**: Character lists, object lists, room contents, etc.

---

## 5. Communication Architecture

### 5.1 Player Communication (act_comm.c)

**Speech System**:
- 30 text colors (txtclr_codes array)
- Custom tones with adverb generation
- 94+ language support with scrambling algorithms
- Drunk speech modifiers
- Profanity filtering (optional per character)

**Channel System**:
```
OOC (Out of Character)
├─ Rate limited (ooclimit system)
├─ Color stripping
└─ 254 char limit for non-immortals

NEWBIE
├─ Color stripping
└─ 254 char limit

IMMTALK/IMPCHAT (Staff channels)
CLANCHAT/CLAN MESSAGE
PLANET TALK
MINDTALK (Mental communication)
```

**Communication Mechanisms**:
- SAY - Local room speech with language scrambling
- YELL - Multi-room transmission (range based on ambience)
- WHISPER - Proximity-based private messages
- EMOTE - Action descriptions with embedded speech
- BEEP - Alert with message
- THINK - Stored thoughts (viewable by RPC if enabled)
- ORDER - Command charmed NPCs (blocks 'mp' exploit)

**Comlink System**:
- Encrypted channels (code values in obj->value[4])
- Broadcast to all players
- GNI Report broadcasts
- Holotransmitter relays
- Microphone relays within star system

### 5.2 Inter-Service Communication

**MQTT Message Broker (Mosquitto)**:
- Publishes channel messages (unless NO_MQTT_OUT flag)
- Receives Discord messages
- Coordinates service communication

**Discord Integration**:
- Sends channel messages (unless NO_DISCORD_OUT flag)
- Format: JSON with commandType, command, arguments
- User identification via tag (username#number)

---

## 6. Extension Architecture (Lua)

### 6.1 Looms System

**Definition**: Lua scripts organized in "looms" for game logic extensions

**Location**: /looms/ directory (auto-loaded)

**Purpose**:
- Implement complex game logic without C recompilation
- Event-driven programming (callbacks)
- Rapid prototyping of features

**Conventions**:
- Functions use camelCase (vs. C's snake_case)
- Avoid global functions
- Callbacks: ch_speech, obj_speech, rp_speech, room_speech

### 6.2 Integration Points

**Lua to C**:
- Lua programs callable from C (ENABLE_LPROGS environment variable)
- C functions exposed to Lua via lua_header.h

**Trigger System**:
- Speech triggers fire Lua and MUD program callbacks in sequence
- Event callbacks for character actions

---

## 7. Database Architecture

### 7.1 PostgreSQL Database

**Connection**:
- Host: localhost:5432
- User: root
- Password: 12345
- Database: lotj

**Purpose**:
- Player data persistence
- Character information
- Thought storage (num1=timestamp, num2=sequence)
- Tone definitions (id, name, category, adverb, adverb2)
- Credit transaction logging (sql_credits_log)

**Fieldmap System** (fieldmap.h):
- Database field mapping layer
- Abstracts SQL operations

### 7.2 Area File System

**Format**: .are files (text-based)

**Purpose**: Game world definitions
- Rooms and their properties
- Objects and spawns
- NPCs and their behaviors
- Exits and connections

**Management**: Git submodules (area/ directory)

---

## 8. Build Architecture

### 8.1 Build System (src/Makefile)

**Targets**:
```
swreality (default) - Main game executable
sandbox             - Sandbox build
staging             - Staging build
codingport          - Coding port build
lotjbuild           - Build server executable
clean               - Clean artifacts
style               - Format code (astyle ANSI style)
```

### 8.2 Compiler Requirements

**Constraints**:
- Zero compiler warnings allowed
- Clean builds mandatory
- ANSI style formatting (via astyle)

### 8.3 Platform Considerations

**AIX Compiler Workarounds** (types.h):
- Special handling for short type bugs
- Platform-specific typedefs

---

## 9. Development Architecture

### 9.1 Docker-First Workflow

**CRITICAL**: All development MUST use Docker Compose

**Workflow**:
```bash
# Build
docker-compose build mud

# Restart only MUD service (RECOMMENDED)
docker-compose restart mud

# AVOID: Full restart (10+ minute DB rebuild)
docker-compose down && docker-compose up -d
```

### 9.2 Testing Architecture

**Testing Tool** (tools/tester/):
- Telnet-based automated testing
- Command file execution
- Response capture
- Docker containerized

**Test Credentials**:
- Username: legend
- Password: password

### 9.3 Debugging Architecture

**Crash Handling**:
- Signal handlers capture crashes
- Backtraces written to /backtraces/ directory
- GDB server on port 4444 (when enabled)
- addr2line for address-to-line conversion

**Logging**:
- Server logs: /data/log/
- Channel-specific logs (flag_value used for filename)
- Speech logging (ROOM_LOGSPEECH flag)

**Debug Modes** (Environment Variables):
- VALGRIND - Memory checking
- FULL_DEBUG - Full debugging
- GDBSERVER - Enable GDB server
- FASTBOOT - Fast boot mode

---

## 10. Security Architecture

### 10.1 Copyright Protection

**Legal Status**:
- Copyright: Legends of the Jedi (1999-2010)
- Statutory damages: Up to $5,000 USD per unauthorized use

### 10.2 Communication Security

**Encryption**:
- Comlink encryption via code values
- Requires matching codes for decryption

**Access Control**:
- Trust levels for immortals (>= 105 bypasses language scrambling)
- RPC member permissions
- Clan leadership requirements
- Rank-based restrictions
- Keycard possession checks

**Anti-Exploit**:
- ORDER command blocks 'mp' prefix (prevents exploit)
- Subrestricted state check (CHECK_SUBRESTRICTED macro)
- Command recursion prevention

### 10.3 Missing Security (Issues Found)

**Discord Integration Gaps** (from FIREHOSETESTS.md):
- No authentication tokens or HMACs visible
- No rate limiting documented
- No replay protection or timestamps
- No error handling for malformed commands
- No validation for commandType fields

---

## 11. System Limits and Constraints

### 11.1 Buffer Limits

| Constant | Value | Purpose |
|----------|-------|---------|
| EDITOR_LINES | 2048 | Max editor buffer lines |
| EDITOR_LINE_CHARS | 1024 | Max line length (excluding formatting) |
| DISCORD_CONTENT_MAX_SIZE | 2000 | Discord message max |
| DISCORD_MAX_EMBED_LENGTH | 4096 | Discord embed max |
| STACK_CAPACITY | (defined) | Stack size limit |

### 11.2 Game System Limits

| Constant | Value | Purpose |
|----------|-------|---------|
| MAX_BITS | 128 | Extended bitvector size (XBI * INTBITS) |
| XBI | 4 | Extended bitvector integers |
| MAX_CONDS | 4 | Condition types (drunk, full, thirst, bloodthirst) |
| MAX_WEAR | 24 | Wear locations |
| MAX_DIR | 10 | Normal walking directions |
| MAX_ABILITY | 12 | Character abilities |
| MAX_WEAPONS | 8 | Vehicle weapons |
| MAX_CHANNEL | 42 | Communication channels |
| MAX_LANGUAGE | (enum) | Language count (94+ documented) |
| MAX_TRADE | 5 | Shop trade types |
| MAX_TRAPTYPE | 13 | Trap types |
| MAX_APPLY_TYPE | 63 | Affect application types |
| MAX_WOUND | 24 | Wound locations |
| MAX_MED | 13 | Medical wound locations |
| MAX_IFS | 20 | Mob program IFs |
| MAX_PROG_NEST | 20 | Program nesting depth |
| CARGO_HISTORY_LENGTH | 80 | Price history tracking |
| COUNTER_BUCKETS | 10 | Performance counter buckets |

### 11.3 Bitvector Constraint

**CRITICAL**: Adding more than 32 standard bitvector flags is **EXPLICITLY FORBIDDEN**
(mud.h line 147 comment)

---

## 12. Architectural Patterns

### 12.1 Core Patterns

1. **Macro-Based Abstraction**
   - Memory management via macros
   - Linked list operations via macros
   - Type checking via macros (IS_VALID_SN, IMM_CHECK)

2. **Flag-Based State Management**
   - Room flags (ROOM_SILENCE, ROOM_HOTEL, ROOM_NO_MAGIC, ROOM_LOGSPEECH, ROOM_COMMSHIELD)
   - Character flags (PCFLAG_GAGGED, PCFLAG_CENSOR, PCFLAG_NO_SENSE, PCFLAG_SCREENREADER, RFLAG_STUPID)
   - Channel flags (CHANNEL_GNI, CHANNEL_THINK)
   - Act flags (ACT_SCHOLAR for language learning)

3. **String Table Pattern**
   - txtclr_codes[] and txtclr_names[] parallel arrays
   - Language name tables
   - Profanity filter tables (ignore_table, curse_table)

4. **Callback System**
   - Speech callbacks: ch_speech, obj_speech, rp_speech, room_speech
   - Event-driven Lua integration

5. **Proxy Pattern**
   - Disguise system (text color/tone per character OR disguise)
   - Active comlink pointer (curr_comlink)

### 12.2 Anti-Patterns and Technical Debt

1. **Dangerous Signal Handling**
   - Backtrace generation in async-signal context (acknowledged as dangerous)
   - Trade-off: Keep game up vs. crash safety

2. **Weak Input Validation**
   - Discord integration lacks authentication/rate limiting
   - Command type validation not documented

3. **Global State**
   - Static pointers for list heads/tails
   - Global variables (g_ prefix convention)

4. **Magic Numbers**
   - Some hardcoded values (180 seconds for RP save threshold)
   - Channel message lengths (254 chars for non-immortals)

---

## 13. Scalability and Performance

### 13.1 Performance Monitoring

**Update Intervals**:
- History tracking: 5-element array (UPDATE_INTERVAL_HISTORY_LENGTH)
- Execution time monitoring

**Counter System**:
- 10 counter buckets for performance metrics

### 13.2 Scalability Constraints

**Single-Process Architecture**:
- Monolithic C application (not distributed)
- Telnet connections to single server process

**Database Bottlenecks**:
- PostgreSQL initialization: 10+ minutes
- Recommendation: Never restart DB in development

**Memory Management**:
- Custom allocator (not thread-safe by design)
- Linked list macros assume single-threaded access

---

## 14. Architecture Quality Assessment

### 14.1 Strengths

1. **Clear Separation of Concerns**
   - Strict header file organization
   - Dedicated subsystems (communication, combat, space, etc.)

2. **Memory Safety**
   - Custom memory management prevents leaks
   - Automatic NULL setting on deallocation

3. **Extension Architecture**
   - Lua integration allows rapid prototyping
   - Event callback system is flexible

4. **Service Isolation**
   - Docker Compose enables independent service management
   - MQTT decouples communication

5. **Domain Modeling**
   - Rich struct hierarchy (CHAR_DATA, OBJ_DATA, ROOM_DATA)
   - Flag-based state management is expressive

### 14.2 Weaknesses

1. **Monolithic Codebase**
   - 157,000+ lines in single application
   - High coupling between subsystems

2. **Limited Concurrency**
   - Single-threaded design
   - No parallel processing of game logic

3. **Technical Debt**
   - AIX compiler workarounds suggest old codebase
   - Dangerous signal handling acknowledged but accepted

4. **Security Gaps**
   - Discord integration lacks authentication
   - No documented rate limiting

5. **Testing Coverage**
   - Limited automated testing infrastructure
   - Heavy reliance on manual testing

### 14.3 Architectural Risks

**High Risk**:
- Database restart causes 10+ minute downtime
- Signal handler crashes could corrupt game state
- Memory corruption from macro misuse

**Medium Risk**:
- Header file constraint violations could break builds
- Submodule staging could break deployments
- Linked list macro misuse could corrupt data structures

**Low Risk**:
- Compiler warning accumulation (prevented by CI)
- Lua script errors (isolated from C engine)

---

## 15. Evolution Recommendations

### 15.1 Short-Term Improvements

1. Add authentication to Discord integration
2. Implement rate limiting on communication channels
3. Add automated constraint validation (pre-commit hooks)
4. Improve error handling documentation
5. Add unit tests for critical subsystems

### 15.2 Medium-Term Refactoring

1. Extract subsystems into shared libraries
2. Add thread safety to memory management
3. Implement connection pooling for database
4. Add metrics collection and monitoring
5. Create API documentation from function prototypes

### 15.3 Long-Term Architecture Evolution

1. Consider microservices for isolated subsystems (space, combat)
2. Evaluate event sourcing for game state management
3. Add horizontal scaling capabilities
4. Modernize to C11/C17 standards
5. Consider hybrid Rust modules for safety-critical code

---

## 16. Conclusion

LotJ demonstrates a **well-structured monolithic MUD architecture** with clear
patterns and strict organizational rules. The codebase shows maturity in its
memory management, header organization, and extension mechanisms.

**Key Architectural Principles**:
1. Strict header file hierarchy (no new headers)
2. Custom memory management (never raw malloc/free)
3. Macro-based abstractions for common patterns
4. Docker-first development workflow
5. Lua extensions for game logic flexibility

**Critical Constraints**:
- Zero compiler warnings
- All structs in types.h
- All function prototypes in functions.h
- Docker Compose for all development
- Custom memory macros exclusively

The architecture prioritizes **game availability** over perfect crash handling,
**developer productivity** via Lua extensions, and **code organization** through
strict header file rules.

With 157,000+ lines of C code across 133 source files, the system is substantial
but well-organized. Future work should focus on improving test coverage, adding
security hardening to integrations, and considering selective modernization of
critical subsystems.

---

*End of Architecture Document*
