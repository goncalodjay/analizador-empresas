# Design and Specification Documents

This document provides an overview of the design and specification files used in the project. The source files are organized into directories and follow specific naming conventions to ensure clarity and consistency.

## Source Files Overview

### `openspec/*.md`
These Markdown files contain detailed design specifications, including API definitions, system architecture, and functional requirements. They are typically used to document high-level design decisions and technical specifications.

### `openspec/*.yaml`
YAML files in this directory are used to define configuration settings, data schemas, or structured metadata for specifications. They often complement Markdown files by providing machine-readable data.

### `atl/*.md`
Markdown files here focus on architecture diagrams, technical guidelines, and implementation details. They are used to describe the system's structure, components, and integration points.

### `atl/*.yaml`
YAML files in this directory may store configuration parameters, dependency lists, or environment-specific settings related to the architecture. They are often referenced alongside Markdown documentation for consistency.

## Relationship Between Files
The `.md` and `.yaml` files in these directories are interconnected. For example:
- A `design.md` file might reference a `config.yaml` to define API endpoints.
- An `architecture.md` could use a `dependencies.yaml` to list component relationships.

## Example Usage
1. **API Specification**  
   - `openspec/api.md` (Markdown): Describes endpoint behavior.  
   - `openspec/api.yaml` (YAML): Defines request/response schemas.

2. **Architecture Diagram**  
   - `atl/system.md` (Markdown): Explains component roles.  
   - `atl/system.yaml` (YAML): Lists dependencies between components.

Note: The listed files are placeholders. Actual content depends on the project's specific requirements.