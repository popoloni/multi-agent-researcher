# Changelog

All notable changes to the Multi-Agent Research System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-05-29

### 🚀 Major Features Added

#### AI-Powered Documentation Generation
- **Enhanced Content Quality**: Replaced basic templates with AI-generated descriptions using Ollama llama3.2:1b model
- **Asynchronous Generation**: Implemented background task processing with unique task IDs for long-running documentation generation
- **Real-time Progress Tracking**: Added comprehensive progress indicators (0-100%) with stage-specific status updates
- **Professional Content**: Generate rich, contextual documentation for functions, classes, architecture, and user guides

#### Functionalities Registry Complete Overhaul
- **Hierarchical File Structure**: Implemented tree view grouping functions by source files with collapsible sections
- **Smart Organization**: Added logical sorting (Classes → Functions → Methods → Variables) with both hierarchical and flat view options
- **Functional Action Buttons**: Fixed eye button to open GitHub source code at specific line numbers, doc button navigates to documentation with search
- **Enhanced User Experience**: Renamed confusing buttons and removed non-functional embedded tabs

### 🛠️ Critical Bug Fixes

#### Documentation Generation Issues
- **Fixed Section Mapping**: Resolved frontend/backend mapping inconsistencies (`usage` → `user_guide`, `api` → `api_reference`)
- **Async Flow Implementation**: Updated frontend to handle new asynchronous generation system with proper polling
- **Content Display Fix**: Resolved bug where frontend tried to convert objects when backend returns markdown
- **Timeout Resolution**: Eliminated 30-second timeout errors with proper background processing

#### Repository Management Improvements
- **Extended Timeouts**: Increased timeout from 30 seconds to 5 minutes (300 seconds) for repository operations
- **Progress Indicators**: Added step-by-step progress showing "Cloning repository...", "Analyzing structure...", "Generating AI descriptions..."
- **Enhanced Error Handling**: Implemented user-friendly error messages with automatic error clearing
- **User Education**: Added notices about expected operation times (3-5 minutes)

#### UI/UX Enhancements
- **Path Display Cleanup**: Created utility function to remove temp folder prefixes (`/tmp/kenobi/`) throughout the application
- **Navigation Fixes**: Resolved navigation loops and improved component routing
- **Import Path Fixes**: Corrected React import paths and context usage
- **Visual Feedback**: Enhanced hover tooltips and action button functionality

### 🔧 Technical Improvements

#### Backend Enhancements
- **Async Task Management**: Implemented task-based generation system with status polling endpoints
- **Enhanced Parsing**: Improved R language and Jupyter notebook parsing support
- **Comprehensive Prompts**: Created detailed prompts for overview, architecture analysis, and user guide generation
- **Progress API**: Added `/repositories/{id}/documentation/generate/status` and `/repositories/{id}/documentation/generate` endpoints

#### Frontend Improvements
- **Updated Components**: Enhanced Documentation, FunctionalitiesRegistry, CloneProgress, and RepositoryList components
- **Utility Functions**: Added `cleanRepositoryPath()` for consistent path display
- **Error Boundaries**: Improved error handling and user feedback throughout the application
- **Responsive Design**: Enhanced mobile compatibility and accessibility

### 📊 System Verification
- **Backend API**: Confirmed 78+ endpoints functional
- **GitHub Integration**: Verified working with real repositories (tested with popoloni/covid19)
- **Ollama Integration**: Confirmed 21+ models available and properly configured
- **Documentation Quality**: Verified AI generates professional, contextual content
- **Component Testing**: All major UI components working correctly

### 🐛 Bug Fixes
- Fixed React context errors in notification system
- Resolved repository duplication issues
- Fixed branch detection and language parsing
- Eliminated navigation loops in documentation pages
- Resolved functionalities registry usability issues
- Fixed repository addition timeout errors
- Cleaned up path display throughout the application

### 📝 Files Changed
**28 files changed, 2,598 insertions, 335 deletions**

**Backend Files:**
- `app/services/documentation_service.py` - Enhanced with AI-powered generation
- `app/services/research_service.py` - Improved async handling
- `app/main.py` - Added new endpoints and progress tracking

**Frontend Files:**
- `frontend/src/components/documentation/DocumentationGenerator.jsx` - Complete rewrite for async generation
- `frontend/src/components/documentation/FunctionalitiesRegistry.jsx` - Major overhaul with hierarchical structure
- `frontend/src/pages/Documentation.jsx` - Fixed section mapping and navigation
- `frontend/src/components/repository/CloneProgress.jsx` - Enhanced progress indicators
- `frontend/src/components/repository/RepositoryList.jsx` - Added path cleaning
- `frontend/src/services/repositories.js` - Extended timeouts and error handling

### 🏆 System Status
- **Completion**: 85% complete with high-quality foundations
- **Stability**: All critical bugs resolved
- **Performance**: Proper timeout handling and progress tracking
- **User Experience**: Professional interface with comprehensive error handling

---

## [1.1.0] - Previous Releases
See individual phase implementation summaries:
- [PHASE_0_IMPLEMENTATION_SUMMARY.md](PHASE_0_IMPLEMENTATION_SUMMARY.md)
- [PHASE_1_IMPLEMENTATION_SUMMARY.md](PHASE_1_IMPLEMENTATION_SUMMARY.md)
- [PHASE_3_IMPLEMENTATION_SUMMARY.md](PHASE_3_IMPLEMENTATION_SUMMARY.md) 