# MigrationGuard 365

**ERP Data Migration, Validation & Reconciliation Platform**

MigrationGuard 365 is a Python-based ERP data migration and quality-control platform designed to simulate the migration of legacy ERP data into a Dynamics 365-inspired target structure.

It helps identify data quality issues, detect anomalies, manage migration exceptions, execute approved migrations, and reconcile source and target records.

The project uses synthetic ERP datasets to demonstrate a structured and auditable migration workflow.

## Key Features

- **Schema Mapping:** Maps legacy ERP fields to standardized target fields using Python and RapidFuzz.
- **Data Validation:** Applies configurable validation rules to identify missing, invalid, and inconsistent records.
- **Anomaly Detection:** Uses Isolation Forest to identify unusual invoice amounts.
- **Data Quality Scoring:** Calculates entity-level and overall data quality scores.
- **Migration Dry Run:** Classifies records as Ready, Needs Review, or Rejected before migration.
- **Exception Management:** Stores migration exceptions and supports manual correction of selected records.
- **Migration Execution:** Migrates eligible invoice records into the target database.
- **Reconciliation:** Compares source and target invoice counts and checks amounts, dates, and currencies.
- **Power BI Dashboard:** Visualizes migration KPIs, data quality scores, migration status, and exception distribution.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| Data Processing | Pandas, NumPy |
| Database | PostgreSQL, SQLAlchemy |
| Validation | Pydantic, PyYAML |
| Schema Mapping | RapidFuzz |
| Anomaly Detection | Scikit-learn, Isolation Forest |
| Visualization | Microsoft Power BI |
| Testing | Pytest |
| Synthetic Data | Faker |

## Project Architecture

```text
MigrationGuard365/
│
├── core/
│   ├── mapping.py
│   ├── validators.py
│   ├── rules_config.yaml
│   ├── anomaly_detection.py
│   ├── scoring.py
│   ├── migration.py
│   └── reconciliation.py
│
├── data/
│   ├── generate_data.py
│   ├── load_data.py
│   ├── run_validation.py
│   ├── run_anomaly_detection.py
│   ├── injected_errors.json
│   └── raw/
│
├── db/
│   ├── models.py
│   └── session.py
│
├── tests/
│   └── test_validation_rules.py
│
├── MigrationGuard365.pbix
├── requirements.txt
└── .gitignore
```

## Dataset

The project uses synthetic ERP data generated with Faker.

| Entity | Records |
|---|---:|
| Customers | 1,000 |
| Vendors | 300 |
| Invoices | 3,000 |
| **Total** | **4,300** |

Intentionally injected data quality issues simulate common legacy ERP migration problems, including missing tax IDs, invalid emails, duplicate records, invalid currencies, negative invoice amounts, and orphan references.

## Project Results

### Data Quality

| Entity | Quality Score |
|---|---:|
| Customers | 96.00% |
| Vendors | 92.00% |
| Invoices | 97.67% |
| **Overall** | **96.88%** |

### Migration Results

| Metric | Result |
|---|---:|
| Total records assessed | 4,300 |
| Ready | 4,144 |
| Needs Review | 138 |
| Rejected | 18 |
| Invoices successfully migrated | 2,907 |

### Reconciliation Results

| Metric | Result |
|---|---:|
| Source invoices | 3,000 |
| Target invoices | 2,907 |
| Missing invoices | 93 |
| Mismatched invoices | 0 |

The 93 invoices not present in the target were not migrated during the simulation. They should not be interpreted as data loss. The 2,907 migrated invoices had zero mismatches across the compared amount, date, and currency fields.

## Power BI Dashboard

The included Power BI dashboard provides an overview of:

- Total migration exceptions
- Successfully migrated invoices
- Total customers
- Data mismatches
- Entity-wise data quality scores
- Migration status distribution
- Exception status distribution

Power BI file: `MigrationGuard365.pbix`

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Naman123-code/MigrationGuard365.git
cd MigrationGuard365
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database named:

```text
migrationguard365
```

Create a `.env` file in the project root and configure your database connection:

```env
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/migrationguard365
```

Replace the username and password with your local PostgreSQL credentials.

### 5. Run the project

Start by generating the synthetic datasets and loading them into PostgreSQL. Then execute the validation, anomaly detection, migration, and reconciliation workflows using the scripts in the `data/` directory.

## Project Scope

MigrationGuard 365 is an educational ERP migration simulation inspired by enterprise data migration workflows.

It uses a simplified Dynamics 365-inspired target schema. It does not connect to a live Microsoft Dynamics 365 environment.

## Future Improvements

- Support additional ERP data formats and entities.
- Expand automated reconciliation checks.
- Improve exception correction workflows.
- Introduce role-based access control for migration operations.

---

**Built with Python, PostgreSQL, and Microsoft Power BI.**