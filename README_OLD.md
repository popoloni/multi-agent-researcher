# Multi-Agent Research System

A comprehensive implementation of Anthropic's Multi-Agent Research System that outperforms single-agent workflows by 90%. This system uses a lead agent to orchestrate multiple specialized search subagents working in parallel to conduct thorough research.

## Features

- **Lead Agent Orchestration**: Coordinates research strategy and delegates tasks
- **Parallel Search Subagents**: Multiple agents working simultaneously on different aspects
- **Intelligent Citation System**: Automatically adds proper citations to research reports
- **Memory Persistence**: Maintains context across research sessions
- **REST API**: FastAPI-based interface for easy integration
- **Comprehensive Error Handling**: Robust failure recovery and graceful degradation

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Lead Agent    │────│ Search Subagent │────│ Citation Agent  │
│                 │    │                 │    │                 │
│ • Strategy      │    │ • Web Search    │    │ • Add Citations │
│ • Coordination  │    │ • Content Parse │    │ • Bibliography  │
│ • Synthesis     │    │ • Relevance     │    │ • Source Match  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Memory Store   │
                    │                 │
                    │ • Context       │
                    │ • Results       │
                    │ • State Mgmt    │
                    └─────────────────┘
```

## Installation

1. **Clone and setup environment:**
```bash
git clone <repository>
cd multi-agent-researcher
python3 -m venv researcher-venv
source researcher-venv/bin/activate  # On Windows: researcher-venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
# Edit .env file
ANTHROPIC_API_KEY=your_anthropic_api_key_here
REDIS_URL=redis://localhost:6379
```

## Usage

### Starting the Server

```bash
python run.py
```

The server will start on `http://localhost:12000`

### API Endpoints

#### 1. Health Check
```bash
GET /
```

#### 2. Start Research
```bash
POST /research/start
Content-Type: application/json

{
    "query": "What are the latest developments in AI agents?",
    "max_subagents": 3,
    "max_iterations": 5
}
```

#### 3. Demo Research (Synchronous)
```bash
POST /research/demo
```

#### 4. Test Citations
```bash
POST /research/test-citations
```

### Python API Usage

```python
from app.models.schemas import ResearchQuery
from app.agents.lead_agent import LeadResearchAgent

# Create research query
query = ResearchQuery(
    query="What are the top AI agent companies in 2025?",
    max_subagents=3,
    max_iterations=5
)

# Run research
lead_agent = LeadResearchAgent()
result = await lead_agent.conduct_research(query)

print(f"Report: {result.report}")
print(f"Sources: {len(result.sources_used)}")
print(f"Citations: {len(result.citations)}")
```

## Testing

Run the comprehensive test suite:

```bash
python test_client.py
```

This will test:
- Citation Agent functionality
- Search Subagent operations
- Full research pipeline
- API endpoints (if server is running)

## System Components

### Lead Agent
- **Strategy Development**: Analyzes queries and creates research plans
- **Task Delegation**: Creates and assigns tasks to subagents
- **Result Synthesis**: Combines findings into coherent reports
- **Quality Control**: Ensures comprehensive coverage and accuracy

### Search Subagents
- **Specialized Search**: Focus on specific aspects of the research
- **Content Evaluation**: Assess source quality and relevance
- **Information Extraction**: Pull key facts and insights
- **Parallel Processing**: Work simultaneously for efficiency

### Citation Agent
- **Claim Identification**: Find statements requiring citations
- **Source Matching**: Link claims to appropriate sources
- **Citation Insertion**: Add proper academic-style citations
- **Bibliography Generation**: Create formatted reference lists

### Memory Store
- **Context Persistence**: Maintain state across operations
- **Result Caching**: Store completed research for retrieval
- **TTL Management**: Automatic cleanup of expired data
- **Distributed Support**: Ready for Redis integration

## Configuration

Key settings in `app/core/config.py`:

```python
# Model Configuration
LEAD_AGENT_MODEL = "claude-3-opus-20240229"
SUBAGENT_MODEL = "claude-3-sonnet-20240229"
CITATION_MODEL = "claude-3-haiku-20240307"

# Performance Settings
MAX_PARALLEL_SUBAGENTS = 5
MAX_THINKING_LENGTH = 50000
SEARCH_TIMEOUT = 30

# Memory Settings
MEMORY_TTL = 3600  # 1 hour
```

## Production Considerations

### Security
- API key management through environment variables
- Input validation and sanitization
- Rate limiting implementation
- CORS configuration for web integration

### Scalability
- Redis for distributed memory storage
- Async processing throughout
- Configurable parallelism limits
- Resource cleanup and management

### Monitoring
- Token usage tracking
- Execution time monitoring
- Error logging and alerting
- Performance metrics collection

### Error Handling
- Graceful degradation on failures
- Retry logic for transient issues
- Fallback responses for critical paths
- Comprehensive exception handling

## Example Output

```markdown
# AI Agent Market Analysis 2025

## Executive Summary
The AI agent market has experienced unprecedented growth in 2025, with multi-agent systems leading the transformation [1]. Key players have emerged with specialized offerings targeting different market segments [2].

## Market Leaders

### Anthropic
Anthropic leads the research and analysis segment with their Claude-based multi-agent systems [3]. Their approach focuses on coordinated research tasks that outperform single-agent workflows by 90% [1].

### OpenAI
OpenAI dominates the developer tools segment with GPT-based agents [4]. Their focus on code generation and software development has captured significant market share [5].

## References

[1] "Multi-Agent Systems Outperform Single Agents by 90%." Anthropic Research. https://anthropic.com/research/multi-agent-systems
[2] "AI Agent Market Analysis 2025." TechCrunch. https://techcrunch.com/2025/ai-agents-market
[3] "Claude Multi-Agent Coordination." Anthropic Blog. https://anthropic.com/blog/claude-coordination
[4] "GPT Agents for Developers." OpenAI Blog. https://openai.com/blog/gpt-agents
[5] "Developer Tools Market Share 2025." Industry Report. https://example.com/dev-tools-2025
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on Anthropic's Multi-Agent Research System blueprint
- Inspired by the 90% performance improvement findings
- Built with modern async Python patterns
- Designed for production scalability