# Feature Specification: Database Schema Discovery API

**Feature Branch**: `002-database-schema-api`
**Created**: 2025-11-23
**Status**: Draft
**Input**: User description: "create a new controller targeted to let the user understand the underlying database schema. please refer to @/home/user1/ai-expense-app-bundle/ai-expense-tracker-agent/langgraph/react-pipeline/src/react_agent/tools/schema.py (please be aware this is just sample that you can enhance based on get_database_schema, get_table_relationships)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explore Complete Database Structure (Priority: P1)

As a developer or AI agent working with the expense tracking system, I need to discover the complete database schema to understand available tables, their columns, data types, and relationships so I can construct valid queries and data operations.

**Why this priority**: This is the foundation for all database interactions. Without understanding the schema, users cannot effectively query or manipulate data. This provides immediate value by revealing the entire database structure in a single request.

**Independent Test**: Can be fully tested by making a single API request and verifying that all tables, columns, constraints, and relationships are returned in a structured format. Delivers immediate value for schema discovery and documentation.

**Acceptance Scenarios**:

1. **Given** the database contains multiple tables with various columns and relationships, **When** I request the complete database schema, **Then** I receive a structured response containing all table names, column definitions (with data types, nullability, defaults), constraints (primary keys, foreign keys, unique constraints), and relationships between tables
2. **Given** I am exploring the database for the first time, **When** I request the complete schema, **Then** I can identify which tables exist and how they relate to each other without needing to query each table individually
3. **Given** the database includes reference tables (currencies, account_types, categories), **When** I retrieve the complete schema, **Then** I can see these tables listed along with their columns and understand their purpose in the system

---

### User Story 2 - Inspect Individual Table Details (Priority: P2)

As a developer or AI agent, I need to inspect a specific table's structure in detail to understand its columns, constraints, and data types before performing operations on that table.

**Why this priority**: While P1 gives the complete picture, this provides focused details for specific tables. It's useful when you already know which table you're interested in and want detailed information without the overhead of fetching the entire schema.

**Independent Test**: Can be tested independently by requesting schema information for a single table (e.g., "accounts") and verifying that column details, constraints, and foreign key relationships are returned accurately.

**Acceptance Scenarios**:

1. **Given** I need to work with the "transactions" table, **When** I request schema information for that specific table, **Then** I receive detailed column information including names, data types, nullability, default values, and any length/precision constraints
2. **Given** a table has foreign key relationships, **When** I request its schema, **Then** I can see which columns reference other tables and understand the relationship structure
3. **Given** I request schema for a non-existent table, **When** the request is processed, **Then** I receive a clear error message indicating the table does not exist

---

### User Story 3 - Discover Table Relationships (Priority: P2)

As a developer or AI agent, I need to understand how tables relate to each other through foreign keys so I can construct proper JOIN queries and maintain referential integrity.

**Why this priority**: Understanding relationships is crucial for multi-table queries and maintaining data integrity. This is a focused view that complements the complete schema by highlighting the relationship graph.

**Independent Test**: Can be tested independently by requesting all foreign key relationships and verifying that the response shows which tables reference which other tables, including the specific columns involved.

**Acceptance Scenarios**:

1. **Given** the database has multiple foreign key relationships, **When** I request table relationships, **Then** I receive a list showing each foreign key with source table, source column, target table, and target column
2. **Given** I need to understand how "transactions" connect to "accounts", **When** I review the relationships response, **Then** I can identify the foreign key constraint and the columns that link these tables
3. **Given** a table has no foreign key relationships, **When** relationships are retrieved, **Then** that table is either not listed or clearly marked as having no relationships

---

### User Story 4 - Access Reference Data Values (Priority: P3)

As a developer or AI agent, I need to retrieve the actual values stored in reference/lookup tables (currencies, account types, categories) so I can validate user input and present available options.

**Why this priority**: While knowing the schema structure is essential, having quick access to reference data values helps with validation and user interface construction. This is lower priority because it's about data content rather than structure, but still valuable for complete understanding.

**Independent Test**: Can be tested independently by requesting reference data for a specific type (e.g., "currencies") and verifying that actual records with their values are returned.

**Acceptance Scenarios**:

1. **Given** I need to know valid currency codes, **When** I request reference data for currencies, **Then** I receive all active currency records with codes, names, symbols, and decimal places
2. **Given** I'm building a form for account creation, **When** I request account_types reference data, **Then** I receive all available account types with their IDs, names, descriptions, and whether they represent assets
3. **Given** I need all reference data at once, **When** I request reference data with type "all", **Then** I receive currencies, account types, and categories in a single response
4. **Given** I request reference data for an invalid type, **When** the request is processed, **Then** I receive an error message indicating the valid options (currencies, account_types, categories, all)

---

### Edge Cases

- What happens when the database schema changes (tables added/removed) after the API is deployed? The API should dynamically read from information_schema, so it always reflects the current state.
- How does the system handle database connection failures when trying to retrieve schema information? Should return an appropriate error response with clear messaging.
- What happens if a table has no constraints defined? The constraints array should be empty, not cause an error.
- How does the system handle very large databases with hundreds of tables? Consider response size and performance implications; may need pagination for complete schema requests.
- What happens when requesting schema for system tables (pg_catalog, information_schema)? Should filter to only show application tables in the 'public' schema.
- How does the system handle tables with no relationships? They should still appear in the schema response with empty or null relationship fields.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an endpoint to retrieve complete database schema information including all tables, columns, constraints, and relationships in a single request
- **FR-002**: System MUST provide an endpoint to retrieve detailed schema information for a specific table by name
- **FR-003**: System MUST provide an endpoint to retrieve all foreign key relationships across the database
- **FR-004**: System MUST provide an endpoint to retrieve reference data values from lookup tables (currencies, account_types, categories)
- **FR-005**: System MUST return column information including: column name, data type, nullability, default value, and length/precision constraints where applicable
- **FR-006**: System MUST return constraint information including: constraint name, constraint type (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK), affected columns, and referenced tables/columns for foreign keys
- **FR-007**: System MUST filter results to only include tables in the 'public' schema, excluding system schemas
- **FR-008**: System MUST return clear error messages when requesting schema for non-existent tables
- **FR-009**: System MUST return structured responses in JSON format with consistent field naming
- **FR-010**: Reference data endpoints MUST support filtering by type (currencies, account_types, categories, all)
- **FR-011**: Reference data endpoints MUST only return active records where applicable (e.g., currencies.is_active = TRUE, categories.is_active = TRUE)
- **FR-012**: System MUST handle database connection errors gracefully with appropriate error responses
- **FR-013**: All endpoints MUST use async/await patterns for non-blocking database operations
- **FR-014**: System MUST log successful schema retrievals and errors for monitoring and debugging

### Key Entities *(include if feature involves data)*

- **Database Schema**: Represents the complete structure of the database including all tables, their columns with data types and constraints, and relationships between tables via foreign keys
- **Table Schema**: Represents a single table's structure including its columns (name, data type, nullability, default values, length/precision) and constraints (primary keys, foreign keys, unique constraints, check constraints)
- **Table Relationship**: Represents a foreign key relationship between two tables, including the source table and column, target table and column, and constraint name
- **Reference Data**: Represents lookup/reference table records that define valid values for certain fields (currency codes, account types, expense categories)
- **Column Definition**: Represents detailed information about a table column including its name, data type, whether it accepts null values, default value, and size constraints (character_maximum_length, numeric_precision, numeric_scale)
- **Constraint Definition**: Represents a database constraint including its name, type (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK), the columns it affects, and for foreign keys, the referenced table and column

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can discover the complete database structure in a single API call without consulting external documentation
- **SC-002**: Schema information requests complete in under 2 seconds for databases with up to 50 tables
- **SC-003**: 100% of current table columns and constraints are accurately represented in the API response
- **SC-004**: AI agents can successfully use the schema endpoints to understand the database structure and construct valid queries without human intervention
- **SC-005**: Error responses provide clear, actionable information when schema requests fail (invalid table names, connection issues)
- **SC-006**: Reference data endpoints return results in under 500 milliseconds for typical lookup table sizes (under 1000 records)
- **SC-007**: The API accurately reflects schema changes immediately after database migrations without requiring service restart
