# Migration Scripts

This directory contains scripts for database migrations, data import/export, and legacy system migrations for the Multi-Agent Research System.

## 📁 Directory Structure

```
migration_scripts/
├── database/                 # Database schema migrations
│   ├── migrations/          # Alembic migration files
│   ├── init_db.py          # Database initialization script
│   ├── backup_db.py        # Database backup utilities
│   └── restore_db.py       # Database restore utilities
├── data/                    # Data import/export scripts
│   ├── export_repositories.py    # Export repository data
│   ├── import_repositories.py    # Import repository data
│   ├── export_documentation.py   # Export documentation data
│   └── data_validation.py        # Data integrity validation
├── legacy/                  # Legacy system migration tools
│   ├── migrate_from_v1.py   # Migration from version 1.x
│   ├── convert_old_format.py # Convert old data formats
│   └── legacy_data_parser.py # Parse legacy data files
└── enhance_research_service.py   # Research service enhancements
```

## Purpose

Migration scripts are used to:
- Upgrade existing functionality with enhanced features
- Migrate data between different versions
- Apply system improvements and optimizations
- Maintain backward compatibility during updates
- Handle database schema changes
- Import/export data for backup and migration purposes

## Available Scripts

### System Enhancement Scripts

#### 1. enhance_research_service.py
**Status**: Ready for integration
**Purpose**: Enhances the research service with better async handling and progress tracking
**Features**:
- Improved ResearchTask class with better state management
- Enhanced ProgressTracker for real-time progress updates
- Better async handling for concurrent research operations

### Database Migration Scripts

#### database/init_db.py
**Purpose**: Initialize database schema and create initial tables
**Usage**: `python database/init_db.py`

#### database/backup_db.py
**Purpose**: Create database backups with timestamp
**Usage**: `python database/backup_db.py --output backup_$(date +%Y%m%d_%H%M%S).sql`

#### database/restore_db.py
**Purpose**: Restore database from backup file
**Usage**: `python database/restore_db.py --input backup_file.sql`

### Data Migration Scripts

#### data/export_repositories.py
**Purpose**: Export repository data to JSON or CSV format
**Usage**: `python data/export_repositories.py --format json --output repositories.json`

#### data/import_repositories.py
**Purpose**: Import repository data from JSON or CSV files
**Usage**: `python data/import_repositories.py --input repositories.json`

#### data/export_documentation.py
**Purpose**: Export documentation data for backup or migration
**Usage**: `python data/export_documentation.py --all --output docs_export.json`

#### data/data_validation.py
**Purpose**: Validate data integrity and fix common issues
**Usage**: `python data/data_validation.py --check-all`

### Legacy Migration Scripts

#### legacy/migrate_from_v1.py
**Purpose**: Migrate data from version 1.x to current version
**Usage**: `python legacy/migrate_from_v1.py --source /path/to/old --target /path/to/new`

#### legacy/convert_old_format.py
**Purpose**: Convert old data formats to new schema
**Usage**: `python legacy/convert_old_format.py --input old_data.xml --output new_data.json`

#### legacy/legacy_data_parser.py
**Purpose**: Parse and convert legacy data files
**Usage**: `python legacy/legacy_data_parser.py --input legacy_export.txt --output parsed_data.json`

## Usage

### Running Migration Scripts

1. **Backup your data** before running any migration script
2. **Stop all services** using `./stop_all.sh`
3. **Run the migration script**:
   ```bash
   cd migration_scripts
   python enhance_research_service.py
   ```
4. **Restart services** using `./start_all.sh`
5. **Verify functionality** using the web interface

### Integration Process

1. **Review the script** to understand what changes will be made
2. **Test in development** environment first
3. **Create backups** of critical data and configurations
4. **Run the migration** during maintenance window
5. **Validate results** and rollback if necessary

## Migration Guidelines

### Before Migration
- [ ] Create full system backup
- [ ] Document current system state
- [ ] Test migration in development environment
- [ ] Plan rollback strategy

### During Migration
- [ ] Stop all services
- [ ] Run migration script
- [ ] Monitor for errors
- [ ] Validate database integrity

### After Migration
- [ ] Restart all services
- [ ] Test core functionality
- [ ] Verify data integrity
- [ ] Update documentation
- [ ] Monitor system performance

## Rollback Procedures

If a migration fails or causes issues:

1. **Stop all services**
2. **Restore from backup**
3. **Restart services**
4. **Verify system functionality**
5. **Report issues** for investigation

## Contributing

When adding new migration scripts:

1. **Follow naming convention**: `action_component_version.py`
2. **Include comprehensive documentation**
3. **Add rollback procedures**
4. **Test thoroughly in development**
5. **Update this README**

## Support

For migration issues or questions:
- Check the main project documentation
- Review system logs for error details
- Create an issue in the project repository