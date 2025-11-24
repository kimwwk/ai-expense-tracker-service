# Feature Specification: Table Names List Endpoint

**Feature Branch**: `003-list-tables`
**Created**: 2025-11-24
**Status**: Draft
**Input**: User description: "create a new endpoint under schema controller, targeted to allow user access all the table names."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quick Table Discovery (Priority: P1)

As a developer or AI agent working with the expense tracker database, I want to quickly retrieve a simple list of all table names so that I can understand what tables exist without fetching the full schema details.

**Why this priority**: This is the most lightweight schema discovery operation - essential for quick exploration, autocomplete features, and initial database understanding. It provides immediate value by answering "what tables exist?" without the overhead of fetching full schema metadata.

**Independent Test**: Can be fully tested by making a single GET request and verifying it returns an array of table names from the public schema.

**Acceptance Scenarios**:

1. **Given** the database contains multiple tables in the public schema, **When** a user requests the table names list, **Then** the system returns all table names as a simple string array
2. **Given** a user needs to discover available tables, **When** they call the endpoint, **Then** the response completes in under 100ms
3. **Given** the database contains system tables in other schemas, **When** a user requests table names, **Then** only public schema tables are returned

---

### Edge Cases

- What happens when the public schema is empty (no tables)?
- How does the system handle database connection failures?
- What if the user lacks permissions to read information_schema?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST return a list of all table names from the public schema
- **FR-002**: System MUST return only table names, excluding views and system tables
- **FR-003**: System MUST sort table names alphabetically for consistent output
- **FR-004**: System MUST exclude tables from non-public schemas (pg_catalog, information_schema, etc.)
- **FR-005**: System MUST return an empty array if no tables exist in the public schema
- **FR-006**: System MUST use the existing schema router (/schema prefix)
- **FR-007**: System MUST follow existing error handling patterns used in other schema endpoints
- **FR-008**: System MUST log requests for monitoring and debugging purposes

### Key Entities

- **TableName**: A simple string representing the name of a database table in the public schema

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can retrieve the complete list of table names in under 100ms
- **SC-002**: The endpoint returns accurate results matching the actual database schema
- **SC-003**: The endpoint appears in the OpenAPI documentation at /docs with proper descriptions
- **SC-004**: 100% of table names from the public schema are included in the response
- **SC-005**: Zero system or internal schema tables are exposed in the response

## Assumptions

- The endpoint will be added to the existing schema router under the /schema prefix
- The implementation will follow the same patterns as other schema endpoints
- The response will be a simple JSON array of strings for minimal overhead
- The endpoint will use the existing database connection and session management
- Standard authentication/authorization rules apply (same as other schema endpoints)
- Performance target of <100ms is achievable since this is a simple metadata query
