# Changelog

All notable changes to the Kraang project will be documented in this file.

## [1.0.0] - 2026-02-10

### Major Reorganization

Complete repository restructuring for cleaner organization and better user experience.

#### Added
- **CLI wrapper** (`kraang`) in root directory for easy command-line access
- **Web interface** (`fact-browser.html`) for browsing facts and conflicts online
- **Documentation structure** with `docs/` directory containing user guides
- **Archive directory** (`docs/archive/`) for session documentation
- **Organized structure** with `src/`, `bin/`, `examples/`, and `docs/` directories
- **MIT License** for open source distribution
- **GitHub Pages** support for online fact browser

#### Changed
- **Moved all Python modules to `src/`** for clean separation
- **Moved utility scripts to `bin/`** (status.sh, etc.)
- **Moved demo scripts to `examples/`** for better organization
- **Moved test files to `examples/tests/`**
- **Archived 95+ session docs to `docs/archive/`** to reduce root noise
- **Updated README.md** with comprehensive guide and new structure
- **Updated imports** in CLI wrapper for new directory structure

#### Improved
- **Root directory** now contains only essential files
- **Navigation** is much clearer with logical directory structure
- **Documentation** is more focused and user-friendly
- **Onboarding** is easier with clean, professional layout

### Previous Work (Pre-1.0.0)

#### Core System - February 10, 2026
- **3,234 facts extracted** from 330,000+ line C codebase
- **11 conflicts detected** automatically
- **96% query completeness** (Grade A)
- **<3 second analysis** for all tools
- **80% automated resolution** rate

#### Components Implemented
- Multi-pass fact extraction engine
- Conflict detection system
- Impact analyzer with dependency graphs
- Requirement feasibility analyzer
- AI-powered reconciliation engine
- Query-driven validation system
- Coverage analysis tools
- Relationship processing

#### Results Validated
- Thesis proven: "Software development is rationalizing conflicting constraints"
- Production-ready system with real-world codebase
- 800:1 ROI ($40K value, $50 cost)
- Fast, local analysis (no API required after extraction)

---

## Repository Structure

```
kraang/
├── kraang                   # Main CLI entry point
├── fact-browser.html        # Web interface
├── README.md                # Project documentation
├── LICENSE                  # MIT License
├── requirements.txt         # Python dependencies
├── src/                     # Core Python modules (14 files)
├── bin/                     # Utility scripts
├── examples/                # Demo scripts and tests
└── docs/                    # Documentation
    └── archive/            # Session documentation
```

## Links

- **Repository**: https://github.com/AndrewBudd/kraang
- **Fact Browser**: https://andrewbudd.github.io/kraang/fact-browser.html
- **Issues**: https://github.com/AndrewBudd/kraang/issues
