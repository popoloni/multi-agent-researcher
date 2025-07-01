# Research Functionality Implementation Plan

## 📋 Executive Summary

This document outlines a comprehensive plan to implement the multi-agent research functionality as the highest priority feature. The plan is based on the user's detailed UI proposal and ensures full compatibility with the existing API structure while providing a production-ready research system.

## 🎯 Project Scope & Objectives

### Primary Goal
Implement a fully functional multi-agent research system that can:
- Accept research queries and execute them asynchronously
- Provide real-time progress tracking with agent activity monitoring
- Generate comprehensive research reports with citations
- Maintain research history and provide result analytics

### Success Criteria
- ✅ Complete async research workflow from query to final report
- ✅ Real-time progress tracking with visual indicators
- ✅ Comprehensive test coverage (unit, integration, e2e)
- ✅ Production-ready error handling and monitoring
- ✅ Responsive UI matching the proposed design
- ✅ Full API compatibility with existing endpoints

## 🏗️ Architecture Analysis

### Current State Assessment
- **Backend**: Research endpoints exist but use mock implementations
- **Frontend**: Basic placeholder WebResearch page
- **API Compatibility**: ✅ Excellent - proposed UI aligns perfectly with existing endpoints
- **Data Models**: ✅ Complete - all required schemas are defined
- **Agent System**: ✅ Functional - LeadResearchAgent and subagents exist

### Proposed Architecture Alignment
The user's proposal is **fully compatible** with the current system:
- API endpoints match exactly (`/research/start`, `/research/{id}/status`, `/research/{id}/result`)
- Data models align with `ResearchQuery`, `ResearchResult`, `CitationInfo` schemas
- Component structure follows React best practices
- Service layer integration is well-designed

## 📅 Implementation Phases

## Phase 1: Backend Research Service Enhancement (Days 1-3)

### Task 1.1: Research Service Core Implementation
**Objective**: Replace mock research service with fully functional implementation

**Deliverables**:
- Enhanced `ResearchService` with real async processing
- Proper research ID generation and tracking
- Status management with detailed progress states
- Result storage and retrieval

**Implementation Details**:
```python
# app/services/research_service.py enhancements
class ResearchService:
    def __init__(self):
        self.active_research: Dict[UUID, ResearchTask] = {}
        self.completed_research: Dict[UUID, ResearchResult] = {}
        self.research_status: Dict[UUID, ResearchStatus] = {}
    
    async def start_research(self, query: ResearchQuery) -> UUID:
        # Generate unique research ID
        # Create research task with progress tracking
        # Initialize agent coordination
        # Return research ID
    
    async def get_research_status(self, research_id: UUID) -> Dict[str, Any]:
        # Return detailed status with agent activities
        # Include progress percentage and current stage
        # Provide token usage and source counts
    
    async def get_research_result(self, research_id: UUID) -> ResearchResult:
        # Return complete research result
        # Include formatted report, citations, sources
        # Provide analytics and metadata
```

**Test Requirements**:
- Unit tests for all service methods
- Integration tests with LeadResearchAgent
- Mock agent responses for consistent testing
- Performance tests for concurrent research tasks

**Acceptance Criteria**:
- [ ] Research tasks execute asynchronously without blocking
- [ ] Status updates provide accurate progress information
- [ ] Results include all required fields (report, citations, sources)
- [ ] Error handling covers all failure scenarios
- [ ] Concurrent research tasks don't interfere with each other

### Task 1.2: Progress Tracking Enhancement
**Objective**: Implement detailed progress tracking with agent activity monitoring

**Deliverables**:
- Real-time progress updates with stage information
- Individual agent status tracking
- Token usage and performance metrics
- Research stage transitions (planning → executing → synthesizing → citing)

**Implementation Details**:
```python
class ResearchStatus:
    status: Literal["started", "planning", "executing", "synthesizing", "citing", "completed", "failed"]
    progress_percentage: int
    current_stage: str
    agents: List[AgentStatus]
    sources_found: int
    tokens_used: int
    estimated_completion: Optional[datetime]
    
class AgentStatus:
    agent_id: str
    name: str
    status: Literal["idle", "searching", "analyzing", "completed", "failed"]
    current_task: str
    sources_processed: int
    tokens_used: int
```

**Test Requirements**:
- Progress tracking accuracy tests
- Agent status synchronization tests
- Performance impact assessment
- Real-time update delivery tests

**Acceptance Criteria**:
- [ ] Progress updates are accurate and timely
- [ ] Agent activities are properly tracked and reported
- [ ] Performance metrics are collected and exposed
- [ ] Status transitions follow logical sequence

### Task 1.3: Enhanced Agent Coordination
**Objective**: Improve LeadResearchAgent to provide detailed progress feedback

**Deliverables**:
- Enhanced agent communication for progress reporting
- Structured research plan generation
- Improved error handling and recovery
- Agent performance monitoring

**Test Requirements**:
- Agent coordination tests
- Error recovery scenario tests
- Performance benchmarking
- Resource usage monitoring

**Acceptance Criteria**:
- [ ] Agents report progress consistently
- [ ] Research plans are well-structured and actionable
- [ ] Error recovery maintains system stability
- [ ] Resource usage is optimized and monitored

## Phase 2: Frontend Component Development (Days 4-7)

### Task 2.1: ResearchInterface Component
**Objective**: Implement the main research interface component

**Deliverables**:
- Complete ResearchInterface component with all proposed features
- Research query input with validation
- Settings configuration (max agents, iterations)
- Real-time status polling
- Error handling and user feedback

**Implementation Details**:
```jsx
// src/components/research/ResearchInterface.jsx
const ResearchInterface = () => {
  // State management for query, research status, results
  // Polling mechanism for status updates
  // Settings configuration
  // Error handling and recovery
  // Integration with research service API
};
```

**Test Requirements**:
- Component rendering tests
- User interaction tests (input, buttons, settings)
- API integration tests
- Error state handling tests
- Responsive design tests

**Acceptance Criteria**:
- [ ] Component renders correctly on all screen sizes
- [ ] User inputs are validated and handled properly
- [ ] API calls are made correctly with proper error handling
- [ ] Real-time updates work without performance issues
- [ ] Settings are persisted and applied correctly

### Task 2.2: ResearchProgress Component
**Objective**: Implement comprehensive progress tracking display

**Deliverables**:
- Visual progress indicators with stage breakdown
- Agent activity monitoring display
- Performance metrics visualization
- Time tracking and estimation

**Implementation Details**:
```jsx
// src/components/research/ResearchProgress.jsx
const ResearchProgress = ({ status, isActive }) => {
  // Progress bar with stage indicators
  // Agent activity cards with real-time updates
  // Performance metrics dashboard
  // Time tracking and estimation
};
```

**Test Requirements**:
- Progress visualization accuracy tests
- Real-time update performance tests
- Agent status display tests
- Responsive layout tests

**Acceptance Criteria**:
- [ ] Progress is visually clear and accurate
- [ ] Agent activities are displayed in real-time
- [ ] Performance metrics are easy to understand
- [ ] Component handles all status states correctly

### Task 2.3: ResearchResults Component
**Objective**: Implement comprehensive results display with multiple views

**Deliverables**:
- Tabbed interface (Report, Sources, Citations, Analytics)
- Report formatting and display
- Source verification and citation management
- Analytics dashboard with research metadata

**Implementation Details**:
```jsx
// src/components/research/ResearchResults.jsx
const ResearchResults = ({ results, query }) => {
  // Tabbed interface with smooth transitions
  // Rich text report display with formatting
  // Interactive source and citation management
  // Analytics visualization
  // Export functionality (download, copy, share)
};
```

**Test Requirements**:
- Tab navigation and content display tests
- Report formatting and rendering tests
- Source and citation interaction tests
- Export functionality tests
- Analytics accuracy tests

**Acceptance Criteria**:
- [ ] All tabs display correct content
- [ ] Report formatting is readable and professional
- [ ] Sources and citations are properly linked and verified
- [ ] Analytics provide meaningful insights
- [ ] Export functions work correctly

### Task 2.4: ResearchHistory Component
**Objective**: Implement research history management

**Deliverables**:
- Historical research query display
- Quick query reuse functionality
- Research result access
- History management (delete, organize)

**Test Requirements**:
- History loading and display tests
- Query reuse functionality tests
- History management operation tests
- Performance tests with large history

**Acceptance Criteria**:
- [ ] History loads quickly and displays correctly
- [ ] Query reuse works seamlessly
- [ ] History management operations are reliable
- [ ] Component handles empty and large history states

## Phase 3: API Service Integration (Days 8-9)

### Task 3.1: Research API Service
**Objective**: Implement comprehensive API service for research operations

**Deliverables**:
- Complete research service with all API endpoints
- Error handling and retry logic
- Request/response validation
- Performance optimization

**Implementation Details**:
```javascript
// src/services/research.js
export const researchService = {
  startResearch: (query, settings) => api.post('/research/start', { query, ...settings }),
  getResearchStatus: (researchId) => api.get(`/research/${researchId}/status`),
  getResearchResult: (researchId) => api.get(`/research/${researchId}/result`),
  getHistory: () => api.get('/research/history'),
  // Additional utility methods
};
```

**Test Requirements**:
- API endpoint integration tests
- Error handling and retry logic tests
- Request/response validation tests
- Performance and timeout tests

**Acceptance Criteria**:
- [ ] All API endpoints work correctly
- [ ] Error handling provides meaningful feedback
- [ ] Requests are properly validated
- [ ] Performance meets requirements

### Task 3.2: Real-time Updates Implementation
**Objective**: Implement efficient real-time status updates

**Deliverables**:
- Optimized polling mechanism
- WebSocket integration (if needed)
- Update batching and throttling
- Connection management

**Test Requirements**:
- Polling efficiency tests
- Update accuracy and timing tests
- Connection stability tests
- Performance impact assessment

**Acceptance Criteria**:
- [ ] Updates are timely and accurate
- [ ] Polling doesn't impact performance
- [ ] Connection issues are handled gracefully
- [ ] Update frequency is optimized

## Phase 4: Testing & Quality Assurance (Days 10-12)

### Task 4.1: Comprehensive Test Suite
**Objective**: Implement complete test coverage for all components and services

**Deliverables**:
- Unit tests for all components and services
- Integration tests for API interactions
- End-to-end tests for complete workflows
- Performance and load tests

**Test Structure**:
```
tests/
├── unit/
│   ├── components/
│   │   ├── ResearchInterface.test.jsx
│   │   ├── ResearchProgress.test.jsx
│   │   ├── ResearchResults.test.jsx
│   │   └── ResearchHistory.test.jsx
│   ├── services/
│   │   ├── research.test.js
│   │   └── api.test.js
│   └── backend/
│       ├── research_service.test.py
│       └── lead_agent.test.py
├── integration/
│   ├── research_workflow.test.js
│   ├── api_integration.test.js
│   └── agent_coordination.test.py
└── e2e/
    ├── research_complete_flow.test.js
    ├── error_scenarios.test.js
    └── performance.test.js
```

**Test Requirements**:
- 90%+ code coverage for all new components
- All user workflows tested end-to-end
- Error scenarios and edge cases covered
- Performance benchmarks established

**Acceptance Criteria**:
- [ ] All tests pass consistently
- [ ] Code coverage meets requirements
- [ ] Performance benchmarks are met
- [ ] Error scenarios are properly handled

### Task 4.2: User Acceptance Testing
**Objective**: Validate the implementation meets user requirements

**Deliverables**:
- User testing scenarios and scripts
- Usability testing results
- Performance validation
- Accessibility compliance

**Test Scenarios**:
1. **Basic Research Flow**: User enters query, monitors progress, reviews results
2. **Advanced Settings**: User configures agents and iterations, validates impact
3. **Error Handling**: Network issues, invalid queries, service failures
4. **History Management**: Accessing previous research, reusing queries
5. **Export Functionality**: Downloading reports, copying content
6. **Mobile Experience**: All functionality on mobile devices

**Acceptance Criteria**:
- [ ] All user scenarios complete successfully
- [ ] User interface is intuitive and responsive
- [ ] Performance meets user expectations
- [ ] Accessibility standards are met

## Phase 5: Production Deployment & Monitoring (Days 13-14)

### Task 5.1: Production Readiness
**Objective**: Ensure the system is ready for production deployment

**Deliverables**:
- Production configuration and environment setup
- Monitoring and alerting implementation
- Performance optimization
- Security review and hardening

**Production Checklist**:
- [ ] Environment variables properly configured
- [ ] Database connections optimized
- [ ] Caching strategy implemented
- [ ] Rate limiting configured
- [ ] Security headers and CORS properly set
- [ ] Logging and monitoring in place
- [ ] Error tracking configured
- [ ] Performance monitoring active

### Task 5.2: Documentation & Training
**Objective**: Provide comprehensive documentation for users and developers

**Deliverables**:
- User documentation and tutorials
- API documentation updates
- Developer setup and contribution guides
- Troubleshooting and FAQ

**Documentation Structure**:
```
docs/
├── user/
│   ├── research-guide.md
│   ├── advanced-features.md
│   └── troubleshooting.md
├── developer/
│   ├── research-api.md
│   ├── component-architecture.md
│   └── testing-guide.md
└── deployment/
    ├── production-setup.md
    └── monitoring-guide.md
```

## 🧪 Testing Strategy

### Test Pyramid Structure

#### Unit Tests (70% of tests)
- **Frontend Components**: React Testing Library + Jest
- **Backend Services**: pytest with async support
- **API Endpoints**: FastAPI test client
- **Utility Functions**: Standard unit testing

#### Integration Tests (20% of tests)
- **API Integration**: Full request/response cycle testing
- **Database Integration**: Real database operations
- **Agent Coordination**: Multi-agent workflow testing
- **Service Communication**: Inter-service communication testing

#### End-to-End Tests (10% of tests)
- **Complete User Workflows**: Cypress or Playwright
- **Cross-browser Testing**: Multiple browser support
- **Performance Testing**: Load and stress testing
- **Accessibility Testing**: Screen reader and keyboard navigation

### Test Data Management
- **Mock Data**: Consistent test datasets for predictable results
- **Test Fixtures**: Reusable test data and configurations
- **Database Seeding**: Automated test data setup and teardown
- **API Mocking**: External service mocking for isolated testing

### Continuous Testing
- **Pre-commit Hooks**: Automated testing before code commits
- **CI/CD Pipeline**: Automated testing on all pull requests
- **Performance Monitoring**: Continuous performance regression testing
- **Security Testing**: Automated security vulnerability scanning

## 📊 Success Metrics & KPIs

### Functional Metrics
- **Research Completion Rate**: >95% of research queries complete successfully
- **Average Research Time**: <5 minutes for standard queries
- **Progress Accuracy**: Progress indicators within 5% of actual completion
- **Error Recovery Rate**: >90% of errors handled gracefully

### Performance Metrics
- **API Response Time**: <200ms for status checks, <2s for research start
- **Frontend Load Time**: <3s initial load, <1s navigation
- **Concurrent Users**: Support 50+ concurrent research sessions
- **Memory Usage**: <500MB per active research session

### Quality Metrics
- **Test Coverage**: >90% code coverage across all components
- **Bug Density**: <1 bug per 1000 lines of code
- **User Satisfaction**: >4.5/5 rating in user testing
- **Accessibility Score**: >95% WCAG 2.1 AA compliance

### Business Metrics
- **Feature Adoption**: >80% of users try research functionality
- **User Retention**: >70% of users return to use research again
- **Research Quality**: >4/5 average rating for research report quality
- **Time Savings**: >50% reduction in manual research time

## 🚀 Risk Management & Mitigation

### Technical Risks
1. **Performance Degradation**
   - *Risk*: Real-time updates impact system performance
   - *Mitigation*: Implement efficient polling, connection pooling, caching
   - *Monitoring*: Performance metrics, load testing

2. **Agent Coordination Complexity**
   - *Risk*: Multi-agent coordination becomes unreliable
   - *Mitigation*: Robust error handling, agent isolation, fallback mechanisms
   - *Monitoring*: Agent health checks, coordination success rates

3. **Scalability Limitations**
   - *Risk*: System doesn't scale with increased usage
   - *Mitigation*: Horizontal scaling design, resource optimization
   - *Monitoring*: Resource usage tracking, performance benchmarks

### User Experience Risks
1. **Complex Interface**
   - *Risk*: Users find the interface overwhelming
   - *Mitigation*: Progressive disclosure, user testing, intuitive design
   - *Monitoring*: User feedback, usage analytics

2. **Slow Research Times**
   - *Risk*: Research takes too long, users abandon
   - *Mitigation*: Progress indicators, time estimates, optimization
   - *Monitoring*: Completion rates, user session duration

### Business Risks
1. **Feature Scope Creep**
   - *Risk*: Requirements expand beyond initial scope
   - *Mitigation*: Clear requirements documentation, change control process
   - *Monitoring*: Regular scope reviews, stakeholder alignment

2. **Timeline Delays**
   - *Risk*: Implementation takes longer than planned
   - *Mitigation*: Realistic estimates, buffer time, parallel development
   - *Monitoring*: Daily progress tracking, milestone reviews

## 📋 Implementation Checklist

### Phase 1: Backend Enhancement
- [ ] Research service core implementation
- [ ] Progress tracking system
- [ ] Agent coordination enhancement
- [ ] Database integration
- [ ] Error handling implementation
- [ ] Performance optimization
- [ ] Unit test coverage
- [ ] Integration testing

### Phase 2: Frontend Development
- [ ] ResearchInterface component
- [ ] ResearchProgress component
- [ ] ResearchResults component
- [ ] ResearchHistory component
- [ ] Responsive design implementation
- [ ] Accessibility features
- [ ] Component testing
- [ ] User interaction testing

### Phase 3: Integration & Services
- [ ] API service implementation
- [ ] Real-time update system
- [ ] Error handling and recovery
- [ ] Performance optimization
- [ ] Security implementation
- [ ] API testing
- [ ] Integration testing

### Phase 4: Testing & QA
- [ ] Comprehensive test suite
- [ ] Performance testing
- [ ] Security testing
- [ ] Accessibility testing
- [ ] User acceptance testing
- [ ] Cross-browser testing
- [ ] Mobile testing
- [ ] Load testing

### Phase 5: Production Deployment
- [ ] Production environment setup
- [ ] Monitoring implementation
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Documentation completion
- [ ] User training materials
- [ ] Deployment automation
- [ ] Go-live checklist

## 🎯 Conclusion

This implementation plan provides a comprehensive roadmap for delivering a production-ready multi-agent research system. The plan is structured to deliver tangible value at each phase while maintaining high quality standards and thorough testing.

The proposed UI design is fully compatible with the existing API structure, making implementation straightforward and reducing integration risks. The phased approach allows for iterative development and early feedback incorporation.

Key success factors:
- **Clear deliverables** at each phase with specific acceptance criteria
- **Comprehensive testing** strategy ensuring quality and reliability
- **Risk mitigation** plans for common technical and business challenges
- **Performance focus** with specific metrics and monitoring
- **User-centric design** with emphasis on usability and accessibility

The estimated timeline of 14 days provides adequate time for thorough implementation while maintaining development momentum. Regular checkpoints and milestone reviews will ensure the project stays on track and meets all requirements.

---

**Next Steps**: 
1. Review and approve this implementation plan
2. Set up development environment and tooling
3. Begin Phase 1 implementation
4. Establish regular progress review meetings
5. Prepare test environments and data

**Contact**: For questions or clarifications about this implementation plan, please refer to the detailed task descriptions and acceptance criteria provided for each phase.

---

# User proposal

# Research Page Implementation

Based on the API description and requirements, I'll create a comprehensive search/research page that performs async research with progress tracking and results display.

## 📋 Research Page Structure

### 1. Research Interface Component

**src/components/research/ResearchInterface.jsx:**
```jsx
import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  Play, 
  Pause, 
  RefreshCw, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  FileText,
  Download,
  Settings,
  Loader2
} from 'lucide-react';
import ResearchProgress from './ResearchProgress';
import ResearchResults from './ResearchResults';
import ResearchHistory from './ResearchHistory';

const ResearchInterface = () => {
  const [query, setQuery] = useState('');
  const [isResearching, setIsResearching] = useState(false);
  const [currentResearchId, setCurrentResearchId] = useState(null);
  const [researchStatus, setResearchStatus] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [settings, setSettings] = useState({
    maxSubagents: 3,
    maxIterations: 5
  });

  const pollIntervalRef = useRef(null);

  // Poll for research status updates
  useEffect(() => {
    if (currentResearchId && isResearching) {
      pollIntervalRef.current = setInterval(async () => {
        try {
          const response = await fetch(`/api/research/${currentResearchId}/status`);
          const statusData = await response.json();
          
          setResearchStatus(statusData);
          
          if (statusData.status === 'completed') {
            // Fetch final results
            const resultResponse = await fetch(`/api/research/${currentResearchId}/result`);
            const resultData = await resultResponse.json();
            setResults(resultData);
            setIsResearching(false);
            clearInterval(pollIntervalRef.current);
          } else if (statusData.status === 'failed') {
            setError(statusData.message || 'Research failed');
            setIsResearching(false);
            clearInterval(pollIntervalRef.current);
          }
        } catch (err) {
          console.error('Error polling research status:', err);
          setError('Failed to get research status');
          setIsResearching(false);
          clearInterval(pollIntervalRef.current);
        }
      }, 2000); // Poll every 2 seconds
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [currentResearchId, isResearching]);

  const startResearch = async () => {
    if (!query.trim()) return;

    setIsResearching(true);
    setError(null);
    setResults(null);
    setResearchStatus(null);

    try {
      const response = await fetch('/api/research/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          max_subagents: settings.maxSubagents,
          max_iterations: settings.maxIterations
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setCurrentResearchId(data.research_id);
        setResearchStatus({
          status: 'started',
          message: 'Research initiated...'
        });
      } else {
        throw new Error(data.detail || 'Failed to start research');
      }
    } catch (err) {
      setError(err.message);
      setIsResearching(false);
    }
  };

  const stopResearch = () => {
    setIsResearching(false);
    setCurrentResearchId(null);
    setResearchStatus(null);
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }
  };

  const clearResults = () => {
    setResults(null);
    setError(null);
    setResearchStatus(null);
    setCurrentResearchId(null);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isResearching) {
      e.preventDefault();
      startResearch();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Multi-Agent Research System
          </h1>
          <p className="text-gray-600">
            Conduct comprehensive research using AI agents that work in parallel to gather and analyze information.
          </p>
        </div>

        {/* Research Input */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex flex-col space-y-4">
            {/* Query Input */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Research Query
              </label>
              <div className="relative">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Enter your research question (e.g., 'What are the latest breakthroughs in AI-powered medical diagnosis in 2025?')"
                  className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  rows={3}
                  disabled={isResearching}
                />
                <Search className="absolute right-4 top-4 w-5 h-5 text-gray-400" />
              </div>
            </div>

            {/* Settings and Controls */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
              {/* Research Settings */}
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Settings className="w-4 h-4 text-gray-500" />
                  <label className="text-sm text-gray-700">Max Agents:</label>
                  <select
                    value={settings.maxSubagents}
                    onChange={(e) => setSettings(prev => ({ ...prev, maxSubagents: parseInt(e.target.value) }))}
                    disabled={isResearching}
                    className="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={1}>1</option>
                    <option value={2}>2</option>
                    <option value={3}>3</option>
                    <option value={4}>4</option>
                    <option value={5}>5</option>
                  </select>
                </div>

                <div className="flex items-center space-x-2">
                  <label className="text-sm text-gray-700">Max Iterations:</label>
                  <select
                    value={settings.maxIterations}
                    onChange={(e) => setSettings(prev => ({ ...prev, maxIterations: parseInt(e.target.value) }))}
                    disabled={isResearching}
                    className="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={2}>2</option>
                    <option value={3}>3</option>
                    <option value={5}>5</option>
                    <option value={8}>8</option>
                    <option value={10}>10</option>
                  </select>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-3">
                {results && (
                  <button
                    onClick={clearResults}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    Clear
                  </button>
                )}
                
                {isResearching ? (
                  <button
                    onClick={stopResearch}
                    className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-2"
                  >
                    <Pause className="w-4 h-4" />
                    <span>Stop Research</span>
                  </button>
                ) : (
                  <button
                    onClick={startResearch}
                    disabled={!query.trim()}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                  >
                    <Play className="w-4 h-4" />
                    <span>Start Research</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="text-red-800 font-medium">Research Error</span>
            </div>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        )}

        {/* Progress Display */}
        {(isResearching || researchStatus) && (
          <ResearchProgress 
            status={researchStatus}
            isActive={isResearching}
          />
        )}

        {/* Results Display */}
        {results && (
          <ResearchResults 
            results={results}
            query={query}
          />
        )}

        {/* Research History */}
        {!isResearching && !results && (
          <ResearchHistory 
            onSelectQuery={(selectedQuery) => setQuery(selectedQuery)}
          />
        )}
      </div>
    </div>
  );
};

export default ResearchInterface;
```

### 2. Research Progress Component

**src/components/research/ResearchProgress.jsx:**
```jsx
import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  CheckCircle, 
  Loader2, 
  Search, 
  FileText, 
  Users, 
  BarChart3,
  AlertTriangle 
} from 'lucide-react';

const ResearchProgress = ({ status, isActive }) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (isActive) {
      const interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [isActive, startTime]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusInfo = () => {
    if (!status) return { stage: 'Initializing', progress: 0 };

    switch (status.status) {
      case 'started':
        return { stage: 'Planning Research', progress: 10 };
      case 'planning':
        return { stage: 'Creating Research Plan', progress: 20 };
      case 'executing':
        return { stage: 'Agents Researching', progress: 40 };
      case 'synthesizing':
        return { stage: 'Synthesizing Results', progress: 80 };
      case 'citing':
        return { stage: 'Adding Citations', progress: 90 };
      case 'completed':
        return { stage: 'Research Complete', progress: 100 };
      case 'failed':
        return { stage: 'Research Failed', progress: 0 };
      default:
        return { stage: 'Processing', progress: 30 };
    }
  };

  const { stage, progress } = getStatusInfo();

  // Mock agent activities for demonstration
  const agentActivities = [
    { id: 1, name: 'Search Agent Alpha', status: 'searching', task: 'Finding recent medical AI studies' },
    { id: 2, name: 'Search Agent Beta', status: 'analyzing', task: 'Analyzing FDA approvals' },
    { id: 3, name: 'Search Agent Gamma', status: 'completed', task: 'Gathering hospital statistics' }
  ];

  const getAgentIcon = (agentStatus) => {
    switch (agentStatus) {
      case 'searching':
        return <Search className="w-4 h-4 text-blue-500 animate-pulse" />;
      case 'analyzing':
        return <BarChart3 className="w-4 h-4 text-orange-500 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {isActive ? (
            <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
          ) : status?.status === 'completed' ? (
            <CheckCircle className="w-6 h-6 text-green-500" />
          ) : status?.status === 'failed' ? (
            <AlertTriangle className="w-6 h-6 text-red-500" />
          ) : (
            <Clock className="w-6 h-6 text-gray-500" />
          )}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{stage}</h3>
            <p className="text-sm text-gray-600">
              {status?.message || 'Research in progress...'}
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-sm text-gray-500">Elapsed Time</div>
          <div className="text-lg font-mono font-semibold text-gray-900">
            {formatTime(elapsedTime)}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Research Stages */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        {[
          { stage: 'Plan', icon: FileText, completed: progress >= 20 },
          { stage: 'Search', icon: Search, completed: progress >= 40 },
          { stage: 'Analyze', icon: BarChart3, completed: progress >= 60 },
          { stage: 'Synthesize', icon: Users, completed: progress >= 80 },
          { stage: 'Complete', icon: CheckCircle, completed: progress >= 100 }
        ].map((item, index) => (
          <div 
            key={index}
            className={`flex flex-col items-center p-3 rounded-lg border-2 transition-colors ${
              item.completed 
                ? 'border-green-200 bg-green-50 text-green-700' 
                : progress > (index * 20) 
                  ? 'border-blue-200 bg-blue-50 text-blue-700' 
                  : 'border-gray-200 bg-gray-50 text-gray-500'
            }`}
          >
            <item.icon className="w-5 h-5 mb-1" />
            <span className="text-xs font-medium">{item.stage}</span>
          </div>
        ))}
      </div>

      {/* Agent Activities */}
      {isActive && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <Users className="w-4 h-4 mr-2" />
            Agent Activities
          </h4>
          <div className="space-y-2">
            {agentActivities.map((agent) => (
              <div 
                key={agent.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  {getAgentIcon(agent.status)}
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {agent.name}
                    </div>
                    <div className="text-xs text-gray-600">
                      {agent.task}
                    </div>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  agent.status === 'completed' 
                    ? 'bg-green-100 text-green-800'
                    : agent.status === 'failed'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-blue-100 text-blue-800'
                }`}>
                  {agent.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stats Summary */}
      {(status?.plan || status?.agents) && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-semibold text-gray-900">
                {status?.agents?.length || 3}
              </div>
              <div className="text-xs text-gray-500">Active Agents</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-gray-900">
                {status?.sources_found || '...'}
              </div>
              <div className="text-xs text-gray-500">Sources Found</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-gray-900">
                {status?.tokens_used || '...'}
              </div>
              <div className="text-xs text-gray-500">Tokens Used</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResearchProgress;
```

### 3. Research Results Component

**src/components/research/ResearchResults.jsx:**
```jsx
import React, { useState } from 'react';
import { 
  FileText, 
  Download, 
  ExternalLink, 
  Copy, 
  Share2, 
  BookOpen,
  BarChart3,
  Clock,
  Users,
  CheckCircle,
  Eye,
  Maximize2,
  ChevronDown,
  ChevronRight
} from 'lucide-react';

const ResearchResults = ({ results, query }) => {
  const [activeTab, setActiveTab] = useState('report');
  const [expandedSection, setExpandedSection] = useState(null);
  const [showFullReport, setShowFullReport] = useState(false);

  const handleCopyReport = () => {
    navigator.clipboard.writeText(results.report);
    // You could add a toast notification here
  };

  const handleDownloadReport = () => {
    const blob = new Blob([results.report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-report-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const ReportSection = ({ children, title, isExpanded, onToggle }) => (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 bg-gray-50 text-left flex items-center justify-between hover:bg-gray-100 transition-colors"
      >
        <span className="font-medium text-gray-900">{title}</span>
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-500" />
        )}
      </button>
      {isExpanded && (
        <div className="p-4 bg-white">
          {children}
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Research Complete
              </h2>
              <p className="text-sm text-gray-600">
                Query: {query}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopyReport}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title="Copy report"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              onClick={handleDownloadReport}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title="Download report"
            >
              <Download className="w-4 h-4" />
            </button>
            <button
              onClick={() => setShowFullReport(!showFullReport)}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title="Full screen"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {results.sources_used?.length || 0}
            </div>
            <div className="text-xs text-gray-500">Sources</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {results.total_tokens_used?.toLocaleString() || 0}
            </div>
            <div className="text-xs text-gray-500">Tokens</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {formatTime(results.execution_time)}
            </div>
            <div className="text-xs text-gray-500">Duration</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {results.subagent_count || 0}
            </div>
            <div className="text-xs text-gray-500">Agents</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-6 border-b border-gray-200">
        <div className="flex space-x-6">
          {[
            { id: 'report', label: 'Research Report', icon: FileText },
            { id: 'sources', label: 'Sources', icon: ExternalLink },
            { id: 'citations', label: 'Citations', icon: BookOpen },
            { id: 'analytics', label: 'Analytics', icon: BarChart3 }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-3 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'report' && (
          <div className="space-y-4">
            {/* Report Content */}
            <div 
              className={`prose max-w-none ${
                showFullReport ? 'max-h-none' : 'max-h-96 overflow-y-auto'
              }`}
            >
              <div 
                className="text-gray-800 whitespace-pre-wrap"
                dangerouslySetInnerHTML={{
                  __html: results.report.replace(/\n/g, '<br/>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                }}
              />
            </div>
            
            {!showFullReport && results.report.length > 2000 && (
              <button
                onClick={() => setShowFullReport(true)}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Show full report
              </button>
            )}
          </div>
        )}

        {activeTab === 'sources' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                Sources Used ({results.sources_used?.length || 0})
              </h3>
            </div>
            
            <div className="grid gap-4">
              {results.sources_used?.map((source, index) => (
                <div 
                  key={index}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-1">
                        {source.title}
                      </h4>
                      <p className="text-sm text-gray-600 mb-2">
                        {source.snippet}
                      </p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>Relevance: {Math.round((source.relevance_score || 0) * 100)}%</span>
                      </div>
                    </div>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-4 p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              )) || (
                <div className="text-center text-gray-500 py-8">
                  No sources available
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'citations' && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">
              Citations ({results.citations?.length || 0})
            </h3>
            
            <div className="space-y-3">
              {results.citations?.map((citation, index) => (
                <div 
                  key={index}
                  className="border-l-4 border-blue-200 pl-4 py-2"
                >
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      [{citation.index}]
                    </span>
                    <span className="font-medium text-gray-900">
                      {citation.title}
                    </span>
                  </div>
                  <a 
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-700 flex items-center space-x-1"
                  >
                    <span>{citation.url}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                  {citation.times_cited && (
                    <div className="text-xs text-gray-500 mt-1">
                      Cited {citation.times_cited} time{citation.times_cited !== 1 ? 's' : ''}
                    </div>
                  )}
                </div>
              )) || (
                <div className="text-center text-gray-500 py-8">
                  No citations available
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Research Analytics</h3>
            
            {/* Research Metadata */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Clock className="w-4 h-4 mr-2" />
                  Execution Details
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Started:</span>
                    <span className="text-gray-900">{formatDate(results.created_at)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Duration:</span>
                    <span className="text-gray-900">{formatTime(results.execution_time)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Research ID:</span>
                    <span className="text-gray-900 font-mono text-xs">{results.research_id}</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Users className="w-4 h-4 mr-2" />
                  Agent Performance
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Agents Used:</span>
                    <span className="text-gray-900">{results.subagent_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Tokens:</span>
                    <span className="text-gray-900">{results.total_tokens_used?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg. per Agent:</span>
                    <span className="text-gray-900">
                      {Math.round(results.total_tokens_used / results.subagent_count).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Report Sections */}
            {results.report_sections && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Report Structure</h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="space-y-1">
                    {results.report_sections.map((section, index) => (
                      <div key={index} className="text-sm text-gray-700">
                        {index + 1}. {section}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchResults;
```

### 4. Research History Component

**src/components/research/ResearchHistory.jsx:**
```jsx
import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Search, 
  FileText, 
  ExternalLink,
  Trash2,
  RefreshCw 
} from 'lucide-react';

const ResearchHistory = ({ onSelectQuery }) => {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      // Mock history data - in real implementation, this would fetch from your API
      const mockHistory = [
        {
          id: '1',
          query: 'What are the latest breakthroughs in AI-powered medical diagnosis in 2025?',
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          status: 'completed',
          sources_count: 15,
          duration: 180
        },
        {
          id: '2',
          query: 'How is quantum computing affecting financial modeling?',
          timestamp: new Date(Date.now() - 172800000).toISOString(),
          status: 'completed',
          sources_count: 23,
          duration: 240
        },
        {
          id: '3',
          query: 'Latest developments in renewable energy storage technologies',
          timestamp: new Date(Date.now() - 259200000).toISOString(),
          status: 'completed',
          sources_count: 18,
          duration: 195
        }
      ];

      setHistory(mockHistory);
    } catch (error) {
      console.error('Error loading history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 48) return 'Yesterday';
    return date.toLocaleDateString();
  };

  const deleteHistoryItem = (id) => {
    setHistory(prev => prev.filter(item => item.id !== id));
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="w-6 h-6 text-gray-400 animate-spin" />
          <span className="ml-2 text-gray-600">Loading research history...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            Recent Research
          </h3>
          <button
            onClick={loadHistory}
            className="text-gray-600 hover:text-gray-800 p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {history.length === 0 ? (
        <div className="p-8 text-center">
          <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h4 className="text-lg font-medium text-gray-900 mb-2">No Research History</h4>
          <p className="text-gray-600">
            Start your first research query to see results here.
          </p>
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {history.map((item) => (
            <div 
              key={item.id}
              className="p-6 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <button
                    onClick={() => onSelectQuery(item.query)}
                    className="text-left w-full group"
                  >
                    <h4 className="text-base font-medium text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-2">
                      {item.query}
                    </h4>
                  </button>
                  
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                    <span className="flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {formatDate(item.timestamp)}
                    </span>
                    <span className="flex items-center">
                      <FileText className="w-3 h-3 mr-1" />
                      {item.sources_count} sources
                    </span>
                    <span className="flex items-center">
                      <Search className="w-3 h-3 mr-1" />
                      {formatTime(item.duration)}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                    item.status === 'completed' 
                      ? 'bg-green-100 text-green-800'
                      : item.status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {item.status}
                  </span>
                  
                  <button
                    onClick={() => deleteHistoryItem(item.id)}
                    className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  
                  <button className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors">
                    <ExternalLink className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ResearchHistory;
```

### 5. API Service for Research

**src/services/research.js:**
```javascript
import api from './api';

export const researchService = {
  // Start new research
  startResearch: (query, maxSubagents = 3, maxIterations = 5) => 
    api.post('/research/start', {
      query,
      max_subagents: maxSubagents,
      max_iterations: maxIterations
    }),
  
  // Get research status
  getResearchStatus: (researchId) => 
    api.get(`/research/${researchId}/status`),
  
  // Get research result
  getResearchResult: (researchId) => 
    api.get(`/research/${researchId}/result`),
  
  // Run demo research
  runDemo: () => 
    api.post('/research/demo'),
  
  // Test citations
  testCitations: () => 
    api.post('/research/test-citations'),
  
  // Get research history (mock - implement based on your needs)
  getHistory: () => 
    Promise.resolve({
      data: {
        history: []
      }
    })
};
```

### 6. Main Research Page

**src/pages/Research.jsx:**
```jsx
import React from 'react';
import ResearchInterface from '../components/research/ResearchInterface';
import Breadcrumb from '../components/layout/Breadcrumb';

const Research = () => {
  const breadcrumbs = [
    { label: 'Your projects', path: '/' },
    { label: 'Research', path: '/research' }
  ];

  return (
    <div>
      <Breadcrumb items={breadcrumbs} />
      <ResearchInterface />
    </div>
  );
};

export default Research;
```

### 7. Route Configuration

Add to your **src/App.jsx:**
```jsx
import Research from './pages/Research';

// Add to your routes
<Route path="/research" element={<Research />} />
```

## 🎯 Key Features Implemented

### ✅ Async Research Processing
- Non-blocking research initiation
- Real-time status polling
- Progress tracking with visual indicators
- Agent activity monitoring

### ✅ Comprehensive Progress Display
- Multi-stage progress visualization
- Individual agent status tracking
- Real-time statistics (tokens, sources, time)
- Elapsed time counter

### ✅ Rich Results Display
- Tabbed interface (Report, Sources, Citations, Analytics)
- Downloadable reports
- Citation management
- Source verification

### ✅ User Experience
- Research history
- Query suggestions
- Configurable parameters
- Error handling and recovery

### ✅ Production Ready
- Proper error handling
- Loading states
- Responsive design
- Accessibility considerations

This implementation provides a complete research interface that matches the multi-agent system described in the API documentation, with full async support and comprehensive progress tracking.