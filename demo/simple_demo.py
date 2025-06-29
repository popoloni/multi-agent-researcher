#!/usr/bin/env python3
"""
Simple demonstration of working Kenobi agent features
"""
import asyncio
import sys
import os
import tempfile

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.kenobi_agent import KenobiAgent

async def main():
    """Simple demo of Kenobi functionality"""
    print("🚀 KENOBI AGENT - SIMPLE DEMO")
    print("=" * 50)
    
    # Test repository path
    repo_path = "/tmp/kenobi_test_repo"
    
    if not os.path.exists(repo_path):
        print("❌ Test repository not found. Creating a simple test...")
        
        # Create a simple test file
        os.makedirs(repo_path, exist_ok=True)
        test_file = os.path.join(repo_path, "simple_test.py")
        
        with open(test_file, 'w') as f:
            f.write('''
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self.result
    
    def multiply(self, value):
        self.result *= value
        return self.result

def main():
    calc = Calculator()
    calc.add(10)
    calc.multiply(2)
    print(f"Result: {calc.result}")

if __name__ == "__main__":
    main()
''')
        print(f"✓ Created test file: {test_file}")
    
    try:
        # Initialize Kenobi
        print("\n🤖 Initializing Kenobi Agent...")
        kenobi = KenobiAgent()
        print(f"✓ Agent: {kenobi.name}")
        print(f"✓ Model: {kenobi.model}")
        print(f"✓ Provider: {kenobi.provider}")
        
        # Analyze repository
        print(f"\n🔍 Analyzing repository: {repo_path}")
        analysis = await kenobi.analyze_repository(repo_path)
        
        print(f"\n✅ ANALYSIS RESULTS:")
        print(f"Repository: {analysis.repository.name}")
        print(f"Language: {analysis.repository.language.value}")
        print(f"Files analyzed: {len(analysis.files)}")
        print(f"Total elements: {sum(len(f.elements) for f in analysis.files)}")
        
        # Show file details
        for file_analysis in analysis.files:
            print(f"\n📄 File: {file_analysis.file_path}")
            print(f"   Elements: {len(file_analysis.elements)}")
            print(f"   Lines: {file_analysis.line_count}")
            print(f"   Size: {file_analysis.size_bytes} bytes")
            
            # Show elements
            for element in file_analysis.elements:
                print(f"   • {element.element_type.value}: {element.name}")
                if element.description:
                    print(f"     → {element.description}")
        
        # Show metrics
        print(f"\n📊 REPOSITORY METRICS:")
        for key, value in analysis.metrics.items():
            if key != 'ai_insights':
                print(f"   {key}: {value}")
        
        # Show AI insights if available
        if 'ai_insights' in analysis.metrics:
            insights = analysis.metrics['ai_insights']
            print(f"\n🧠 AI INSIGHTS:")
            for key, value in insights.items():
                print(f"   {key}: {value}")
        
        print(f"\n🎉 SUCCESS! Kenobi agent is fully operational!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())