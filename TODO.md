# TODO: Improvements and Missing Activities (Prioritized)

## 1. Research Functionality (Highest Value: Core Product Promise)
- [ ] Implement the full research service (currently a mock)
- [ ] Integrate enhanced async handling and progress tracking (see migration_scripts/enhance_research_service.py)
- [ ] Align backend research progress with frontend ProgressTracker
- [ ] Add real multi-stage research operations and reporting

## 2. Production Monitoring and Optimization (Task 5.2 from MASTER_IMPLEMENTATION_PLAN)
- [ ] Implement production-ready monitoring and optimization:
    - Comprehensive performance monitoring
    - RAG response quality metrics
    - Database performance tracking
    - Vector search optimization
    - Caching optimization
    - Production health checks
    - Monitoring dashboard functionality

## 3. Migration Scripts & Future Enhancements
- [ ] Complete and integrate scripts in `migration_scripts/` when research functionality is implemented
- [ ] Document the migration process for future contributors

## 4. Virtual Environment Handling (Repository Health)
- [ ] Add `researcher-env/` to `.gitignore` to prevent committing local virtual environments
- [ ] Remove `researcher-env/` from the repository (should not be tracked)
- [ ] Update documentation to instruct users to create their own virtual environment

## 5. Deployment & Setup (Reliability for All Users)
- [ ] Ensure all scripts (`start_all.sh`, `stop_all.sh`, `check_status.sh`, etc.) are cross-platform or provide Windows alternatives
- [ ] Add more robust error handling and user feedback to management scripts

## 6. Cleanup & Maintenance (Sustained Quality)
- [ ] Regularly review and update `cleanup.sh` and `CLEANUP_GUIDE.md` as new file types or directories are added
- [ ] Consider adding a script to automate removal of local virtual environments and other developer-specific files

## 7. Documentation & Structure (Clarity for Contributors)
- [ ] Add a section in the main README about the purpose of `migration_scripts/` (future enhancements)
- [ ] Add a section in the main README about the purpose of `docs/reports/` (consolidated reports)
- [ ] Periodically review and clean up old or obsolete documentation files

## 8. Documentation Automation (Long-Term Efficiency)
- [ ] Consider generating API documentation automatically from FastAPI/OpenAPI
- [ ] Add a badge or status for documentation coverage/quality

## 9. Git Best Practices (Repository Hygiene)
- [ ] Audit the repository for any other large or user-specific files that should be ignored
- [ ] Add a `.gitattributes` file for consistent line endings and file handling

---
**This TODO list is now ordered by business and technical value, with core product and production-readiness tasks at the top.** 