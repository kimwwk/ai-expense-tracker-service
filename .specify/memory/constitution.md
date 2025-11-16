<!-- SYNC IMPACT REPORT
Version Change: 0.0.0 → 1.0.0
Modified Principles: N/A (Initial constitution)
Added Sections:
  - I. Code Quality & Simplicity
  - II. Testing Standards
  - III. User Experience Consistency
  - IV. Performance Requirements
  - Development Workflow
  - Quality Gates
Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - Updated with constitution checks
  ✅ .specify/templates/spec-template.md - Aligned with requirements structure
  ✅ .specify/templates/tasks-template.md - Aligned with testing and quality principles
Follow-up TODOs: None
-->

# AI Expense App Constitution

## Core Principles

### I. Code Quality & Simplicity (NON-NEGOTIABLE)

Every component, function, and module MUST adhere to single responsibility:

- **Single Purpose**: Each unit of code serves one clear, documented purpose
- **Decoupled Concepts**: Separate concerns into distinct modules - no god objects or files
- **Boring Over Clever**: Choose obvious, maintainable solutions over clever tricks
- **Self-Documenting**: If implementation requires lengthy explanation, it's too complex and MUST be refactored

**Rationale**: Complex, tightly-coupled code is the enemy of maintainability. Boring code that anyone can understand scales better than clever code that only the author understands.

**Anti-patterns to avoid**:
- Functions doing multiple unrelated things
- Classes managing more than one domain concept
- Files mixing business logic with infrastructure concerns
- Premature abstractions before clear patterns emerge

### II. Testing Standards

Testing discipline ensures reliability and enables confident refactoring:

- **Test Categories**: Unit (single function), Integration (module interaction), Contract (API/interface compliance)
- **Test-First Encouraged**: Write tests before or alongside implementation when requirements are clear
- **Test Coverage Goals**: Critical business logic MUST have tests; edge cases SHOULD have tests
- **Test Independence**: Tests MUST run in isolation without shared state or order dependencies
- **Failure Clarity**: Test failures MUST pinpoint the exact issue - no vague assertions

**Rationale**: Tests are living documentation and safety nets. They enable incremental progress by proving each small change works.

**Testing pragmatism**:
- Not everything needs 100% coverage - focus on business value and risk areas
- Integration tests over mocks when practical - test real behavior
- Slow tests are better than no tests, but fast tests are better than slow tests

### III. User Experience Consistency

User-facing features MUST provide consistent, predictable interactions:

- **Progressive Enhancement**: Core functionality works first, enhancements add polish
- **Graceful Degradation**: Features degrade gracefully when dependencies fail
- **Clear Feedback**: User actions receive immediate, unambiguous feedback (loading states, errors, success)
- **Accessible by Default**: UI components follow accessibility standards (WCAG 2.1 Level AA minimum)
- **Mobile-First Responsive**: Interfaces work on mobile devices first, scale up to desktop

**Rationale**: Consistent UX reduces cognitive load and builds user trust. Users should never wonder what's happening or whether their action succeeded.

**UX requirements**:
- Loading states for async operations >200ms
- Error messages explain what happened and how to fix it
- Form validation provides helpful guidance, not just rejection
- Navigation remains consistent across features

### IV. Performance Requirements

Performance is a feature, not an afterthought:

- **Response Time Targets**:
  - API endpoints: <200ms p95 latency for simple queries, <1s for complex operations
  - UI interactions: <100ms feedback, <1s for page loads
- **Resource Constraints**:
  - Backend: <500MB memory per service instance
  - Frontend: <2MB initial bundle size, <100KB per route chunk
- **Scalability Goals**: Support 1000 concurrent users without degradation
- **Monitoring Required**: All production code MUST emit metrics for latency, errors, and throughput

**Rationale**: Poor performance directly impacts user satisfaction and operational costs. Performance budgets prevent gradual degradation.

**Performance pragmatism**:
- Measure before optimizing - profile real bottlenecks
- Simple, correct code often performs well enough
- Complexity justified only when measurements prove necessity

## Development Workflow

### Incremental Progress Protocol

All changes MUST follow an incremental approach:

1. **Small Changes**: Each commit represents a single logical change that compiles and passes tests
2. **Learn First**: Study existing patterns before implementing new ones
3. **Verify Often**: Run tests and build after each change
4. **Commit Frequently**: Checkpoint progress with clear commit messages

**Rationale**: Small, verified steps prevent integration nightmares and make debugging trivial. You always have a working version to return to.

### Code Review Standards

All code changes MUST pass review before merging:

- **Constitution Compliance**: Reviewer verifies adherence to all principles
- **Test Coverage**: Changes include appropriate tests
- **Clarity Check**: Reviewer can understand intent without extensive explanation
- **No Compromises**: Constitution violations require explicit justification documented in PR

## Quality Gates

### Pre-Commit Gates

Before committing, verify:

- [ ] Code compiles/runs without errors
- [ ] Existing tests pass
- [ ] New tests added for new functionality (if applicable)
- [ ] Code follows single responsibility principle
- [ ] No obvious performance issues (N+1 queries, unnecessary loops, etc.)

### Pre-Merge Gates

Before merging to main:

- [ ] All tests pass in CI
- [ ] Code review approved by at least one reviewer
- [ ] Performance benchmarks within targets (if applicable)
- [ ] Documentation updated (if user-facing changes)
- [ ] Constitution compliance verified

### Complexity Justification Required

The following require explicit justification in PR or design doc:

- New external dependencies
- New abstraction layers (repositories, facades, etc.)
- Performance optimizations that sacrifice readability
- Architecture changes affecting multiple modules

**Justification format**: "We need X because Y, and simpler alternative Z was rejected because W"

## Governance

### Amendment Process

1. Propose amendment with rationale in pull request
2. Document impact on existing code and templates
3. Update all dependent templates and documentation
4. Increment version according to semantic versioning rules:
   - **MAJOR**: Backward-incompatible principle changes or removals
   - **MINOR**: New principles added or significant guidance expansions
   - **PATCH**: Clarifications, typo fixes, non-semantic refinements
5. Require approval from project maintainers before merge

### Enforcement

- All PRs MUST verify constitution compliance
- Template validation checks ensure generated artifacts align with principles
- Regular constitution reviews (quarterly) to verify principles remain relevant
- Violations tracked and addressed - patterns of violations trigger principle review

### Living Document

This constitution evolves with the project:

- Principles proven ineffective or harmful MUST be amended
- New consistent patterns discovered SHOULD be codified
- Complexity that provides no value MUST be removed
- Feedback from development experience informs amendments

**Version**: 1.0.0 | **Ratified**: 2025-11-16 | **Last Amended**: 2025-11-16
