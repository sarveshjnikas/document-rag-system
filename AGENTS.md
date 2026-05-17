# Karpathy-Inspired Coding Agent Guidelines

Guidelines for working with coding agents in this repo, inspired by Andrej Karpathy’s observations on common LLM coding pitfalls:
- https://x.com/karpathy/status/2015883857489522876

## The Problems (What to Avoid)

- Making wrong assumptions and “running with it” without checking
- Hiding confusion instead of asking clarifying questions
- Overcomplicating solutions and bloating abstractions
- Making drive-by changes to unrelated code/comments/formatting

## The Solution (Four Principles)

| Principle | Addresses |
| --- | --- |
| **Think Before Coding** | Wrong assumptions, hidden confusion, missing tradeoffs |
| **Simplicity First** | Overcomplication, bloated abstractions |
| **Surgical Changes** | Orthogonal edits, touching code you shouldn’t |
| **Goal-Driven Execution** | Tests-first, verifiable success criteria |

## 1) Think Before Coding

**Don’t assume. Don’t hide confusion. Surface tradeoffs.**

- State assumptions explicitly; if uncertain, ask rather than guess
- Present multiple interpretations when ambiguity exists; don’t pick silently
- Push back when a simpler approach exists
- Stop when confused; name what’s unclear and ask for clarification

## 2) Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked
- No abstractions for single-use code
- No “flexibility/configurability” unless requested
- No error handling for impossible scenarios
- If 200 lines could be 50, simplify

Test: *Would a senior engineer call this overcomplicated? If yes, simplify.*

## 3) Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don’t “improve” adjacent code, comments, or formatting
- Don’t refactor things that aren’t broken
- Match existing style, even if you’d do it differently
- If you notice unrelated dead code, mention it—don’t delete it

If your change creates orphans:
- Remove imports/variables/functions that **your** change made unused
- Don’t remove pre-existing dead code unless asked

Test: *Every changed line should trace directly to the request.*

## 4) Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform imperative asks into verifiable goals:

| Instead of… | Transform to… |
| --- | --- |
| “Add validation” | “Add tests for invalid inputs, then make them pass” |
| “Fix the bug” | “Add a repro test, then make it pass” |
| “Refactor X” | “Ensure tests pass before/after” |

For multi-step tasks, state a brief plan:

1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]

Strong success criteria let the agent loop independently.

## Tradeoff Note

These guidelines bias toward caution over speed. For trivial one-liners, use judgment.

## Commit Message Convention

- All commits must use: `{type}: {message describing commit}`
- Example: `docs: polish readme.md`

