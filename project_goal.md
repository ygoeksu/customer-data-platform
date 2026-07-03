# Customer Data Platform

## Business Problem

Our customer information is scattered across multiple systems.

Customer records are received daily from different sources:

* CSV exports from legacy systems
* Customer metadata from external APIs
* Internal customer databases

As a result, customer data is often inconsistent, incomplete, duplicated, or outdated.

Business teams spend significant time manually cleaning data before they can use it for reporting, analytics, or customer support.

## Goal

Build a maintainable and reliable Customer Data Platform that automatically collects, validates, transforms, and stores customer information from multiple sources.

The platform should provide a single source of truth for customer data.

## Requirements

### Data Ingestion

The system must import customer records from:

* CSV files
* External REST APIs

### Data Validation

The system must validate incoming data and reject invalid records.

Validation rules include:

* Customer ID must exist
* Email must be valid
* Customer name must not be empty
* Country must be provided

### Data Transformation

The system must normalize customer data:

* Standardize names
* Normalize email addresses
* Remove duplicate records
* Apply business rules

### Data Storage

Validated customer records must be stored in a relational database.

### API Access

The platform must expose customer information through a REST API.

Users should be able to:

* Retrieve all customers
* Retrieve a customer by ID
* Verify platform health

### Observability

The platform must provide:

* Structured logging
* Error reporting
* Processing statistics

### Quality Requirements

The solution must be:

* Fully tested
* Type-safe
* Easy to maintain
* Extensible for future data sources

## Success Criteria

The platform successfully processes customer data from multiple sources and provides a clean, reliable, and accessible customer dataset for downstream consumers.
