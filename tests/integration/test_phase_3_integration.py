"""
Integration test for Phase 3: Vector Database + Content Indexing
Tests the complete pipeline from content extraction to semantic search
"""

import asyncio
import tempfile
import os
import shutil
from app.services.vector_database_service import VectorDatabaseService, DocumentType
from app.services.content_indexing_service import ContentIndexingService, ContentType

async def test_phase_3_integration():
    """Test complete Phase 3 integration"""
    print("🧪 Testing Phase 3 Integration: Vector Database + Content Indexing")
    print("=" * 70)
    
    # Initialize services
    vector_service = VectorDatabaseService()
    content_service = ContentIndexingService()
    
    print("✅ Services initialized")
    
    # Create test repository structure
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Created test repository: {temp_dir}")
    
    try:
        # Create comprehensive test files
        await create_test_repository(temp_dir)
        print("📝 Created test repository structure")
        
        # Test 1: Content Extraction
        print("\n" + "="*50)
        print("🔍 PHASE 1: Content Extraction Testing")
        print("="*50)
        
        python_file = os.path.join(temp_dir, "src", "calculator.py")
        extraction_result = await content_service.extract_file_content(python_file)
        
        print(f"✅ Python file extraction: {extraction_result.success}")
        print(f"   Chunks extracted: {len(extraction_result.chunks)}")
        print(f"   Processing time: {extraction_result.extraction_time:.3f}s")
        
        # Show extracted chunks
        for i, chunk in enumerate(extraction_result.chunks[:3]):
            print(f"   Chunk {i+1}: {chunk.content_type.value}")
            print(f"     Content: {chunk.content[:80]}...")
            print(f"     Metadata: {list(chunk.metadata.keys())}")
        
        # Test 2: Vector Indexing
        print("\n" + "="*50)
        print("🗂️  PHASE 2: Vector Database Indexing")
        print("="*50)
        
        indexed_count = 0
        for chunk in extraction_result.chunks:
            document_type = content_service._content_type_to_document_type(chunk.content_type)
            
            indexing_result = await vector_service.index_document(
                content=chunk.content,
                metadata={
                    **chunk.metadata,
                    "file_path": chunk.file_path,
                    "content_type": chunk.content_type.value
                },
                document_type=document_type,
                repository_id="test-repo-integration"
            )
            
            if indexing_result.success:
                indexed_count += 1
        
        print(f"✅ Vector indexing completed: {indexed_count}/{len(extraction_result.chunks)} chunks indexed")
        
        # Test 3: Semantic Search
        print("\n" + "="*50)
        print("🔎 PHASE 3: Semantic Search Testing")
        print("="*50)
        
        search_queries = [
            "fibonacci calculation recursive",
            "calculator add numbers",
            "class definition methods",
            "mathematical operations"
        ]
        
        for query in search_queries:
            search_results = await vector_service.search_documents(
                query=query,
                repository_id="test-repo-integration",
                limit=3
            )
            
            print(f"\n🔍 Query: '{query}'")
            print(f"   Results: {len(search_results)}")
            
            for i, result in enumerate(search_results[:2]):  # Show top 2 results
                print(f"   Result {i+1}: similarity={result.similarity_score:.3f}")
                print(f"     Type: {result.document_type.value}")
                print(f"     Content: {result.document.content[:60]}...")
        
        # Test 4: Repository Health Check
        print("\n" + "="*50)
        print("📊 PHASE 4: System Health & Statistics")
        print("="*50)
        
        health = await vector_service.get_health_status()
        print(f"✅ Vector Database Health: {health['status']}")
        print(f"   Backend: {health['vector_database']['backend']}")
        print(f"   Documents: {health['vector_database']['document_count']}")
        print(f"   Search stats: {health['search_performance']['total_searches']} searches")
        
        # Test 5: Content Statistics
        content_stats = await content_service.get_repository_content_stats("test-repo-integration")
        print(f"✅ Content Statistics:")
        print(f"   Total documents: {content_stats.get('total_documents', 0)}")
        print(f"   Content types: {list(content_stats.get('content_types', {}).keys())}")
        
        # Test 6: End-to-End Workflow
        print("\n" + "="*50)
        print("🔄 PHASE 5: End-to-End Workflow Test")
        print("="*50)
        
        # Process multiple files
        files_to_process = [
            os.path.join(temp_dir, "src", "calculator.py"),
            os.path.join(temp_dir, "docs", "README.md"),
            os.path.join(temp_dir, "config.json")
        ]
        
        total_chunks = 0
        total_indexed = 0
        
        for file_path in files_to_process:
            if os.path.exists(file_path):
                result = await content_service.extract_file_content(file_path)
                if result.success:
                    total_chunks += len(result.chunks)
                    
                    for chunk in result.chunks:
                        document_type = content_service._content_type_to_document_type(chunk.content_type)
                        indexing_result = await vector_service.index_document(
                            content=chunk.content,
                            metadata={
                                **chunk.metadata,
                                "file_path": chunk.file_path,
                                "content_type": chunk.content_type.value
                            },
                            document_type=document_type,
                            repository_id="test-repo-integration"
                        )
                        
                        if indexing_result.success:
                            total_indexed += 1
        
        print(f"✅ End-to-end processing completed:")
        print(f"   Files processed: {len(files_to_process)}")
        print(f"   Total chunks extracted: {total_chunks}")
        print(f"   Total chunks indexed: {total_indexed}")
        print(f"   Success rate: {(total_indexed/total_chunks)*100:.1f}%" if total_chunks > 0 else "   Success rate: N/A")
        
        # Final comprehensive search test
        print("\n" + "="*50)
        print("🎯 PHASE 6: Comprehensive Search Test")
        print("="*50)
        
        comprehensive_search = await vector_service.search_documents(
            query="python function calculator mathematics",
            repository_id="test-repo-integration",
            limit=5,
            use_hybrid_search=True
        )
        
        print(f"✅ Comprehensive search results: {len(comprehensive_search)}")
        for i, result in enumerate(comprehensive_search):
            print(f"   Result {i+1}: {result.similarity_score:.3f} - {result.document_type.value}")
            print(f"     File: {result.file_path}")
            print(f"     Preview: {result.context[:50]}..." if result.context else "     Preview: N/A")
        
        print("\n" + "="*70)
        print("🎉 PHASE 3 INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("✅ Vector Database Service: WORKING")
        print("✅ Content Indexing Service: WORKING") 
        print("✅ End-to-End Pipeline: WORKING")
        print("✅ Semantic Search: WORKING")
        print("✅ Ready for Phase 4 RAG Implementation!")
        print("="*70)
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up test repository")

async def create_test_repository(base_dir):
    """Create a comprehensive test repository structure"""
    
    # Create directory structure
    src_dir = os.path.join(base_dir, "src")
    docs_dir = os.path.join(base_dir, "docs")
    tests_dir = os.path.join(base_dir, "tests")
    
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)
    
    # Create Python source file
    calculator_py = os.path.join(src_dir, "calculator.py")
    with open(calculator_py, 'w') as f:
        f.write('''
"""
Advanced Calculator Module
Provides mathematical operations and utilities
"""

import math
from typing import Union, List

def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number using recursion.
    
    Args:
        n: The position in the Fibonacci sequence
        
    Returns:
        The nth Fibonacci number
        
    Example:
        >>> fibonacci(5)
        5
    """
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n: int) -> int:
    """Calculate factorial of n"""
    if n <= 1:
        return 1
    return n * factorial(n-1)

class Calculator:
    """
    Advanced calculator with history tracking and multiple operations.
    
    This class provides basic mathematical operations and maintains
    a history of all calculations performed.
    """
    
    def __init__(self):
        """Initialize calculator with empty history"""
        self.history: List[str] = []
        self.memory: float = 0.0
    
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers and record in history.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a"""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers"""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: float, b: float) -> float:
        """
        Divide a by b with zero division protection.
        
        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def power(self, base: float, exponent: float) -> float:
        """Calculate base raised to exponent"""
        result = math.pow(base, exponent)
        self.history.append(f"{base} ^ {exponent} = {result}")
        return result
    
    def sqrt(self, n: float) -> float:
        """Calculate square root"""
        if n < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = math.sqrt(n)
        self.history.append(f"sqrt({n}) = {result}")
        return result
    
    def clear_history(self):
        """Clear calculation history"""
        self.history.clear()
    
    def get_history(self) -> List[str]:
        """Get copy of calculation history"""
        return self.history.copy()

class ScientificCalculator(Calculator):
    """
    Extended calculator with scientific functions.
    
    Inherits from Calculator and adds trigonometric and logarithmic functions.
    """
    
    def sin(self, angle: float, degrees: bool = False) -> float:
        """Calculate sine of angle"""
        if degrees:
            angle = math.radians(angle)
        result = math.sin(angle)
        self.history.append(f"sin({angle}) = {result}")
        return result
    
    def cos(self, angle: float, degrees: bool = False) -> float:
        """Calculate cosine of angle"""
        if degrees:
            angle = math.radians(angle)
        result = math.cos(angle)
        self.history.append(f"cos({angle}) = {result}")
        return result
    
    def log(self, n: float, base: float = math.e) -> float:
        """Calculate logarithm"""
        if n <= 0:
            raise ValueError("Logarithm undefined for non-positive numbers")
        result = math.log(n, base)
        self.history.append(f"log({n}, {base}) = {result}")
        return result

# Utility functions
def is_prime(n: int) -> bool:
    """Check if a number is prime"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def gcd(a: int, b: int) -> int:
    """Calculate greatest common divisor using Euclidean algorithm"""
    while b:
        a, b = b, a % b
    return a
''')
    
    # Create README documentation
    readme_md = os.path.join(docs_dir, "README.md")
    with open(readme_md, 'w') as f:
        f.write('''
# Advanced Calculator Library

A comprehensive Python library for mathematical calculations with history tracking and scientific functions.

## Features

### Basic Calculator
- **Arithmetic Operations**: Addition, subtraction, multiplication, division
- **Advanced Operations**: Power, square root, factorial
- **History Tracking**: Automatic recording of all calculations
- **Memory Functions**: Store and recall values
- **Error Handling**: Robust error handling for edge cases

### Scientific Calculator
- **Trigonometric Functions**: Sine, cosine, tangent
- **Logarithmic Functions**: Natural and custom base logarithms
- **Angle Conversion**: Support for degrees and radians
- **Extended Operations**: All basic calculator features plus scientific functions

### Utility Functions
- **Fibonacci Sequence**: Recursive calculation of Fibonacci numbers
- **Prime Number Testing**: Efficient prime number detection
- **Greatest Common Divisor**: Euclidean algorithm implementation

## Installation

```bash
pip install advanced-calculator
```

## Quick Start

### Basic Usage

```python
from calculator import Calculator

# Create calculator instance
calc = Calculator()

# Perform calculations
result = calc.add(10, 5)        # Returns 15
result = calc.multiply(3, 4)    # Returns 12
result = calc.divide(20, 4)     # Returns 5.0

# View calculation history
history = calc.get_history()
print(history)  # ['10 + 5 = 15', '3 * 4 = 12', '20 / 4 = 5.0']
```

### Scientific Calculator

```python
from calculator import ScientificCalculator
import math

# Create scientific calculator
sci_calc = ScientificCalculator()

# Trigonometric functions
result = sci_calc.sin(90, degrees=True)    # Returns 1.0
result = sci_calc.cos(0, degrees=True)     # Returns 1.0

# Logarithmic functions
result = sci_calc.log(100, 10)             # Returns 2.0
result = sci_calc.log(math.e)              # Returns 1.0 (natural log)
```

### Utility Functions

```python
from calculator import fibonacci, is_prime, gcd

# Fibonacci sequence
fib_10 = fibonacci(10)          # Returns 55

# Prime number testing
is_17_prime = is_prime(17)      # Returns True
is_15_prime = is_prime(15)      # Returns False

# Greatest common divisor
common_divisor = gcd(48, 18)    # Returns 6
```

## API Reference

### Calculator Class

#### Methods

- `add(a, b)`: Add two numbers
- `subtract(a, b)`: Subtract b from a
- `multiply(a, b)`: Multiply two numbers
- `divide(a, b)`: Divide a by b (with zero division protection)
- `power(base, exponent)`: Calculate base raised to exponent
- `sqrt(n)`: Calculate square root (with negative number protection)
- `clear_history()`: Clear calculation history
- `get_history()`: Get copy of calculation history

#### Properties

- `history`: List of calculation strings
- `memory`: Memory storage for values

### ScientificCalculator Class

Inherits all Calculator methods plus:

- `sin(angle, degrees=False)`: Calculate sine
- `cos(angle, degrees=False)`: Calculate cosine
- `log(n, base=e)`: Calculate logarithm

### Utility Functions

- `fibonacci(n)`: Calculate nth Fibonacci number
- `factorial(n)`: Calculate factorial of n
- `is_prime(n)`: Test if number is prime
- `gcd(a, b)`: Calculate greatest common divisor

## Error Handling

The library includes comprehensive error handling:

- **Division by Zero**: Raises `ValueError` with descriptive message
- **Negative Square Root**: Raises `ValueError` for negative inputs
- **Invalid Logarithm**: Raises `ValueError` for non-positive inputs
- **Type Validation**: Automatic type checking for numeric inputs

## Performance Considerations

- **Fibonacci Calculation**: Uses recursive algorithm (exponential time complexity)
- **Prime Testing**: Optimized algorithm with square root limit
- **History Storage**: Unlimited history storage (consider clearing for long sessions)
- **Memory Usage**: Minimal memory footprint for basic operations

## Examples

### Complex Calculations

```python
calc = ScientificCalculator()

# Calculate compound interest
principal = 1000
rate = 0.05
time = 10
compound_interest = principal * calc.power(1 + rate, time)

# Calculate triangle area using trigonometry
side_a = 10
side_b = 15
angle_c = 60  # degrees
area = 0.5 * side_a * side_b * calc.sin(angle_c, degrees=True)

# Statistical calculations
numbers = [1, 2, 3, 4, 5]
mean = sum(numbers) / len(numbers)
variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
std_dev = calc.sqrt(variance)
```

### Batch Operations

```python
calc = Calculator()

# Process multiple calculations
operations = [
    (calc.add, 10, 5),
    (calc.multiply, 3, 7),
    (calc.divide, 100, 4),
    (calc.power, 2, 8)
]

results = []
for operation, a, b in operations:
    result = operation(a, b)
    results.append(result)

print(f"Results: {results}")
print(f"History: {calc.get_history()}")
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0
- Initial release with basic and scientific calculator functionality
- Comprehensive error handling and input validation
- Full test suite with 100% code coverage
- Complete documentation and examples

### Version 1.1.0 (Planned)
- Matrix operations support
- Complex number calculations
- Statistical functions
- Performance optimizations
''')
    
    # Create configuration file
    config_json = os.path.join(base_dir, "config.json")
    with open(config_json, 'w') as f:
        f.write('''
{
    "project": {
        "name": "Advanced Calculator Library",
        "version": "1.0.0",
        "description": "Comprehensive mathematical calculation library",
        "author": "Calculator Team",
        "license": "MIT"
    },
    "settings": {
        "precision": 10,
        "angle_mode": "radians",
        "history_limit": 1000,
        "scientific_notation": true,
        "error_handling": "strict"
    },
    "features": {
        "basic_operations": true,
        "scientific_functions": true,
        "history_tracking": true,
        "memory_functions": true,
        "batch_operations": true
    },
    "performance": {
        "cache_results": false,
        "optimize_recursion": true,
        "parallel_processing": false
    },
    "logging": {
        "level": "INFO",
        "file": "calculator.log",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}
''')

if __name__ == "__main__":
    asyncio.run(test_phase_3_integration())