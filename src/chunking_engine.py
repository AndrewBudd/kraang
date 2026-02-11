#!/usr/bin/env python3
"""
Chunking Engine for Kraang

Provides semantic chunking of large source code files using AST analysis.
Solves the problem of files >250KB timing out during extraction.
"""

import hashlib
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import tree_sitter_c as tsc
from tree_sitter import Language, Parser, Node


class ChunkingStrategy(Enum):
    """Chunking strategies"""
    SIMPLE_LINES = "simple_lines"  # Fallback: every N lines
    AST_SEMANTIC = "ast_semantic"  # Tree-sitter based function/struct boundaries
    AST_HYBRID = "ast_hybrid"      # AST with overlap regions


@dataclass
class ChunkContext:
    """Context metadata for chunk reconstruction"""
    file_path: str
    total_chunks: int
    chunk_index: int
    imports: List[str]          # File-level imports
    type_definitions: List[str]  # Relevant types
    parent_scope: Optional[str]  # Containing function/class
    file_hash: str              # SHA256 of original file


@dataclass
class Chunk:
    """A semantic chunk of code"""
    chunk_id: str              # "file_hash:chunk_0"
    content: str               # Actual chunk content
    start_line: int
    end_line: int
    context: ChunkContext      # Metadata for reconstruction
    chunk_type: str            # "function", "struct", "class", "module"

    def to_dict(self):
        return {
            **asdict(self),
            'context': asdict(self.context)
        }


class TreeSitterChunker:
    """C/C++ chunking using tree-sitter"""

    def __init__(self, target_lines: int = 80, overlap_lines: int = 16):
        """
        Args:
            target_lines: Target lines per chunk (default: 80)
            overlap_lines: Lines to overlap between chunks (default: 16 = 20%)
        """
        self.target_lines = target_lines
        self.overlap_lines = overlap_lines

        # Initialize tree-sitter C parser
        self.c_language = Language(tsc.language())
        self.parser = Parser(self.c_language)

    def chunk_file(self, content: str, file_path: str) -> List[Chunk]:
        """
        Chunk a C file at semantic boundaries.

        Args:
            content: File content
            file_path: Path to file

        Returns:
            List of semantic chunks with context
        """
        # Parse AST
        tree = self.parser.parse(bytes(content, 'utf8'))
        root = tree.root_node

        # Extract file-level imports and types
        imports = self._extract_imports(root, content)
        type_defs = self._extract_type_definitions(root, content)

        # Compute file hash
        file_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        # Find semantic boundaries (functions, structs, etc.)
        boundaries = self._find_boundaries(root, content)

        # Group boundaries into chunks
        chunk_groups = self._group_boundaries(boundaries, self.target_lines)

        # Create chunks with context and overlap
        chunks = []
        lines = content.split('\n')

        for idx, (start_line, end_line, chunk_type) in enumerate(chunk_groups):
            # Add overlap with previous chunk
            if idx > 0 and start_line >= self.overlap_lines:
                actual_start = start_line - self.overlap_lines
            else:
                actual_start = start_line

            # Extract chunk content
            chunk_lines = lines[actual_start:end_line]
            chunk_content = '\n'.join(chunk_lines)

            # Build context metadata
            context = ChunkContext(
                file_path=file_path,
                total_chunks=len(chunk_groups),
                chunk_index=idx,
                imports=imports,
                type_definitions=type_defs,
                parent_scope=None,  # TODO: Detect parent scope
                file_hash=file_hash
            )

            # Create chunk
            chunk = Chunk(
                chunk_id=f"{file_hash}:chunk_{idx}",
                content=chunk_content,
                start_line=actual_start,
                end_line=end_line,
                context=context,
                chunk_type=chunk_type
            )

            chunks.append(chunk)

        return chunks

    def _extract_imports(self, root: Node, content: str) -> List[str]:
        """Extract #include directives"""
        imports = []

        # Query for preproc_include nodes
        from tree_sitter import Query
        includes_query = Query(self.c_language, """
            (preproc_include) @include
        """)

        captures = includes_query.matches(root)
        for match in captures:
            for node in match[1].values():
                include_text = content[node.start_byte:node.end_byte]
                imports.append(include_text.strip())

        return imports[:10]  # Limit to first 10 to keep context compact

    def _extract_type_definitions(self, root: Node, content: str) -> List[str]:
        """Extract struct/union/enum/typedef declarations"""
        type_defs = []

        # Query for type definition nodes
        from tree_sitter import Query
        type_query = Query(self.c_language, """
            (struct_specifier) @struct
            (union_specifier) @union
            (enum_specifier) @enum
            (type_definition) @typedef
        """)

        captures = type_query.matches(root)
        for match in captures:
            for node in match[1].values():
                # Get just the declaration, not the full definition
                type_text = content[node.start_byte:node.end_byte]
                # Truncate if too long (>200 chars)
                if len(type_text) > 200:
                    type_text = type_text[:200] + "..."
                type_defs.append(type_text.strip())

        return type_defs[:10]  # Limit to first 10

    def _find_boundaries(self, root: Node, content: str) -> List[Tuple[int, int, str]]:
        """
        Find semantic boundaries (functions, structs, etc.)

        Returns:
            List of (start_line, end_line, type) tuples
        """
        boundaries = []

        # Query for top-level constructs
        from tree_sitter import Query
        constructs_query = Query(self.c_language, """
            (function_definition) @function
            (struct_specifier) @struct
            (union_specifier) @union
            (enum_specifier) @enum
            (declaration) @declaration
        """)

        captures = constructs_query.matches(root)

        for match in captures:
            for capture_name, node in match[1].items():
                # Skip nested constructs (only want top-level)
                if node.parent and node.parent.type != 'translation_unit':
                    continue

                start_line = node.start_point[0]
                end_line = node.end_point[0] + 1  # +1 to include last line

                boundaries.append((start_line, end_line, capture_name))

        # Sort by start line
        boundaries.sort(key=lambda x: x[0])

        return boundaries

    def _group_boundaries(self, boundaries: List[Tuple[int, int, str]], target_lines: int) -> List[Tuple[int, int, str]]:
        """
        Group boundaries into chunks of approximately target_lines.

        Keeps complete semantic units together (don't split functions).
        """
        if not boundaries:
            return []

        chunks = []
        current_start = boundaries[0][0]
        current_end = boundaries[0][1]
        current_type = boundaries[0][2]

        for start, end, bound_type in boundaries[1:]:
            boundary_size = end - start
            current_size = current_end - current_start

            # Can we add this boundary to the current chunk?
            if current_size + boundary_size <= target_lines * 1.25:  # Allow 25% overage
                # Yes, extend current chunk
                current_end = end
                current_type = f"{current_type},{bound_type}" if current_type != bound_type else current_type
            else:
                # No, finalize current chunk and start new one
                chunks.append((current_start, current_end, current_type))
                current_start = start
                current_end = end
                current_type = bound_type

        # Add final chunk
        chunks.append((current_start, current_end, current_type))

        return chunks


class SimpleChunker:
    """Fallback chunker for unsupported languages"""

    def __init__(self, lines_per_chunk: int = 100, overlap_lines: int = 20):
        self.lines_per_chunk = lines_per_chunk
        self.overlap_lines = overlap_lines

    def chunk_file(self, content: str, file_path: str) -> List[Chunk]:
        """Simple line-based chunking with overlap"""
        lines = content.split('\n')
        file_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        chunks = []
        total_chunks = int((len(lines) + self.lines_per_chunk - 1) // self.lines_per_chunk)

        for idx in range(total_chunks):
            start_line = int(max(0, idx * self.lines_per_chunk - (self.overlap_lines if idx > 0 else 0)))
            end_line = int(min(len(lines), (idx + 1) * self.lines_per_chunk))

            chunk_lines = lines[start_line:end_line]
            chunk_content = '\n'.join(chunk_lines)

            context = ChunkContext(
                file_path=file_path,
                total_chunks=total_chunks,
                chunk_index=idx,
                imports=[],
                type_definitions=[],
                parent_scope=None,
                file_hash=file_hash
            )

            chunk = Chunk(
                chunk_id=f"{file_hash}:chunk_{idx}",
                content=chunk_content,
                start_line=start_line,
                end_line=end_line,
                context=context,
                chunk_type="block"
            )

            chunks.append(chunk)

        return chunks


class ChunkingEngine:
    """Main interface for chunking"""

    def __init__(self, target_lines: int = 80, overlap_pct: float = 0.20):
        """
        Args:
            target_lines: Target lines per chunk
            overlap_pct: Overlap percentage (0.0 - 1.0)
        """
        overlap_lines = int(target_lines * overlap_pct)

        self.c_chunker = TreeSitterChunker(target_lines, overlap_lines)
        self.simple_chunker = SimpleChunker(target_lines * 1.25, overlap_lines)

        # Language detection map
        self.language_map = {
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.hpp': 'cpp',
        }

    def needs_chunking(self, content: str, max_size_kb: int = 250, max_lines: int = 3000) -> bool:
        """
        Check if content needs chunking.

        Args:
            content: File content
            max_size_kb: Maximum file size before chunking (default: 250KB)
            max_lines: Maximum lines before chunking (default: 3000)

        Returns:
            True if chunking is needed
        """
        size_kb = len(content.encode()) / 1024
        lines = content.count('\n')

        return size_kb > max_size_kb or lines > max_lines

    def get_chunks(self, content: str, file_path: str) -> List[Chunk]:
        """
        Get chunks for a file.

        Automatically selects the appropriate chunker based on file type.

        Args:
            content: File content
            file_path: Path to file

        Returns:
            List of chunks with context
        """
        # Detect language from extension
        ext = Path(file_path).suffix.lower()
        language = self.language_map.get(ext, 'unknown')

        # Select chunker
        if language == 'c' or language == 'cpp':
            try:
                return self.c_chunker.chunk_file(content, file_path)
            except Exception as e:
                print(f"  Warning: AST chunking failed ({e}), falling back to simple chunking")
                return self.simple_chunker.chunk_file(content, file_path)
        else:
            # Use simple chunker for unsupported languages
            return self.simple_chunker.chunk_file(content, file_path)

    def format_chunk_with_context(self, chunk: Chunk) -> str:
        """
        Format a chunk with prepended context metadata.

        This helps the LLM understand the chunk's context.
        """
        context_header = f"""/*
 * CHUNK METADATA
 * File: {chunk.context.file_path}
 * Lines: {chunk.start_line}-{chunk.end_line}
 * Chunk: {chunk.context.chunk_index + 1}/{chunk.context.total_chunks}
 * Type: {chunk.chunk_type}
 */

"""

        # Add imports if present
        if chunk.context.imports:
            imports_section = "// Essential includes:\n"
            imports_section += "\n".join(chunk.context.imports[:5])
            imports_section += "\n\n"
        else:
            imports_section = ""

        # Add type definitions if present
        if chunk.context.type_definitions:
            types_section = "// Relevant type definitions:\n"
            for typedef in chunk.context.type_definitions[:3]:
                types_section += f"// {typedef}\n"
            types_section += "\n"
        else:
            types_section = ""

        return context_header + imports_section + types_section + chunk.content


# Example usage and testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python chunking_engine.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Read file
    with open(file_path, 'r') as f:
        content = f.read()

    # Create chunking engine
    engine = ChunkingEngine(target_lines=80, overlap_pct=0.20)

    # Check if chunking needed
    if engine.needs_chunking(content):
        num_lines = content.count('\n')
        print(f"File size: {len(content) / 1024:.1f} KB, Lines: {num_lines}")
        print("Chunking needed!")

        # Get chunks
        chunks = engine.get_chunks(content, file_path)

        print(f"\nCreated {len(chunks)} chunks:")
        for chunk in chunks:
            print(f"  Chunk {chunk.context.chunk_index}: lines {chunk.start_line}-{chunk.end_line} "
                  f"({chunk.end_line - chunk.start_line} lines, type: {chunk.chunk_type})")

        # Show first chunk with context
        if chunks:
            print("\n" + "="*80)
            print("FIRST CHUNK WITH CONTEXT:")
            print("="*80)
            print(engine.format_chunk_with_context(chunks[0]))
    else:
        print("File is small enough, no chunking needed.")
