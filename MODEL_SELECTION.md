# Kraang Model Selection Guide

## Overview

Kraang is tightly coupled to Anthropic's Claude API. You can choose different Claude models to balance cost, speed, and quality.

---

## Available Models

### 1. Haiku 4.5 (Recommended for Most Extractions)

**Model ID**: `claude-haiku-4-5-20251001`
**Shorthand**: `haiku`

**Cost** (approximate):
- Input: ~$0.001 per 1K tokens
- Output: ~$0.005 per 1K tokens

**Best For**:
- Code fact extraction (structured, predictable)
- Large file processing (minimal cost)
- High-volume extractions
- When speed matters

**Performance**:
- Fastest model
- Excellent for structured tasks
- May miss subtle nuances

**Example**:
```bash
./kraang extract-multi artifact_187 --model haiku
```

---

### 2. Sonnet 4.5 (Default, Balanced)

**Model ID**: `claude-sonnet-4-5-20250929`
**Shorthand**: `sonnet`

**Cost** (approximate):
- Input: ~$0.003 per 1K tokens
- Output: ~$0.015 per 1K tokens

**Best For**:
- Complex code analysis
- Nuanced constraint detection
- When quality matters more than cost

**Performance**:
- Balanced speed and capability
- Good reasoning ability
- 3x more expensive than Haiku

**Example**:
```bash
./kraang extract-multi artifact_187 --model sonnet
# Or (default):
./kraang extract-multi artifact_187
```

---

### 3. Opus 4.6 (Highest Quality)

**Model ID**: `claude-opus-4-6`
**Shorthand**: `opus`

**Cost** (approximate):
- Input: ~$0.015 per 1K tokens
- Output: ~$0.075 per 1K tokens

**Best For**:
- Critical analysis requiring highest accuracy
- Complex architectural constraints
- When cost is not a concern

**Performance**:
- Slowest model
- Best reasoning and analysis
- 15x more expensive than Haiku
- 5x more expensive than Sonnet

**Example**:
```bash
./kraang extract-multi artifact_187 --model opus
```

---

## Cost Comparison

### Scenario: Extract from update.c (283KB, 78 chunks, 7 passes)

Estimated API calls: **546 calls** (78 chunks × 7 passes)

**Without Caching** (first run):

| Model | Estimated Cost | Time |
|-------|----------------|------|
| **Haiku** | ~$5-10 | 5-10 min |
| **Sonnet** (default) | ~$15-30 | 10-15 min |
| **Opus** | ~$75-150 | 20-30 min |

**With Caching** (subsequent runs):

| Model | Estimated Cost | Reduction |
|-------|----------------|-----------|
| **Haiku** | ~$0.50-1 | 90% |
| **Sonnet** | ~$1.50-3 | 90% |
| **Opus** | ~$7.50-15 | 90% |

---

## Recommendations

### Development & Testing
**Use Haiku** - Fast, cheap, plenty capable for structured extraction

```bash
./kraang extract-multi artifact_187 --model haiku
```

### Production Extractions
**Use Sonnet** - Balanced quality and cost (default)

```bash
./kraang extract-multi artifact_187 --model sonnet
```

### Critical Analysis
**Use Opus** - Only when highest accuracy needed

```bash
./kraang extract-multi artifact_187 --model opus
```

---

## API Rate Limits

Different models have different rate limits:

| Model | Requests/min | Tokens/min |
|-------|--------------|------------|
| Haiku | Higher limits | Higher limits |
| Sonnet | Medium limits | Medium limits |
| Opus | Lower limits | Lower limits |

**Note**: Haiku typically has higher quotas, making it better for bulk processing.

---

## Usage Examples

### Simple (use shorthand)
```bash
# Fast and cheap
./kraang extract-multi artifact_187 --model haiku

# Balanced (default)
./kraang extract-multi artifact_187 --model sonnet

# Highest quality
./kraang extract-multi artifact_187 --model opus
```

### Advanced (full model ID)
```bash
./kraang extract-multi artifact_187 --model claude-haiku-4-5-20251001
```

### Combined with other options
```bash
# Haiku + limited passes + budget
./kraang extract-multi artifact_187 \
  --model haiku \
  --max-passes 5 \
  --budget 100
```

---

## Anthropic Coupling

### What's Tightly Coupled

✅ **Anthropic API**: Required, no alternatives
✅ **Claude models**: Must use Claude family
✅ **Prompt caching**: Uses Anthropic's cache_control API
✅ **Response format**: Expects Claude's JSON structure

### What Could Be Abstracted (Future)

⚠️ **Model selection**: ✅ Already configurable
⚠️ **Prompt format**: Could support other LLMs with adapter layer
⚠️ **Response parsing**: Could add fallback for non-Claude models

**Verdict**: Currently 100% Anthropic-dependent. Would need significant refactoring to support other providers (OpenAI, Google, etc.).

---

## Cost Optimization Tips

### 1. Use Haiku for Initial Extraction
```bash
./kraang extract-multi artifact_187 --model haiku
```

### 2. Enable All Caching Features
Caching is enabled by default, gives 70-90% cost reduction on re-runs.

### 3. Use Smart Pass Selection
Pass selector automatically skips irrelevant passes (40-60% fewer calls).

### 4. Incremental Updates
Only extract from changed files (80-95% reduction).

### 5. Combined Approach
```bash
# First extraction: Haiku (cheap)
./kraang extract-multi artifact_187 --model haiku

# Re-extraction: Cached (90% cheaper)
./kraang extract-multi artifact_187 --model haiku

# Expected: $5-10 first run, $0.50-1 subsequent runs
```

---

## Model Performance for Fact Extraction

Based on testing:

| Aspect | Haiku | Sonnet | Opus |
|--------|-------|--------|------|
| Accuracy | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Speed | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Cost | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Structured Tasks | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Subtle Nuances | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Conclusion**: Haiku is excellent for structured fact extraction and recommended for most use cases.

---

## API Key & Credits

### Setting API Key
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Checking Credits
Visit: https://console.anthropic.com/settings/billing

### Recharging
When you see:
```
Error: Your credit balance is too low to access the Anthropic API
```

Go to Plans & Billing to add credits.

---

## Summary

**Default**: Haiku 4.5 (cheapest/fastest, excellent for fact extraction)
**Balanced**: Sonnet 4.5 (if you need more nuanced analysis)
**High-accuracy**: Opus 4.6 (most expensive, only when needed)

**Typical Workflow**:
1. Develop with Haiku (fast, cheap)
2. Production with Haiku (cost-effective)
3. Critical analysis with Sonnet/Opus (when needed)

---

**Last Updated**: 2026-02-11
