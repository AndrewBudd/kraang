# LotJ Constraint Catalog
**Generated**: 2026-02-10
**Total Constraints**: 110

This catalog lists all extracted constraints from the LotJ codebase. Constraints
represent hard requirements and rules that MUST be followed.

---

## Table of Contents

1. [Development Workflow](#development-workflow)
2. [Code Standards](#code-standards)
3. [Memory Management](#memory-management)
4. [Header File Organization](#header-file-organization)
5. [Git and Version Control](#git-and-version-control)
6. [Communication and Chat](#communication-and-chat)
7. [Room Restrictions](#room-restrictions)
8. [Command Permissions](#command-permissions)
9. [System Limits](#system-limits)
10. [Error Handling](#error-handling)
11. [Security](#security)
12. [Other Constraints](#other-constraints)

---

## Development Workflow

**Count**: 3

### 1. fact_2

**Statement**: Local development MUST use Docker Compose exclusively, never build or run services directly in local environment

**Source**: artifact_1 (Lines 7-15, Section: IMPORTANT: Docker-First Development)

### 2. fact_8

**Statement**: Docker-compose down MUST be avoided in normal development as it forces database rebuild taking 10+ minutes

**Source**: artifact_1 (Lines 148-153, Section: Development Workflow - Database Initialization Warning)

### 3. fact_573

**Statement**: Default test credentials for local development are username 'legend' and password 'password'

**Source**: artifact_167 (Default Credentials section)

---

## Code Standards

**Count**: 4

### 1. fact_12

**Statement**: C function naming convention is snake_case

**Source**: artifact_1 (Line 205, Section: C Code Conventions)

### 2. fact_14

**Statement**: Constants MUST be named in ALL_CAPS

**Source**: artifact_1 (Line 207, Section: C Code Conventions)

### 3. fact_15

**Statement**: No compiler warnings are acceptable - all builds MUST be clean

**Source**: artifact_1 (Line 209, Section: C Code Conventions)

### 4. fact_398

**Statement**: AIX compiler has bugs with short types, requiring special handling

**Source**: artifact_169 (Lines 24-40, AIX-specific typedef section)

---

## Memory Management

**Count**: 11

### 1. fact_28

**Statement**: The MUD uses a custom memory management system - never use raw malloc/free

**Source**: artifact_1 (Line 262, Section: Memory Management)

### 2. fact_29

**Statement**: CREATE(result, type, number) macro MUST be used to allocate memory for number items of type

**Source**: artifact_1 (Lines 264-267, Section: Memory Management)

### 3. fact_30

**Statement**: DISPOSE(pointer) macro MUST be used to free memory and set pointer to NULL

**Source**: artifact_1 (Lines 269-271, Section: Memory Management)

### 4. fact_32

**Statement**: Never use raw malloc(), free(), calloc(), realloc(), or str_dup()

**Source**: artifact_1 (Line 279, Section: Memory Management)

### 5. fact_33

**Statement**: Raw strdup() should only be used when SET_STRING is unsafe

**Source**: artifact_1 (Line 281, Section: Memory Management)

### 6. fact_199

**Statement**: After x64 transition, the far right memory address no longer works when passed directly into addr2line due to Linux's address space randomization

**Source**: artifact_164 (How to use backtraces (The new way) - paragraph after example backtrace)

### 7. fact_264

**Statement**: Memory allocation MUST use CREATE macro instead of malloc directly

**Source**: artifact_165 (Lines 305-316, CREATE macro definition)

### 8. fact_265

**Statement**: Memory deallocation MUST use DISPOSE macro which sets pointer to NULL after freeing

**Source**: artifact_165 (Line 333, DISPOSE macro definition)

### 9. fact_266

**Statement**: String allocation MUST use STRALLOC macro (str_dup function)

**Source**: artifact_165 (Line 335, STRALLOC macro definition)

### 10. fact_267

**Statement**: String deallocation MUST use STRFREE macro

**Source**: artifact_165 (Line 337, STRFREE macro definition)

### 11. fact_286

**Statement**: String setting MUST use SET_STRING macro which frees existing string before allocating new one

**Source**: artifact_165 (Lines 373-377, SET_STRING macro definition)

---

## Header File Organization

**Count**: 7

### 1. fact_16

**Statement**: DO NOT create new header files, use existing well-established header file structure

**Source**: artifact_1 (Line 213, Section: Header Files - CRITICAL)

### 2. fact_20

**Statement**: ALL new struct definitions MUST be placed in types.h

**Source**: artifact_1 (Line 229, Section: Core Headers)

### 3. fact_22

**Statement**: ALL new function declarations MUST be placed in functions.h

**Source**: artifact_1 (Line 233, Section: Core Headers)

### 4. fact_24

**Statement**: Most files should include mud.h first, then types.h, then other headers as needed

**Source**: artifact_1 (Line 248, Section: Header Inclusion Rules)

### 5. fact_25

**Statement**: functions.h is typically included last for function prototypes

**Source**: artifact_1 (Line 249, Section: Header Inclusion Rules)

### 6. fact_26

**Statement**: Struct definitions MUST go in types.h

**Source**: artifact_1 (Line 254, Section: Content Placement Guidelines)

### 7. fact_27

**Statement**: Function prototypes MUST go in functions.h

**Source**: artifact_1 (Line 255, Section: Content Placement Guidelines)

---

## Git and Version Control

**Count**: 6

### 1. fact_149

**Statement**: Submodule changes must never be staged, committed, or added for directories: area/, data/, template/, looms/, src/lua/

**Source**: artifact_148 (Title and first section '⚠️ CRITICAL: Never Stage Submodule Changes')

### 2. fact_151

**Statement**: Staging submodule changes can create merge conflicts

**Source**: artifact_148 (Section 'Why?' - bullet point 1)

### 3. fact_152

**Statement**: Staging submodule changes can point to wrong commits in other repositories

**Source**: artifact_148 (Section 'Why?' - bullet point 2)

### 4. fact_153

**Statement**: Staging submodule changes can break the build for other developers

**Source**: artifact_148 (Section 'Why?' - bullet point 3)

### 5. fact_154

**Statement**: Staging submodule changes can cause deployment issues

**Source**: artifact_148 (Section 'Why?' - bullet point 4)

### 6. fact_156

**Statement**: The command 'git add area data template looms src/lua' must never be executed

**Source**: artifact_148 (Section 'What to do instead:' - never do command example)

---

## Communication and Chat

**Count**: 6

### 1. fact_86

**Statement**: BEEP command cannot be used in ROOM_SILENCE flagged rooms unless user is RPC

**Source**: artifact_78 (Lines 300-304, do_beep() silence check)

### 2. fact_104

**Statement**: WHISPER command requires characters to be within proximity using is_near() check

**Source**: artifact_78 (Lines 3401-3406, do_whisper() proximity check)

### 3. fact_116

**Statement**: OOC and NEWBIE channels strip color codes before transmission and limit message length to 254 characters for non-immortals

**Source**: artifact_78 (Lines 1456-1472, do_ooc() and do_newbiechat() color stripping)

### 4. fact_124

**Statement**: CLAN MESSAGE requires clan leadership or 'clan_message' bestowment to send inter-clan communications

**Source**: artifact_78 (Lines 4374-4379, do_clan_message() authorization check)

### 5. fact_125

**Statement**: Planet talk requires clan ownership of planet (governed_by) and comlink possession

**Source**: artifact_78 (Lines 4467-4480, do_planet_talk() planet ownership check)

### 6. fact_440

**Statement**: Maximum channels is 42 (CHANNEL_LPROG + 1)

**Source**: artifact_169 (Lines 846-852, channels_enum with MAX_CHANNEL)

---

## Room Restrictions

**Count**: 2

### 1. fact_112

**Statement**: Characters can only quit in ROOM_HOTEL flagged rooms unless they are RPC or unauthorized

**Source**: artifact_78 (Lines 3703-3710, do_quit() hotel room check)

### 2. fact_123

**Statement**: Mental connections are blocked by ROOM_NO_MAGIC flag or PCFLAG_NO_SENSE on either participant

**Source**: artifact_78 (Lines 4616-4619, do_mindtalk() blocking conditions)

---

## Command Permissions

**Count**: 17

### 1. fact_107

**Statement**: Learning a language costs 5 credits and requires ACT_SCHOLAR NPC in room

**Source**: artifact_78 (Lines 4016-4070, do_languages() learning logic)

### 2. fact_118

**Statement**: ORDER command allows controlling charmed NPCs but blocks 'mp' prefixed commands to prevent cheating

**Source**: artifact_78 (Lines 3880-3887, do_order() mp command blocking)

### 3. fact_119

**Statement**: LORRDIAN language is physical/visual and requires line of sight or special abilities to understand

**Source**: artifact_78 (Lines 3034-3047, do_say() Lorrdian visibility check)

### 4. fact_121

**Statement**: RPC members can view player thoughts only if player has thinkrpc flag set to 1

**Source**: artifact_78 (Lines 4596-4602, do_think() RPC viewing restriction)

### 5. fact_251

**Statement**: Bug diagnosis requires exact binary matching - developers must use the exact binary that generated the trace on the server to convert addresses to line numbers

**Source**: artifact_164 (## The files themselves, paragraph 3: 'To do this you will need to be on the server with the exact binary that generated the trace')

### 6. fact_254

**Statement**: After x64 transition, the debugging process requires hex math calculation combining symbol base address from objdump with offset from stack trace due to address space randomization

**Source**: artifact_164 (# How to use backtraces (The new way), paragraph 2-4)

### 7. fact_312

**Statement**: Commands cannot be used from within other commands (subrestricted state check)

**Source**: artifact_165 (Lines 617-625, CHECK_SUBRESTRICTED macro definition)

### 8. fact_345

**Statement**: Multiple test commands reference the same uuid '12345' which could indicate shared state without documented synchronization if executed concurrently

**Source**: artifact_166 (FIREHOSETESTS.md:discordconfirmreply for Legend, immtalk message, ooc message, mortchat, immchat message, rpcto)

### 9. fact_354

**Statement**: No apparent authentication token, signature, or HMAC present in command structure to verify sender authenticity

**Source**: artifact_166 (All command examples (lines 2-32) lack cryptographic authentication fields)

### 10. fact_360

**Statement**: No rate limiting, replay protection, or timestamp validation visible in command structure

**Source**: artifact_166 (All command examples (lines 2-32) lack timestamp or nonce fields)

### 11. fact_364

**Statement**: No error handling patterns are documented for malformed JSON commands

**Source**: artifact_166 (Document-wide: all command examples show valid JSON structure but no invalid cases or error responses)

### 12. fact_367

**Statement**: No error handling specified for missing required fields in command payloads

**Source**: artifact_166 (All command examples show complete payloads but missing field handling not documented)

### 13. fact_369

**Statement**: No error responses or failure modes documented for any command type

**Source**: artifact_166 (Document-wide: only success case examples provided)

### 14. fact_372

**Statement**: No error handling for empty or missing argument fields in commands

**Source**: artifact_166 (!whoami and !who examples show empty argument fields without documented validation)

### 15. fact_375

**Statement**: No validation for commandType field values or enumeration constraints

**Source**: artifact_166 (Examples show 'botcommand' and 'accountcommand' types without validation rules)

### 16. fact_501

**Statement**: Command files must contain one command per line

**Source**: artifact_167 (Command Files section and Troubleshooting section)

### 17. fact_538

**Statement**: Credentials are visible in process listings and command history when passed as arguments

**Source**: artifact_167 (Usage examples throughout showing credentials in command-line arguments)

---

## System Limits

**Count**: 24

### 1. fact_106

**Statement**: Players can learn additional languages up to lang_limit which is (INT/5) + feat bonuses

**Source**: artifact_78 (Lines 4525-4538, lang_limit() function)

### 2. fact_396

**Statement**: XBI is defined as 4 (number of integers in extended bitvector)

**Source**: artifact_169 (Line 522, #define XBI 4)

### 3. fact_397

**Statement**: MAX_BITS is calculated as XBI * INTBITS (4 * 32 = 128 bits)

**Source**: artifact_169 (Line 523, #define MAX_BITS XBI * INTBITS)

### 4. fact_401

**Statement**: Editor buffer has maximum 2048 lines

**Source**: artifact_169 (Line 1629, #define EDITOR_LINES 2048)

### 5. fact_402

**Statement**: Editor line maximum length is 1024 characters excluding formatting codes

**Source**: artifact_169 (Line 1630, #define EDITOR_LINE_CHARS 1024)

### 6. fact_403

**Statement**: Maximum number of conditions (COND_DRUNK, COND_FULL, COND_THIRST, COND_BLOODTHIRST) is 4

**Source**: artifact_169 (Lines 1912-1917, conditions enum with MAX_CONDS)

### 7. fact_404

**Statement**: Maximum wear locations is 24 (WEAR_BACK + 1)

**Source**: artifact_169 (Lines 2539-2544, wear_locations enum with MAX_WEAR)

### 8. fact_406

**Statement**: Maximum directions for normal walking is DIR_SOUTHWEST (10 directions total)

**Source**: artifact_169 (Lines 2857-2859, MAX_DIR definition)

### 9. fact_410

**Statement**: Maximum cargo types is defined by MAX_CARGO_TYPES in cargo_types enum

**Source**: artifact_169 (Lines 1427-1434, cargo_types enum ending with MAX_CARGO_TYPES)

### 10. fact_413

**Statement**: Maximum abilities is 12 (SCIENCE_ABILITY + 1)

**Source**: artifact_169 (Lines 862-867, abilities_enum with MAX_ABILITY)

### 11. fact_418

**Statement**: Maximum vehicle weapons is 8

**Source**: artifact_169 (Line 1299, #define MAX_WEAPONS 8)

### 12. fact_422

**Statement**: Discord content maximum size is 2000 characters

**Source**: artifact_169 (Line 3253, #define DISCORD_CONTENT_MAX_SIZE 2000)

### 13. fact_424

**Statement**: Discord maximum embed length is 4096

**Source**: artifact_169 (Line 3256, #define DISCORD_MAX_EMBED_LENGTH 4096)

### 14. fact_425

**Statement**: Maximum trade types in shop is 5

**Source**: artifact_169 (Line 1075, #define MAX_TRADE 5)

### 15. fact_426

**Statement**: Maximum trap type is TRAP_TYPE_SEX_CHANGE (value 13)

**Source**: artifact_169 (Lines 2325-2329, trap_types enum and MAX_TRAPTYPE)

### 16. fact_437

**Statement**: Maximum apply types is 63 (APPLY_BLOOD value plus one)

**Source**: artifact_169 (Lines 2442-2449, apply_table_enum with MAX_APPLY_TYPE)

### 17. fact_438

**Statement**: Affect data can have up to MAX_VALS values

**Source**: artifact_169 (Line 1868, sh_int value[MAX_VALS] in affect_data)

### 18. fact_439

**Statement**: Language maximum is defined by MAX_LANGUAGE in languages_enum

**Source**: artifact_169 (Lines 890-899, languages_enum ending with MAX_LANGUAGE)

### 19. fact_456

**Statement**: Maximum spice/drug types is 11 (SPICE_MAG_CAT_SPICE + 1)

**Source**: artifact_169 (Lines 2410-2414, drug_types_enum)

### 20. fact_464

**Statement**: Maximum IFs in mob programs is 20

**Source**: artifact_169 (Line 1094, #define MAX_IFS 20)

### 21. fact_465

**Statement**: Maximum program nesting is 20

**Source**: artifact_169 (Line 1097, #define MAX_PROG_NEST 20)

### 22. fact_479

**Statement**: Stack capacity is defined by STACK_CAPACITY constant

**Source**: artifact_169 (Lines 3665-3668, Stack struct with items[STACK_CAPACITY])

### 23. fact_484

**Statement**: Maximum wound locations is 24

**Source**: artifact_169 (Lines 2354-2358, wound_flag_types enum ending with MAX_WOUND)

### 24. fact_485

**Statement**: Maximum medical wound locations is 13

**Source**: artifact_169 (Lines 2348-2350, med_wounds enum ending with MAX_MED)

---

## Error Handling

**Count**: 4

### 1. fact_244

**Statement**: Error handling should check intermediate pointers in a chain before accessing deeply nested members

**Source**: artifact_164 (/home/budda/Code/LotJ/docs/BACKTRACES.md: Code example demonstrating checks like 'ship->in_room->area && ship->in_room->area->planet')

### 2. fact_307

**Statement**: Skill IDs must be validated to be greater than 0 and less than last_skill->id

**Source**: artifact_165 (Line 556, IS_VALID_SN macro definition)

### 3. fact_313

**Statement**: IMM_CHECK macro ensures character is valid, not extracted, not NPC, and has immortal trust level

**Source**: artifact_165 (Lines 369-380, IMM_CHECK macro definition)

### 4. fact_430

**Statement**: BERR (error value) is defined as 255

**Source**: artifact_169 (Lines 26-28, #define BERR 255)

---

## Security

**Count**: 1

### 1. fact_260

**Statement**: All data and code is copyrighted by Legends of the Jedi (1999-2010) with statutory damages up to $5,000 USD per unauthorized use

**Source**: artifact_165 (Lines 19-39, copyright and legal notices)

---

## Other Constraints

**Count**: 25

### 1. fact_13

**Statement**: Global variables MUST be prefixed with 'g_'

**Source**: artifact_1 (Line 206, Section: C Code Conventions)

### 2. fact_36

**Statement**: Always use LINK/UNLINK macros for doubly linked lists, never manually manage next and previous pointer values

**Source**: artifact_1 (Lines 288-290, Section: Linked Lists)

### 3. fact_42

**Statement**: Lua functions typically use camelCase

**Source**: artifact_1 (Line 314, Section: Lua Conventions)

### 4. fact_43

**Statement**: Lua global functions should be avoided

**Source**: artifact_1 (Line 315, Section: Lua Conventions)

### 5. fact_95

**Statement**: Language scrambling is bypassed for immortals at trust level >= 105 or when not morting

**Source**: artifact_78 (Lines 1288-1290, do_talk() immortal bypass)

### 6. fact_96

**Statement**: Characters with RFLAG_STUPID can only form sentences up to 3 words in length

**Source**: artifact_78 (Multiple locations including lines 1100-1104, 1146-1149, sentence length checks)

### 7. fact_97

**Statement**: Characters with INT < 12 can form sentences up to (INT/3)+2 words in length

**Source**: artifact_78 (Multiple locations including lines 1105-1109, 1150-1154, INT-based sentence length checks)

### 8. fact_103

**Statement**: Turbolift access can be restricted by clan membership, rank level, and keycard possession

**Source**: artifact_78 (Lines 3177-3283, turbolift access validation in do_say())

### 9. fact_127

**Statement**: Text color must be in range 0 to txtclr_count-1 or defaults to empty string

**Source**: artifact_78 (Lines 4296-4311, txtclr() validation)

### 10. fact_130

**Statement**: RP points are only saved if player has been online for more than 30 minutes (1800 seconds)

**Source**: artifact_78 (Lines 3678-3692, do_quit() RP point saving logic)

### 11. fact_139

**Statement**: Gagged characters (PCFLAG_GAGGED) produce muffled sounds and cannot communicate clearly

**Source**: artifact_78 (Multiple locations including lines 296-301, 1055-1060, gagged speech restrictions)

### 12. fact_204

**Statement**: Backtrace analysis must be performed on the server with the exact binary that generated the trace

**Source**: artifact_164 (How to use backtraces (the old way) - Using addr2line paragraph)

### 13. fact_223

**Statement**: Backtrace generation from signal handlers is acknowledged as dangerous in async-signal context

**Source**: artifact_164 (BACKTRACES.md - 'doing the stacktrace is also dangerous in the way we are doing it')

### 14. fact_237

**Statement**: Catching crashes and doing stacktrace is dangerous but risks are taken to keep the game up

**Source**: artifact_164 (/home/budda/Code/LotJ/docs/BACKTRACES.md: 'How to use backtraces (the old way)' section, first paragraph)

### 15. fact_248

**Statement**: Game loop prioritizes availability over optimal crash handling performance

**Source**: artifact_164 (# How to use backtraces (the old way) - 'ultimately these are risks we take to try and keep the game up')

### 16. fact_269

**Statement**: Adding more than 32 standard bitvector flags is explicitly forbidden

**Source**: artifact_165 (Line 147, comment '/* 32 USED! DO NOT ADD MORE! SB */')

### 17. fact_319

**Statement**: Discord users are identified by a tag format (username#number)

**Source**: artifact_166 (Discord confirmation examples show 'tag':'Miros#6234')

### 18. fact_420

**Statement**: Cargo price history length is 80

**Source**: artifact_169 (Line 1424, #define CARGO_HISTORY_LENGTH 80)

### 19. fact_421

**Statement**: Counter buckets array has 10 elements

**Source**: artifact_169 (Line 703, #define COUNTER_BUCKETS 10)

### 20. fact_423

**Statement**: Discord ID size is 64 characters

**Source**: artifact_169 (Line 3254, #define DISCORD_ID_SIZE 64)

### 21. fact_428

**Statement**: FALSE is defined as 0

**Source**: artifact_169 (Lines 18-20, #define FALSE 0)

### 22. fact_429

**Statement**: TRUE is defined as 1

**Source**: artifact_169 (Lines 22-24, #define TRUE 1)

### 23. fact_473

**Statement**: Update intervals track execution history with 5-element array

**Source**: artifact_169 (Lines 3397-3399, #define UPDATE_INTERVAL_HISTORY_LENGTH 5 and history_ms array)

### 24. fact_556

**Statement**: Username parameter is required for tool operation

**Source**: artifact_167 (Usage > Command-Line Options, -u USERNAME entry)

### 25. fact_574

**Statement**: Tests should always use default credentials when testing locally to ensure consistent behavior

**Source**: artifact_167 (Default Credentials section, second paragraph)

---

## Summary

Total constraints extracted: **110**

### Distribution by Category

- **Development Workflow**: 3
- **Code Standards**: 4
- **Memory Management**: 11
- **Header File Organization**: 7
- **Git and Version Control**: 6
- **Communication and Chat**: 6
- **Room Restrictions**: 2
- **Command Permissions**: 17
- **System Limits**: 24
- **Error Handling**: 4
- **Security**: 1
- **Other Constraints**: 25

### Key Findings

1. **Memory Management** is heavily constrained with custom macros (CREATE, DISPOSE, SET_STRING)
2. **Header File Organization** is strictly enforced - no new headers allowed
3. **System Limits** are explicitly defined for buffers, arrays, and data structures
4. **Git Workflow** has critical constraints around submodule handling
5. **Development Workflow** mandates Docker-first approach

### Recommendations

1. Create automated checks for constraint violations (linters, pre-commit hooks)
2. Document exception handling for constraints that can be overridden
3. Add constraint validation to CI/CD pipeline
4. Create developer training materials around critical constraints
5. Monitor for constraint violations in code reviews

---

*End of Constraint Catalog*
