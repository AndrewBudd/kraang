#!/usr/bin/env python3
"""
Multi-Pass Extraction Strategy for Kraang

This module implements a sophisticated multi-pass extraction system that:
1. Uses specialized prompts to extract different aspects of constraints
2. Deduplicates facts across passes using semantic similarity
3. Detects diminishing returns to optimize API usage
4. Orchestrates the extraction workflow efficiently
"""

import json
import os
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import anthropic
from pathlib import Path
import hashlib
import difflib

# Import new enhancement modules
try:
    from chunking_engine import ChunkingEngine, Chunk
    CHUNKING_AVAILABLE = True
except ImportError:
    CHUNKING_AVAILABLE = False
    print("Warning: chunking_engine not available, large file chunking disabled")

try:
    from cache_manager import CacheManager, CacheConfig, PromptCacheHelper
    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False
    print("Warning: cache_manager not available, caching disabled")

try:
    from pass_selector import PassSelector
    PASS_SELECTION_AVAILABLE = True
except ImportError:
    PASS_SELECTION_AVAILABLE = False
    print("Warning: pass_selector not available, smart pass selection disabled")


class PassType(Enum):
    """Types of extraction passes with different focus areas"""
    GENERAL = "general"
    MEMORY = "memory"
    CONCURRENCY = "concurrency"
    SECURITY = "security"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE = "performance"
    TESTING = "testing"


@dataclass
class ExtractionPass:
    """Configuration for a single extraction pass"""
    pass_type: PassType
    prompt_template: str
    priority: int  # Lower number = higher priority, runs earlier
    expected_fact_types: List[str]


@dataclass
class ExtractedFact:
    """A fact extracted during a pass"""
    statement: str
    type: str
    location: str
    confidence: float
    pass_type: PassType
    keywords: Set[str] = field(default_factory=set)
    statement_normalized: str = ""

    def __post_init__(self):
        """Generate normalized form and keywords for deduplication"""
        # Normalize statement for comparison
        self.statement_normalized = self._normalize_statement(self.statement)
        # Extract keywords
        self.keywords = self._extract_keywords(self.statement)

    def _normalize_statement(self, text: str) -> str:
        """Normalize statement for comparison"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove common punctuation at end
        text = text.rstrip('.,;:')
        return text

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract significant keywords from statement"""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'it', 'its', 'they', 'their', 'them'
        }

        # Split into words and filter
        words = text.lower().split()
        keywords = set()
        for word in words:
            # Remove punctuation
            word = word.strip('.,;:()[]{}"\'-!?')
            # Keep if significant
            if len(word) >= 3 and word not in stop_words:
                keywords.add(word)

        return keywords


@dataclass
class PassResults:
    """Results from a single extraction pass"""
    pass_type: PassType
    facts_extracted: List[ExtractedFact]
    facts_deduplicated: int
    new_unique_facts: int
    api_calls: int
    tokens_used: int


@dataclass
class DeduplicationResult:
    """Result of deduplication analysis"""
    is_duplicate: bool
    similarity_score: float
    matching_fact: Optional[ExtractedFact]
    reason: str


@dataclass
class DiminishingReturnsMetrics:
    """Metrics for tracking diminishing returns"""
    pass_number: int
    new_facts: int
    new_categories: Set[str]
    total_facts: int
    unique_fact_ratio: float  # new_facts / total_existing_facts
    novelty_score: float  # 0.0 - 1.0, based on new categories and unique facts
    should_continue: bool
    reasoning: str


class ExtractionPromptLibrary:
    """Library of specialized extraction prompts"""

    @staticmethod
    def get_general_prompt() -> str:
        """General-purpose extraction to establish baseline"""
        return """You are analyzing a software artifact to extract facts and constraints.

Artifact Type: {artifact_type}
Path: {artifact_path}

Content:
{artifact_content}

Extract all significant facts, constraints, requirements, and implementation details.

Focus on:
- Core requirements and business rules
- Design decisions and architectural constraints
- Implementation patterns and conventions
- Data structures and their invariants
- API contracts and interfaces

For each fact, provide:
1. A clear, concise statement of the fact/constraint
2. The type: requirement, implementation, design, constraint
3. The specific location in the artifact
4. Your confidence level (0.0 to 1.0)

Examples:
- "User authentication must use JWT tokens" (requirement)
- "Database connections are pooled with max size of 100" (implementation)
- "The system must handle 10,000 concurrent users" (constraint)

Return JSON array:
[
  {{
    "statement": "The fact or constraint",
    "type": "requirement|implementation|design|constraint",
    "location": "Specific location",
    "confidence": 0.9
  }}
]

Return ONLY the JSON array."""

    @staticmethod
    def get_memory_prompt() -> str:
        """Memory management specific extraction"""
        return """You are analyzing a software artifact for MEMORY MANAGEMENT constraints.

Artifact Type: {artifact_type}
Path: {artifact_path}

Content:
{artifact_content}

Extract ALL facts related to memory management, allocation, deallocation, and resource lifecycle.

Focus specifically on:
- Memory allocation patterns (malloc, calloc, custom allocators, CREATE macros)
- Memory deallocation requirements (free, custom deallocators, DESTROY macros)
- Memory ownership semantics (who owns, who frees)
- Buffer sizes and bounds constraints
- Memory leak prevention patterns
- Stack vs heap allocation rules
- Memory pool usage
- Reference counting or lifetime management
- Memory limits and quotas

For each fact, provide:
1. Statement focused on memory aspect
2. Type: constraint, implementation, or requirement
3. Specific location
4. Confidence (0.0 to 1.0)

Examples:
- "All memory allocation MUST use CREATE macro, not malloc" (constraint)
- "Strings are stored in hash table with reference counting" (implementation)
- "Memory pool has maximum size of 1MB" (constraint)

Return JSON array with same format as before.
Return ONLY the JSON array."""

    @staticmethod
    def get_concurrency_prompt() -> str:
        """Concurrency and threading specific extraction"""
        return """You are analyzing a software artifact for CONCURRENCY and THREADING constraints.

Artifact Type: {artifact_type}
Path: {artifact_path}

Content:
{artifact_content}

Extract ALL facts related to concurrency, threading, synchronization, and parallel execution.

Focus specifically on:
- Threading model (single-threaded, multi-threaded, thread pool)
- Lock/mutex usage and requirements
- Deadlock prevention strategies
- Race condition protections
- Thread-safety guarantees or requirements
- Atomic operations
- Synchronization primitives (semaphores, barriers, etc.)
- Lock ordering constraints
- Lock-free or wait-free algorithms
- Critical sections and protected resources
- Thread affinity or pinning

For each fact, provide:
1. Statement focused on concurrency aspect
2. Type: constraint, implementation, or requirement
3. Specific location
4. Confidence (0.0 to 1.0)

Examples:
- "Hashtable access must be protected by rwlock" (constraint)
- "System is single-threaded, no locking required" (implementation)
- "Lock acquisition order: global_lock before hashtable_lock" (constraint)

Return JSON array with same format as before.
Return ONLY the JSON array."""

    @staticmethod
    def get_security_prompt() -> str:
        """Security constraints specific extraction"""
        return """You are analyzing a software artifact for SECURITY constraints and requirements.

Artifact Type: {artifact_type}
Path: {artifact_path}

Content:
{artifact_content}

Extract ALL facts related to security, authentication, authorization, data protection, and threat mitigation.

Focus specifically on:
- Authentication mechanisms and requirements
- Authorization rules and access control
- Input validation and sanitization
- Cryptography usage (encryption, hashing, signing)
- Secret/credential management
- Security boundaries and trust zones
- Attack surface and threat vectors
- Secure coding patterns (bounds checking, etc.)
- Security logging and audit requirements
- Privacy constraints (PII, GDPR, etc.)
- Network security (TLS, certificates, etc.)

For each fact, provide:
1. Statement focused on security aspect
2. Type: constraint, requirement, or implementation
3. Specific location
4. Confidence (0.0 to 1.0)

Examples:
- "User passwords must be hashed with bcrypt, minimum 12 rounds" (requirement)
- "All API endpoints require JWT authentication" (constraint)
- "SQL queries use prepared statements to prevent injection" (implementation)

Return JSON array with same format as before.
Return ONLY the JSON array."""

    @staticmethod
    def get_error_handling_prompt() -> str:
        """Error handling patterns extraction"""
        return """You are analyzing a software artifact for ERROR HANDLING patterns and constraints.

Artifact Type: {artifact_type}
Path: {artifact_path}

Content:
{artifact_content}

Extract ALL facts related to error handling, failure modes, recovery, and resilience.

Focus specifically on:
- Error return codes and conventions
- Exception handling patterns
- Error propagation rules
- Failure detection mechanisms
- Recovery and retry strategies
- Graceful degradation requirements
- Error logging and reporting
- Timeout handling
- Resource cleanup on error
- Validation and precondition checking
- Assertion usage and invariant checking
- Fallback behaviors

For each fact, provide:
1. Statement focused on error handling aspect
2. Type: constraint, implementation, or requirement
3. Specific location
4. Confidence (0.0 to 1.0)

Examples:
- "All functions return -1 on error, 0 on success" (constraint)
- "Failed database queries automatically retry up to 3 times" (implementation)
- "System must handle network partitions gracefully" (requirement)

Return JSON array with same format as before.
Return ONLY the JSON array."""

    @staticmethod
    def get_performance_prompt() -> str:
        """Performance constraints extraction"""
        return """You are analyzing a software artifact for PERFORMANCE constraints and requirements.

Artifact Type: {artifact_type}
Path: {artifact_path}

Content:
{artifact_content}

Extract ALL facts related to performance, efficiency, scalability, and resource usage.

Focus specifically on:
- Latency requirements and SLAs
- Throughput requirements (requests/sec, transactions/sec)
- Scalability constraints (max users, max connections)
- Resource limits (CPU, memory, disk, network)
- Algorithmic complexity requirements (O(n), O(log n))
- Caching strategies
- Database query optimization
- Indexing requirements
- Connection pooling
- Batch processing constraints
- Performance monitoring and profiling
- Hot path optimizations

For each fact, provide:
1. Statement focused on performance aspect
2. Type: constraint, requirement, or implementation
3. Specific location
4. Confidence (0.0 to 1.0)

Examples:
- "API response time must be under 100ms for 95th percentile" (requirement)
- "Hash table lookup is O(1) average case" (implementation)
- "System must support 10,000 concurrent connections" (constraint)

Return JSON array with same format as before.
Return ONLY the JSON array."""

    @staticmethod
    def get_testing_prompt() -> str:
        """Testing requirements extraction"""
        return """You are analyzing a software artifact for TESTING requirements and constraints.

Artifact Type: {artifact_type}
Path: {artifact_path}

Content:
{artifact_content}

Extract ALL facts related to testing, verification, validation, and quality assurance.

Focus specifically on:
- Unit testing requirements and coverage goals
- Integration testing strategies
- End-to-end testing requirements
- Test data and fixtures
- Mock/stub usage patterns
- Test isolation requirements
- Continuous integration/deployment constraints
- Code coverage requirements
- Performance testing requirements
- Security testing requirements
- Acceptance criteria
- Test automation requirements

For each fact, provide:
1. Statement focused on testing aspect
2. Type: constraint, requirement, or implementation
3. Specific location
4. Confidence (0.0 to 1.0)

Examples:
- "All public functions must have unit tests with 80% coverage" (requirement)
- "Integration tests run in Docker containers" (implementation)
- "Performance tests must verify sub-100ms latency" (constraint)

Return JSON array with same format as before.
Return ONLY the JSON array."""

    @classmethod
    def get_all_passes(cls) -> List[ExtractionPass]:
        """Get all configured extraction passes in priority order"""
        return [
            ExtractionPass(
                pass_type=PassType.GENERAL,
                prompt_template=cls.get_general_prompt(),
                priority=1,
                expected_fact_types=["requirement", "implementation", "design", "constraint"]
            ),
            ExtractionPass(
                pass_type=PassType.MEMORY,
                prompt_template=cls.get_memory_prompt(),
                priority=2,
                expected_fact_types=["constraint", "implementation"]
            ),
            ExtractionPass(
                pass_type=PassType.CONCURRENCY,
                prompt_template=cls.get_concurrency_prompt(),
                priority=3,
                expected_fact_types=["constraint", "implementation"]
            ),
            ExtractionPass(
                pass_type=PassType.SECURITY,
                prompt_template=cls.get_security_prompt(),
                priority=4,
                expected_fact_types=["constraint", "requirement", "implementation"]
            ),
            ExtractionPass(
                pass_type=PassType.ERROR_HANDLING,
                prompt_template=cls.get_error_handling_prompt(),
                priority=5,
                expected_fact_types=["constraint", "implementation"]
            ),
            ExtractionPass(
                pass_type=PassType.PERFORMANCE,
                prompt_template=cls.get_performance_prompt(),
                priority=6,
                expected_fact_types=["constraint", "requirement"]
            ),
            ExtractionPass(
                pass_type=PassType.TESTING,
                prompt_template=cls.get_testing_prompt(),
                priority=7,
                expected_fact_types=["constraint", "requirement"]
            ),
        ]


class FactDeduplicator:
    """Handles deduplication of facts across multiple passes"""

    # Similarity thresholds
    EXACT_MATCH_THRESHOLD = 0.95
    HIGH_SIMILARITY_THRESHOLD = 0.80
    MODERATE_SIMILARITY_THRESHOLD = 0.65

    @staticmethod
    def compute_similarity(fact1: ExtractedFact, fact2: ExtractedFact) -> float:
        """
        Compute similarity between two facts using multiple signals.

        Returns a score from 0.0 (completely different) to 1.0 (identical).
        """
        # 1. Exact normalized match
        if fact1.statement_normalized == fact2.statement_normalized:
            return 1.0

        # 2. String similarity using SequenceMatcher
        string_similarity = difflib.SequenceMatcher(
            None,
            fact1.statement_normalized,
            fact2.statement_normalized
        ).ratio()

        # 3. Keyword overlap (Jaccard similarity)
        if len(fact1.keywords) == 0 or len(fact2.keywords) == 0:
            keyword_similarity = 0.0
        else:
            intersection = len(fact1.keywords & fact2.keywords)
            union = len(fact1.keywords | fact2.keywords)
            keyword_similarity = intersection / union if union > 0 else 0.0

        # 4. Type match bonus
        type_bonus = 0.1 if fact1.type == fact2.type else 0.0

        # 5. Location similarity (same general area in file)
        location_bonus = 0.05 if fact1.location == fact2.location else 0.0

        # Weighted combination
        # String similarity is primary signal (60%)
        # Keyword overlap is secondary (30%)
        # Type and location are minor signals (10%)
        combined_score = (
            0.60 * string_similarity +
            0.30 * keyword_similarity +
            type_bonus +
            location_bonus
        )

        return min(1.0, combined_score)

    @classmethod
    def find_duplicate(
        cls,
        new_fact: ExtractedFact,
        existing_facts: List[ExtractedFact]
    ) -> DeduplicationResult:
        """
        Check if new_fact is a duplicate of any existing fact.

        Returns DeduplicationResult with details.
        """
        if not existing_facts:
            return DeduplicationResult(
                is_duplicate=False,
                similarity_score=0.0,
                matching_fact=None,
                reason="No existing facts to compare"
            )

        # Find best match
        best_similarity = 0.0
        best_match = None

        for existing_fact in existing_facts:
            similarity = cls.compute_similarity(new_fact, existing_fact)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = existing_fact

        # Determine if it's a duplicate based on threshold
        if best_similarity >= cls.EXACT_MATCH_THRESHOLD:
            return DeduplicationResult(
                is_duplicate=True,
                similarity_score=best_similarity,
                matching_fact=best_match,
                reason=f"Exact match (similarity: {best_similarity:.2f})"
            )
        elif best_similarity >= cls.HIGH_SIMILARITY_THRESHOLD:
            return DeduplicationResult(
                is_duplicate=True,
                similarity_score=best_similarity,
                matching_fact=best_match,
                reason=f"High similarity (similarity: {best_similarity:.2f})"
            )
        else:
            return DeduplicationResult(
                is_duplicate=False,
                similarity_score=best_similarity,
                matching_fact=best_match,
                reason=f"Below threshold (similarity: {best_similarity:.2f}, threshold: {cls.HIGH_SIMILARITY_THRESHOLD:.2f})"
            )

    @staticmethod
    def merge_facts(
        existing_fact: ExtractedFact,
        new_fact: ExtractedFact
    ) -> ExtractedFact:
        """
        Merge two similar facts, combining their information.

        Strategy:
        - Keep the statement with higher confidence
        - Combine keywords
        - Use maximum confidence
        - Track that it came from multiple passes
        """
        # Choose statement with higher confidence
        if new_fact.confidence > existing_fact.confidence:
            merged_statement = new_fact.statement
            merged_type = new_fact.type
        else:
            merged_statement = existing_fact.statement
            merged_type = existing_fact.type

        # Combine keywords
        merged_keywords = existing_fact.keywords | new_fact.keywords

        # Use maximum confidence (more evidence = higher confidence)
        merged_confidence = max(existing_fact.confidence, new_fact.confidence)
        # Boost slightly for having multiple sources
        merged_confidence = min(1.0, merged_confidence + 0.05)

        # Create merged fact
        merged = ExtractedFact(
            statement=merged_statement,
            type=merged_type,
            location=existing_fact.location,  # Keep original location
            confidence=merged_confidence,
            pass_type=existing_fact.pass_type,  # Keep original pass
        )
        merged.keywords = merged_keywords

        return merged


class DiminishingReturnsDetector:
    """Detects when additional extraction passes have diminishing returns"""

    # Thresholds for stopping
    MIN_NEW_FACTS_THRESHOLD = 2  # Stop if fewer than this many new facts
    MIN_NOVELTY_SCORE_THRESHOLD = 0.15  # Stop if novelty drops below this

    @staticmethod
    def compute_metrics(
        pass_number: int,
        new_facts: List[ExtractedFact],
        all_facts: List[ExtractedFact],
        previous_categories: Set[str]
    ) -> DiminishingReturnsMetrics:
        """
        Compute metrics to determine if we should continue extraction.

        Returns metrics with should_continue flag and reasoning.
        """
        # Count new facts
        num_new_facts = len(new_facts)
        total_facts = len(all_facts)

        # Identify new categories (fact types)
        new_categories = set(f.type for f in new_facts)
        truly_new_categories = new_categories - previous_categories

        # Compute unique fact ratio
        if total_facts == 0:
            unique_ratio = 1.0
        else:
            unique_ratio = num_new_facts / total_facts

        # Compute novelty score
        # Factors:
        # 1. Number of new facts (higher is better)
        # 2. New categories discovered (higher is better)
        # 3. Unique ratio (higher is better)

        # Normalize new facts (diminishing returns curve)
        # 10+ new facts = 1.0, 5 facts = 0.5, 1 fact = 0.1
        if num_new_facts >= 10:
            facts_score = 1.0
        elif num_new_facts >= 5:
            facts_score = 0.5 + (num_new_facts - 5) * 0.1
        elif num_new_facts >= 2:
            facts_score = 0.2 + (num_new_facts - 2) * 0.1
        else:
            facts_score = num_new_facts * 0.1

        # New categories score
        category_score = len(truly_new_categories) * 0.2  # 0.2 per new category
        category_score = min(1.0, category_score)

        # Combine scores
        novelty_score = (
            0.60 * facts_score +
            0.25 * category_score +
            0.15 * unique_ratio
        )

        # Decide whether to continue
        should_continue = True
        reasons = []

        # Check thresholds
        if num_new_facts < DiminishingReturnsDetector.MIN_NEW_FACTS_THRESHOLD:
            should_continue = False
            reasons.append(
                f"Only {num_new_facts} new facts (threshold: {DiminishingReturnsDetector.MIN_NEW_FACTS_THRESHOLD})"
            )

        if novelty_score < DiminishingReturnsDetector.MIN_NOVELTY_SCORE_THRESHOLD:
            should_continue = False
            reasons.append(
                f"Low novelty score {novelty_score:.2f} (threshold: {DiminishingReturnsDetector.MIN_NOVELTY_SCORE_THRESHOLD:.2f})"
            )

        # Hard stop after 7 passes (all specialized passes)
        if pass_number >= 7:
            should_continue = False
            reasons.append("Completed all specialized passes")

        # Success reasons if continuing
        if should_continue:
            reasons.append(
                f"{num_new_facts} new facts with novelty score {novelty_score:.2f}"
            )
            if truly_new_categories:
                reasons.append(f"Discovered new categories: {', '.join(truly_new_categories)}")

        reasoning = "; ".join(reasons)

        return DiminishingReturnsMetrics(
            pass_number=pass_number,
            new_facts=num_new_facts,
            new_categories=truly_new_categories,
            total_facts=total_facts,
            unique_fact_ratio=unique_ratio,
            novelty_score=novelty_score,
            should_continue=should_continue,
            reasoning=reasoning
        )


class MultiPassExtractor:
    """
    Orchestrates multi-pass extraction with deduplication and diminishing returns detection.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        max_passes: int = 7,
        enable_diminishing_returns: bool = True,
        budget_api_calls: Optional[int] = None,
        # NEW: Enhancement parameters
        enable_caching: bool = True,
        enable_chunking: bool = True,
        enable_prompt_caching: bool = True,
        chunk_size_lines: int = 80,
        chunk_overlap_pct: float = 0.20,
        # Model selection
        model: str = "claude-sonnet-4-5-20250929"
    ):
        """
        Initialize multi-pass extractor.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            max_passes: Maximum number of passes to run
            enable_diminishing_returns: Stop early if returns diminish
            budget_api_calls: Maximum API calls to make (None = unlimited)
            enable_caching: Enable result caching (default: True)
            enable_chunking: Enable large file chunking (default: True)
            enable_prompt_caching: Use Claude prompt caching API (default: True)
            chunk_size_lines: Target lines per chunk (default: 80)
            chunk_overlap_pct: Overlap percentage between chunks (default: 0.20)
            model: Claude model to use (default: claude-sonnet-4-5-20250929)
                   Options: claude-haiku-4-5-20251001 (cheapest/fastest)
                           claude-sonnet-4-5-20250929 (balanced)
                           claude-opus-4-6 (most capable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model
        self.max_passes = max_passes
        self.enable_diminishing_returns = enable_diminishing_returns
        self.budget_api_calls = budget_api_calls

        self.deduplicator = FactDeduplicator()
        self.detector = DiminishingReturnsDetector()

        # State tracking
        self.all_facts: List[ExtractedFact] = []
        self.pass_results: List[PassResults] = []
        self.total_api_calls = 0
        self.total_tokens_used = 0

        # NEW: Enhancement features
        self.enable_caching = enable_caching and CACHING_AVAILABLE
        self.enable_chunking = enable_chunking and CHUNKING_AVAILABLE
        self.enable_prompt_caching = enable_prompt_caching and CACHING_AVAILABLE
        self.enable_smart_passes = True  # Always enable if available

        # Initialize cache manager
        if self.enable_caching:
            self.cache_manager = CacheManager(CacheConfig())
            self.prompt_helper = PromptCacheHelper()
            print("✓ Caching enabled (result + prompt caching)")
        else:
            self.cache_manager = None
            self.prompt_helper = None

        # Initialize chunking engine
        if self.enable_chunking:
            self.chunking_engine = ChunkingEngine(
                target_lines=chunk_size_lines,
                overlap_pct=chunk_overlap_pct
            )
            print(f"✓ Chunking enabled (target: {chunk_size_lines} lines, overlap: {chunk_overlap_pct:.0%})")
        else:
            self.chunking_engine = None

        # Initialize pass selector
        if self.enable_smart_passes and PASS_SELECTION_AVAILABLE:
            self.pass_selector = PassSelector(min_relevance=0.3)
            print("✓ Smart pass selection enabled (skips irrelevant passes)")
        else:
            self.pass_selector = None

        # Track cache statistics
        self.cache_hits = 0
        self.cache_misses = 0

    def extract_single_pass(
        self,
        artifact_type: str,
        artifact_path: str,
        artifact_content: str,
        extraction_pass: ExtractionPass,
        chunk_id: Optional[str] = None
    ) -> List[ExtractedFact]:
        """
        Run a single extraction pass with a specialized prompt.

        Returns list of extracted facts (before deduplication).
        """
        # NEW: Check result cache first
        if self.cache_manager:
            cache_key = self.cache_manager.result_cache.get_cache_key(
                artifact_content,
                extraction_pass.pass_type.value,
                chunk_id
            )
            cached_facts = self.cache_manager.result_cache.get_cached_results(cache_key)

            if cached_facts:
                self.cache_hits += 1
                # Convert cached dicts back to ExtractedFact objects
                return [
                    ExtractedFact(
                        statement=f['statement'],
                        type=f['type'],
                        location=f['location'],
                        confidence=f['confidence'],
                        pass_type=extraction_pass.pass_type
                    )
                    for f in cached_facts
                ]

        self.cache_misses += 1

        # Format prompt
        formatted_prompt = extraction_pass.prompt_template.format(
            artifact_type=artifact_type,
            artifact_path=artifact_path,
            artifact_content=artifact_content
        )

        # NEW: Use prompt caching if enabled
        if self.enable_prompt_caching and self.prompt_helper:
            system_instructions = "You are a fact extraction expert specializing in software constraints and requirements."

            message = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                system=[{
                    "type": "text",
                    "text": system_instructions,
                    "cache_control": {"type": "ephemeral"}
                }],
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": artifact_content,
                            "cache_control": {"type": "ephemeral"}
                        },
                        {
                            "type": "text",
                            "text": formatted_prompt
                        }
                    ]
                }]
            )
        else:
            # Standard non-cached call
            message = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                messages=[{"role": "user", "content": formatted_prompt}]
            )

        self.total_api_calls += 1
        self.total_tokens_used += message.usage.input_tokens + message.usage.output_tokens

        # Parse response
        response_text = message.content[0].text

        # Extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        try:
            facts_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Try to recover from truncated response
            print(f"  ⚠ JSON parsing failed for {extraction_pass.pass_type.value}, attempting recovery...")
            # Find last complete object
            lines = response_text.split('\n')
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip().endswith('}') or lines[i].strip().endswith('},'):
                    recovered = '\n'.join(lines[:i+1])
                    if recovered.strip().endswith(','):
                        recovered = recovered.rsplit(',', 1)[0]
                    recovered += '\n]'
                    try:
                        facts_data = json.loads(recovered)
                        print(f"  ✓ Recovered {len(facts_data)} facts")
                        break
                    except:
                        continue
            else:
                print(f"  ✗ Could not recover from truncation")
                raise e

        # Convert to ExtractedFact objects
        extracted_facts = []
        for fact_data in facts_data:
            fact = ExtractedFact(
                statement=fact_data["statement"],
                type=fact_data["type"],
                location=fact_data["location"],
                confidence=fact_data.get("confidence", 1.0),
                pass_type=extraction_pass.pass_type
            )
            extracted_facts.append(fact)

        # NEW: Cache the results
        if self.cache_manager:
            cache_key = self.cache_manager.result_cache.get_cache_key(
                artifact_content,
                extraction_pass.pass_type.value,
                chunk_id
            )
            # Convert facts to dicts for caching
            facts_dicts = [
                {
                    'statement': f.statement,
                    'type': f.type,
                    'location': f.location,
                    'confidence': f.confidence
                }
                for f in extracted_facts
            ]
            self.cache_manager.result_cache.cache_results(
                cache_key,
                facts_dicts,
                {
                    'pass_type': extraction_pass.pass_type.value,
                    'artifact_path': artifact_path,
                    'chunk_id': chunk_id
                }
            )

        return extracted_facts

    def deduplicate_and_merge(
        self,
        new_facts: List[ExtractedFact]
    ) -> Tuple[List[ExtractedFact], int]:
        """
        Deduplicate new facts against existing facts and merge similar ones.

        Returns:
            - List of truly new unique facts
            - Count of facts that were deduplicated
        """
        unique_new_facts = []
        deduplicated_count = 0

        for new_fact in new_facts:
            # Check for duplicates
            dedup_result = self.deduplicator.find_duplicate(new_fact, self.all_facts)

            if dedup_result.is_duplicate:
                # Merge with existing fact
                existing_fact = dedup_result.matching_fact
                merged_fact = self.deduplicator.merge_facts(existing_fact, new_fact)

                # Replace existing fact with merged version
                idx = self.all_facts.index(existing_fact)
                self.all_facts[idx] = merged_fact

                deduplicated_count += 1
            else:
                # Truly new fact
                unique_new_facts.append(new_fact)
                self.all_facts.append(new_fact)

        return unique_new_facts, deduplicated_count

    def run_passes(
        self,
        artifact_type: str,
        artifact_path: str,
        artifact_content: str
    ) -> Dict[str, Any]:
        """
        Run multiple extraction passes with orchestration logic.

        Returns comprehensive results including:
        - All extracted facts
        - Per-pass statistics
        - Deduplication metrics
        - Diminishing returns analysis
        - Resource usage
        """
        print(f"\n{'='*70}")
        print(f"Multi-Pass Extraction: {artifact_path}")
        print(f"{'='*70}\n")

        # Get all configured passes
        all_passes = ExtractionPromptLibrary.get_all_passes()

        # NEW: Smart pass selection
        if self.pass_selector:
            # Analyze file and select relevant passes
            pass_relevances = self.pass_selector.select_passes(
                artifact_path,
                artifact_content,
                artifact_type
            )

            # Filter passes to only selected ones
            # Compare by enum value (string) since PassType enums are different objects
            selected_pass_values = {pr.pass_type.value for pr in pass_relevances}
            all_passes = [p for p in all_passes if p.pass_type.value in selected_pass_values]

            print(f"Smart Selection: {len(all_passes)}/{len(ExtractionPromptLibrary.get_all_passes())} passes")
            if len(all_passes) < 7:
                skipped = 7 - len(all_passes)
                print(f"  ℹ Skipping {skipped} low-relevance passes (saves ~${skipped * 0.10:.2f})")

        all_passes.sort(key=lambda p: p.priority)

        # Track categories seen
        seen_categories = set()

        # Run passes
        for pass_idx, extraction_pass in enumerate(all_passes, 1):
            # Check budget
            if self.budget_api_calls and self.total_api_calls >= self.budget_api_calls:
                print(f"\n⚠ API call budget exhausted ({self.budget_api_calls} calls)")
                break

            # Check max passes
            if pass_idx > self.max_passes:
                print(f"\n⚠ Maximum passes reached ({self.max_passes})")
                break

            print(f"Pass {pass_idx}: {extraction_pass.pass_type.value.upper()}")
            print(f"  Focus: {', '.join(extraction_pass.expected_fact_types)}")

            # Extract facts
            print(f"  Extracting...")

            # NEW: Check if chunking is needed
            if self.chunking_engine and self.chunking_engine.needs_chunking(artifact_content):
                print(f"  ℹ File size requires chunking...")
                chunks = self.chunking_engine.get_chunks(artifact_content, artifact_path)
                print(f"  ✓ Split into {len(chunks)} chunks")

                # Extract from each chunk
                raw_facts = []
                for chunk in chunks:
                    chunk_facts = self.extract_single_pass(
                        artifact_type,
                        artifact_path,
                        chunk.content,
                        extraction_pass,
                        chunk_id=chunk.chunk_id
                    )
                    raw_facts.extend(chunk_facts)

                print(f"  ✓ Extracted {len(raw_facts)} raw facts from {len(chunks)} chunks")
            else:
                # Standard single-file extraction
                raw_facts = self.extract_single_pass(
                    artifact_type,
                    artifact_path,
                    artifact_content,
                    extraction_pass
                )
                print(f"  ✓ Extracted {len(raw_facts)} raw facts")

            # Deduplicate
            print(f"  Deduplicating...")
            unique_facts, dedup_count = self.deduplicate_and_merge(raw_facts)
            print(f"  ✓ {len(unique_facts)} new unique facts, {dedup_count} duplicates merged")

            # Record results
            pass_result = PassResults(
                pass_type=extraction_pass.pass_type,
                facts_extracted=len(raw_facts),
                facts_deduplicated=dedup_count,
                new_unique_facts=len(unique_facts),
                api_calls=1,
                tokens_used=0  # Would need to track from API response
            )
            self.pass_results.append(pass_result)

            # Update seen categories
            new_categories = set(f.type for f in unique_facts)
            seen_categories.update(new_categories)

            # Check diminishing returns
            if self.enable_diminishing_returns and pass_idx >= 2:  # Need at least 2 passes
                metrics = self.detector.compute_metrics(
                    pass_number=pass_idx,
                    new_facts=unique_facts,
                    all_facts=self.all_facts,
                    previous_categories=seen_categories - new_categories
                )

                print(f"  Novelty Score: {metrics.novelty_score:.2f}")
                print(f"  {metrics.reasoning}")

                if not metrics.should_continue:
                    print(f"\n✓ Stopping early: diminishing returns detected")
                    break

            print()

        # Summary
        print(f"{'='*70}")
        print(f"EXTRACTION COMPLETE")
        print(f"{'='*70}")
        print(f"Total Passes: {len(self.pass_results)}")
        print(f"Total Facts Extracted: {len(self.all_facts)}")
        print(f"API Calls: {self.total_api_calls}")
        print(f"Tokens Used: {self.total_tokens_used:,}")

        # NEW: Cache statistics
        if self.cache_manager:
            total_checks = self.cache_hits + self.cache_misses
            hit_rate = (self.cache_hits / total_checks * 100) if total_checks > 0 else 0
            print(f"\nCache Statistics:")
            print(f"  Hits: {self.cache_hits}/{total_checks} ({hit_rate:.1f}%)")
            if self.cache_hits > 0:
                print(f"  Estimated savings: ~${self.cache_hits * 0.10:.2f}")

        # Per-pass breakdown
        print(f"\nPer-Pass Breakdown:")
        for result in self.pass_results:
            print(f"  {result.pass_type.value:20s}: "
                  f"{result.facts_extracted:3d} raw -> "
                  f"{result.new_unique_facts:3d} new "
                  f"({result.facts_deduplicated:3d} duplicates)")

        # Category distribution
        print(f"\nFact Categories:")
        category_counts = {}
        for fact in self.all_facts:
            category_counts[fact.type] = category_counts.get(fact.type, 0) + 1
        for category, count in sorted(category_counts.items()):
            print(f"  {category:20s}: {count:3d}")

        # Return comprehensive results
        return {
            "facts": [asdict(f) for f in self.all_facts],
            "total_facts": len(self.all_facts),
            "passes_run": len(self.pass_results),
            "pass_results": [asdict(r) for r in self.pass_results],
            "api_calls": self.total_api_calls,
            "tokens_used": self.total_tokens_used,
            "category_distribution": category_counts
        }


# Example usage and testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python multi_pass_extraction.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Read file
    with open(file_path, 'r') as f:
        content = f.read()

    # Determine type
    path = Path(file_path)
    if path.suffix in ['.c', '.h', '.py', '.js']:
        artifact_type = "code"
    elif path.suffix in ['.md', '.txt']:
        artifact_type = "doc"
    else:
        artifact_type = "unknown"

    # Run multi-pass extraction
    extractor = MultiPassExtractor(
        max_passes=7,
        enable_diminishing_returns=True,
        budget_api_calls=None  # No limit for testing
    )

    results = extractor.run_passes(
        artifact_type=artifact_type,
        artifact_path=file_path,
        content=content
    )

    # Save results
    output_path = Path(".kraang/multi_pass_results.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to {output_path}")
