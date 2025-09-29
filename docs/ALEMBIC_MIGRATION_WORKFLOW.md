# Alembic Migration Workflow - AI Nurse Florence

## Overview
This document outlines the database migration workflow for AI Nurse Florence using Alembic.

## Setup Complete ✅

### Alembic Configuration
- **Configuration File**: `alembic.ini` - configured for SQLite development
- **Environment**: `alembic/env.py` - imports our database models
- **Migrations Directory**: `alembic/versions/` - stores migration scripts

### Initial Migration
- **Migration ID**: `3f5aacf09e0d`
- **Description**: Initial database schema
- **Tables Created**: `users`, `user_sessions`, `wizard_states`
- **Status**: ✅ Successfully applied

## Migration Commands

### Check Current Migration Status
```bash
alembic current
```

### View Migration History
```bash
alembic history --verbose
```

### Create New Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration for manual changes
alembic revision -m "Manual changes description"
```

### Apply Migrations
```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision_id>

# Upgrade one version at a time
alembic upgrade +1
```

### Rollback Migrations
```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Downgrade to base (remove all migrations)
alembic downgrade base
```

## Workflow for Schema Changes

### 1. Update Models
Edit the SQLAlchemy models in `src/models/database.py`

### 2. Generate Migration
```bash
alembic revision --autogenerate -m "Add new field to user table"
```

### 3. Review Migration
- Check the generated migration in `alembic/versions/`
- Verify the upgrade and downgrade functions
- Add any manual changes if needed

### 4. Test Migration
```bash
# Apply the migration
alembic upgrade head

# Test the changes
python test_alembic_migration.py

# If issues found, rollback
alembic downgrade -1
```

### 5. Commit Changes
```bash
git add alembic/ src/models/
git commit -m "Add migration: description"
```

## Database Configuration

### Development (SQLite)
```ini
# alembic.ini
sqlalchemy.url = sqlite:///./ai_nurse_florence.db
```

### Production (PostgreSQL)
```ini
# For production deployment
sqlalchemy.url = postgresql://user:password@localhost/ai_nurse_florence
```

## Migration Best Practices

### 1. Always Review Generated Migrations
- Auto-generated migrations may not be perfect
- Check for data loss scenarios
- Add data migration code if needed

### 2. Test Migrations Thoroughly
- Test both upgrade and downgrade
- Verify data integrity
- Test with realistic data volumes

### 3. Backup Before Production Migrations
```bash
# For PostgreSQL
pg_dump ai_nurse_florence > backup_$(date +%Y%m%d_%H%M%S).sql

# For SQLite
cp ai_nurse_florence.db ai_nurse_florence_backup_$(date +%Y%m%d_%H%M%S).db
```

### 4. Plan Downtime for Schema Changes
- Some migrations require table locks
- Plan maintenance windows for major changes
- Consider zero-downtime migration strategies for critical systems

## Troubleshooting

### Migration Fails
```bash
# Check current state
alembic current

# View pending migrations
alembic heads

# Force to specific version (use with caution)
alembic stamp <revision_id>
```

### Model Import Errors
- Ensure `src/` is in Python path
- Check that all model dependencies are available
- Verify SQLAlchemy model definitions

### Database Connection Issues
- Check database URL in `alembic.ini`
- Verify database server is running
- Check credentials and permissions

## Integration with Application

### Database Initialization
The application automatically creates tables on startup, but for production:

```python
# Use migrations instead of auto-creation
# In src/models/database.py, comment out:
# await conn.run_sync(Base.metadata.create_all)
```

### Health Checks
Monitor migration status in application health checks:

```python
async def check_database_migration_status():
    # Check if database is at latest version
    # Return status for monitoring systems
```

## Testing Migration Workflow

### Run Migration Tests
```bash
python test_alembic_migration.py
```

### Verify Schema Compatibility
```bash
python test_database_integration.py
```

## Production Deployment

### 1. Deploy Code
Deploy application code with new models

### 2. Run Migrations
```bash
alembic upgrade head
```

### 3. Restart Application
Restart application services to use new schema

### 4. Verify Deployment
Run health checks and integration tests

## Status: Phase 3.4.1 Complete ✅

- ✅ Alembic properly configured
- ✅ Initial migration created and tested
- ✅ Migration workflow documented
- ✅ Database schema version controlled
- ✅ Ready for future schema changes

**Next**: Phase 3.4.2 - Auth Router Database Integration
