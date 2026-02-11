#!/usr/bin/env python3
"""
Cache Manager for Kraang

Provides comprehensive caching to reduce API costs and improve speed:
1. Result caching: Cache extracted facts by (file_hash, pass_type)
2. Prompt caching support: Helpers for Claude's prompt caching API

Expected impact:
- Result caching: 50-70% speed improvement on re-runs
- Prompt caching: 70-90% cost reduction on multi-pass extraction
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any
import os


@dataclass
class CacheConfig:
    """Configuration for caching behavior"""
    enable_prompt_cache: bool = True
    enable_result_cache: bool = True
    cache_ttl_days: int = 30
    cache_dir: Path = None  # Will default to .kraang/cache
    auto_cleanup: bool = True

    def __post_init__(self):
        if self.cache_dir is None:
            self.cache_dir = Path(".kraang/cache")


@dataclass
class CacheEntry:
    """A cached result entry"""
    cache_key: str
    facts: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: str
    file_hash: str
    pass_type: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'CacheEntry':
        return CacheEntry(**data)


@dataclass
class CacheStats:
    """Statistics about cache usage"""
    total_entries: int = 0
    size_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0
    last_cleanup: Optional[str] = None

    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)

    @property
    def hit_rate(self) -> float:
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0

    @property
    def cost_savings(self) -> float:
        """Estimate cost savings from cache hits"""
        # Rough estimate: $0.10 per extraction pass
        return self.hit_count * 0.10

    def to_dict(self):
        return {
            'total_entries': self.total_entries,
            'size_bytes': self.size_bytes,
            'size_mb': self.size_mb,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': self.hit_rate,
            'cost_savings_usd': self.cost_savings,
            'last_cleanup': self.last_cleanup
        }


class ResultCache:
    """Cache for extracted facts by (file_hash, pass_type)"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir / "results"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load or initialize metadata
        self.metadata_file = cache_dir / "metadata.json"
        self.stats = self._load_stats()

    def _load_stats(self) -> CacheStats:
        """Load cache statistics"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                return CacheStats(
                    total_entries=data.get('total_entries', 0),
                    size_bytes=data.get('size_bytes', 0),
                    hit_count=data.get('hit_count', 0),
                    miss_count=data.get('miss_count', 0),
                    last_cleanup=data.get('last_cleanup')
                )
            except Exception as e:
                print(f"Warning: Could not load cache metadata: {e}")

        return CacheStats()

    def _save_stats(self):
        """Save cache statistics"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.stats.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache metadata: {e}")

    def get_cache_key(self, file_content: str, pass_type: str, chunk_id: Optional[str] = None) -> str:
        """
        Generate cache key from file content and pass type.

        Args:
            file_content: Content of the file/chunk
            pass_type: Type of extraction pass
            chunk_id: Optional chunk identifier

        Returns:
            Cache key string
        """
        content_hash = hashlib.sha256(file_content.encode()).hexdigest()[:16]

        if chunk_id:
            return f"{content_hash}:{pass_type}:{chunk_id}"
        else:
            return f"{content_hash}:{pass_type}:full"

    def get_cached_results(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve cached facts.

        Args:
            cache_key: Cache key from get_cache_key()

        Returns:
            List of facts if cached, None if cache miss
        """
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            self.stats.miss_count += 1
            self._save_stats()
            return None

        try:
            with open(cache_file, 'r') as f:
                entry_data = json.load(f)
                entry = CacheEntry.from_dict(entry_data)

            self.stats.hit_count += 1
            self._save_stats()

            return entry.facts

        except Exception as e:
            print(f"Warning: Could not load cached results: {e}")
            self.stats.miss_count += 1
            self._save_stats()
            return None

    def cache_results(
        self,
        cache_key: str,
        facts: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ):
        """
        Cache extraction results.

        Args:
            cache_key: Cache key from get_cache_key()
            facts: List of extracted facts
            metadata: Additional metadata (pass info, timestamps, etc.)
        """
        # Extract components from cache_key
        parts = cache_key.split(':')
        file_hash = parts[0]
        pass_type = parts[1] if len(parts) > 1 else "unknown"

        entry = CacheEntry(
            cache_key=cache_key,
            facts=facts,
            metadata=metadata,
            timestamp=datetime.now().isoformat(),
            file_hash=file_hash,
            pass_type=pass_type
        )

        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, 'w') as f:
                json.dump(entry.to_dict(), f, indent=2)

            # Update stats
            self.stats.total_entries = len(list(self.cache_dir.glob("*.json")))
            self.stats.size_bytes = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
            self._save_stats()

        except Exception as e:
            print(f"Warning: Could not cache results: {e}")

    def invalidate_artifact(self, file_hash: str):
        """
        Remove all cache entries for a specific file.

        Args:
            file_hash: SHA256 hash of file content
        """
        removed = 0
        for cache_file in self.cache_dir.glob(f"{file_hash[:16]}:*.json"):
            try:
                cache_file.unlink()
                removed += 1
            except Exception as e:
                print(f"Warning: Could not remove cache file {cache_file}: {e}")

        if removed > 0:
            # Update stats
            self.stats.total_entries = len(list(self.cache_dir.glob("*.json")))
            self.stats.size_bytes = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
            self._save_stats()

        return removed

    def cleanup_old_entries(self, ttl_days: int = 30):
        """
        Remove cache entries older than TTL.

        Args:
            ttl_days: Time-to-live in days

        Returns:
            Number of entries removed
        """
        cutoff_date = datetime.now() - timedelta(days=ttl_days)
        removed = 0

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    entry_data = json.load(f)

                timestamp_str = entry_data.get('timestamp')
                if not timestamp_str:
                    continue

                entry_date = datetime.fromisoformat(timestamp_str)

                if entry_date < cutoff_date:
                    cache_file.unlink()
                    removed += 1

            except Exception as e:
                print(f"Warning: Error processing cache file {cache_file}: {e}")

        if removed > 0:
            # Update stats
            self.stats.total_entries = len(list(self.cache_dir.glob("*.json")))
            self.stats.size_bytes = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
            self.stats.last_cleanup = datetime.now().isoformat()
            self._save_stats()

        return removed

    def clear_all(self):
        """Remove all cache entries"""
        removed = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                removed += 1
            except Exception as e:
                print(f"Warning: Could not remove cache file {cache_file}: {e}")

        # Reset stats
        self.stats = CacheStats()
        self._save_stats()

        return removed


class PromptCacheHelper:
    """Helper for Claude's prompt caching API"""

    @staticmethod
    def wrap_for_caching(content: str, cache_control_type: str = "ephemeral") -> Dict[str, Any]:
        """
        Wrap content for Claude prompt caching.

        Args:
            content: Text content to cache
            cache_control_type: Cache control type (default: "ephemeral")

        Returns:
            Content block with cache control
        """
        return {
            "type": "text",
            "text": content,
            "cache_control": {"type": cache_control_type}
        }

    @staticmethod
    def build_cached_messages(
        system_instructions: str,
        artifact_content: str,
        extraction_prompt: str,
        few_shot_examples: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build message structure optimized for prompt caching.

        Cache order (most reused first):
        1. System instructions (reused across ALL passes)
        2. Few-shot examples (reused across files)
        3. Artifact content (reused across passes for same file)
        4. Extraction prompt (unique per pass)

        Args:
            system_instructions: Base system prompt
            artifact_content: File/chunk content to extract from
            extraction_prompt: Pass-specific extraction prompt
            few_shot_examples: Optional examples to include

        Returns:
            Message structure with cache controls
        """
        content_blocks = []

        # 1. System instructions (CACHE - reused across all passes)
        content_blocks.append(
            PromptCacheHelper.wrap_for_caching(system_instructions)
        )

        # 2. Few-shot examples (CACHE if provided)
        if few_shot_examples:
            content_blocks.append(
                PromptCacheHelper.wrap_for_caching(few_shot_examples)
            )

        # 3. Artifact content (CACHE - reused for multi-pass)
        content_blocks.append(
            PromptCacheHelper.wrap_for_caching(artifact_content)
        )

        # 4. Extraction prompt (NO CACHE - unique per pass)
        content_blocks.append({
            "type": "text",
            "text": extraction_prompt
        })

        return {
            "role": "user",
            "content": content_blocks
        }


class CacheManager:
    """Main cache coordinator"""

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()

        # Initialize cache directory
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize caches
        self.result_cache = ResultCache(self.config.cache_dir)
        self.prompt_helper = PromptCacheHelper()

    def get_stats(self) -> CacheStats:
        """Get current cache statistics"""
        return self.result_cache.stats

    def cleanup(self):
        """Run cleanup operations"""
        if self.config.auto_cleanup:
            removed = self.result_cache.cleanup_old_entries(self.config.cache_ttl_days)
            return removed
        return 0

    def clear_all(self):
        """Clear all caches"""
        return self.result_cache.clear_all()


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python cache_manager.py <command>")
        print("Commands:")
        print("  stats           - Show cache statistics")
        print("  cleanup [days]  - Remove entries older than N days")
        print("  clear           - Clear all cache entries")
        sys.exit(1)

    command = sys.argv[1]

    # Create cache manager
    cache_manager = CacheManager()

    if command == "stats":
        stats = cache_manager.get_stats()
        print("Cache Statistics:")
        print(f"  Total entries: {stats.total_entries}")
        print(f"  Cache size: {stats.size_mb:.2f} MB")
        print(f"  Hit rate: {stats.hit_rate:.1%}")
        print(f"  Hits/Misses: {stats.hit_count}/{stats.miss_count}")
        print(f"  Estimated savings: ${stats.cost_savings:.2f}")
        if stats.last_cleanup:
            print(f"  Last cleanup: {stats.last_cleanup}")

    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        removed = cache_manager.cleanup()
        print(f"Removed {removed} cache entries older than {days} days")

    elif command == "clear":
        removed = cache_manager.clear_all()
        print(f"Cleared {removed} cache entries")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
