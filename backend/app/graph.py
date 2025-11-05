from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import MessagesState
from dotenv import load_dotenv
import boto3
from typing import TypedDict, Optional, List
import json
from datetime import datetime

load_dotenv(".env")

# Initialize Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")


class AgentState(MessagesState):
    """Enhanced state to track all analysis results."""
    code_analysis: Optional[str] = None
    security_report: Optional[str] = None
    performance_report: Optional[str] = None
    best_practices_report: Optional[str] = None
    complexity_report: Optional[str] = None
    documentation_report: Optional[str] = None
    final_documentation: Optional[str] = None
    user_code: str
    metadata: Optional[dict] = None


# Initialize LLM
llm = ChatBedrockConverse(
    model="us.amazon.nova-premier-v1:0",
    max_tokens=32000,
    temperature=0.3  # Lower temperature for more consistent analysis
)


def code_analyzer(state: AgentState):
    """
    Analyzes code for PEP-8 compliance, syntax errors, and code quality.
    """
    user_code = state['user_code']

    prompt = f"""You are an expert Python code analyst specializing in PEP-8 standards and code quality.

Analyze the following Python code and provide a detailed report covering:

1. **PEP-8 Compliance Issues:**
   - Naming conventions (variables, functions, classes)
   - Indentation and whitespace
   - Line length (max 79 characters for code, 72 for docstrings)
   - Import statements organization
   - Blank lines usage

2. **Code Quality Issues:**
   - Syntax errors or potential runtime errors
   - Unused variables, imports, functions, or classes
   - Dead code or unreachable statements
   - Code duplication
   - Magic numbers (hardcoded values that should be constants)

3. **Type Hints:**
   - Missing or incomplete type annotations
   - Inconsistent type hint usage

4. **Error Handling:**
   - Missing exception handling
   - Overly broad exception catches
   - Unhandled edge cases

5. **Code Structure:**
   - Function and method length (should be concise)
   - Cyclomatic complexity
   - Single Responsibility Principle violations

Provide specific line references where possible and categorize issues by severity (Critical, High, Medium, Low).

**DO NOT provide corrected code. Only list issues.**

```python
{user_code}
```

Format your response as:
## Code Analysis Report

### Critical Issues
[List here]

### High Priority Issues
[List here]

### Medium Priority Issues
[List here]

### Low Priority Issues
[List here]

### Summary
[Brief summary of findings]
"""

    try:
        result = llm.invoke(prompt)
        return {"code_analysis": result.content}
    except Exception as e:
        return {"code_analysis": f"Error during code analysis: {str(e)}"}


def security_checker(state: AgentState):
    """
    Performs comprehensive security analysis of the code.
    """
    user_code = state['user_code']

    prompt = f"""You are a cybersecurity expert specializing in Python application security.

Conduct a thorough security audit of the following code, checking for:

1. **Injection Vulnerabilities:**
   - SQL injection risks
   - Command injection vulnerabilities
   - Code injection possibilities
   - Path traversal vulnerabilities

2. **Data Exposure:**
   - Hardcoded credentials, API keys, or secrets
   - Sensitive data logging
   - Information disclosure through error messages
   - Insecure data storage

3. **Authentication & Authorization:**
   - Weak authentication mechanisms
   - Missing authorization checks
   - Session management issues
   - Password handling problems

4. **Cryptography:**
   - Use of weak or deprecated cryptographic algorithms
   - Insecure random number generation
   - Improper certificate validation
   - Hardcoded encryption keys

5. **Input Validation:**
   - Missing input validation
   - Insufficient sanitization
   - Trust boundary violations

6. **Dependency Security:**
   - Use of known vulnerable libraries
   - Outdated dependencies

7. **API Security:**
   - Missing rate limiting
   - CORS misconfiguration
   - Insecure API endpoints

8. **File Operations:**
   - Unsafe file handling
   - Insecure file permissions
   - Unrestricted file uploads

Categorize findings by severity using OWASP standards (Critical, High, Medium, Low, Info).

**DO NOT provide corrected code. Only identify vulnerabilities.**

```python
{user_code}
```

Format your response as:
## Security Assessment Report

### Critical Vulnerabilities
[List with OWASP references if applicable]

### High Risk Issues
[List here]

### Medium Risk Issues
[List here]

### Low Risk Issues
[List here]

### Security Recommendations
[Summary of key recommendations]
"""

    try:
        result = llm.invoke(prompt)
        return {"security_report": result.content}
    except Exception as e:
        return {"security_report": f"Error during security check: {str(e)}"}


def performance_evaluator(state: AgentState):
    """
    Evaluates code for performance issues and optimization opportunities.
    """
    user_code = state['user_code']

    prompt = f"""You are a performance optimization expert for Python applications.

Analyze the following code for performance bottlenecks and optimization opportunities:

1. **Algorithm Efficiency:**
   - Time complexity issues (O(n²) or worse where better exists)
   - Space complexity problems
   - Inefficient algorithms or data structures

2. **Memory Management:**
   - Memory leaks
   - Unnecessary object creation
   - Large data structures in memory
   - Missing garbage collection considerations

3. **I/O Operations:**
   - Blocking I/O operations
   - Missing async/await where beneficial
   - Inefficient file handling
   - Unnecessary network calls

4. **Database Operations:**
   - N+1 query problems
   - Missing database indexing considerations
   - Inefficient queries
   - Missing connection pooling

5. **Loops and Iterations:**
   - Nested loops that could be optimized
   - Missing list comprehensions where applicable
   - Inefficient string concatenation

6. **Caching Opportunities:**
   - Repeated expensive computations
   - Missing memoization
   - Cacheable API calls

7. **Python-Specific:**
   - Missing use of built-in functions
   - Inefficient use of data structures (list vs set vs dict)
   - Global interpreter lock (GIL) considerations
   - Missing vectorization opportunities (NumPy)

8. **Concurrency:**
   - Missing parallelization opportunities
   - Threading vs multiprocessing considerations

Provide specific recommendations with estimated performance impact.

**DO NOT provide corrected code. Only identify issues.**

```python
{user_code}
```

Format your response as:
## Performance Analysis Report

### Critical Performance Issues
[High impact items]

### Optimization Opportunities
[Medium impact items]

### Minor Improvements
[Low impact items]

### Performance Summary
[Overall assessment and priority recommendations]
"""

    try:
        result = llm.invoke(prompt)
        return {"performance_report": result.content}
    except Exception as e:
        return {"performance_report": f"Error during performance evaluation: {str(e)}"}


def best_practices_checker(state: AgentState):
    """
    Checks adherence to Python best practices and design patterns.
    """
    user_code = state['user_code']

    prompt = f"""You are a Python best practices expert and software architect.

Review the code for adherence to Python best practices and design principles:

1. **Design Patterns:**
   - Appropriate use of design patterns
   - Anti-patterns present
   - SOLID principles violations

2. **Pythonic Code:**
   - Use of Python idioms
   - Context managers usage
   - Decorators where appropriate
   - Generator usage
   - List/dict/set comprehensions

3. **Code Organization:**
   - Module structure
   - Class design
   - Function cohesion
   - Separation of concerns

4. **Configuration Management:**
   - Hardcoded configuration
   - Environment variable usage
   - Configuration file handling

5. **Logging:**
   - Appropriate logging levels
   - Logging best practices
   - Missing critical logs

6. **Testing Considerations:**
   - Testability of code
   - Missing test hooks
   - Tight coupling issues

7. **Documentation:**
   - Missing or inadequate docstrings
   - Unclear variable names
   - Missing type hints
   - Complex logic without comments

8. **Dependencies:**
   - Dependency management
   - Import organization
   - Circular dependency risks

**DO NOT provide corrected code. Only identify areas for improvement.**

```python
{user_code}
```

Format your response as:
## Best Practices Review

### Design Issues
[List here]

### Pythonic Improvements
[List here]

### Code Organization
[List here]

### Recommendations
[Priority improvements]
"""

    try:
        result = llm.invoke(prompt)
        return {"best_practices_report": result.content}
    except Exception as e:
        return {"best_practices_report": f"Error during best practices check: {str(e)}"}


def complexity_analyzer(state: AgentState):
    """
    Analyzes code complexity and maintainability.
    """
    user_code = state['user_code']

    prompt = f"""You are a software engineering expert specializing in code maintainability.

Analyze the code complexity and maintainability:

1. **Cyclomatic Complexity:**
   - Functions with high complexity (>10)
   - Deeply nested conditionals
   - Complex boolean expressions

2. **Cognitive Complexity:**
   - Difficult to understand logic
   - Multiple levels of nesting
   - Complex control flow

3. **Code Duplication:**
   - Repeated code blocks
   - Similar functions that could be abstracted
   - Copy-paste programming indicators

4. **Function/Method Metrics:**
   - Functions that are too long (>50 lines)
   - Functions with too many parameters (>5)
   - Functions doing too many things

5. **Class Metrics:**
   - Classes with too many methods
   - God objects
   - Excessive inheritance depth

6. **Maintainability Issues:**
   - Code that's difficult to modify
   - Tight coupling
   - Hidden dependencies

Provide a maintainability score and specific areas that need refactoring.

**DO NOT provide corrected code. Only analyze complexity.**

```python
{user_code}
```

Format your response as:
## Complexity Analysis Report

### High Complexity Areas
[List here]

### Maintainability Concerns
[List here]

### Refactoring Priorities
[List here]

### Complexity Summary
[Overall assessment]
"""

    try:
        result = llm.invoke(prompt)
        return {"complexity_report": result.content}
    except Exception as e:
        return {"complexity_report": f"Error during complexity analysis: {str(e)}"}


def documentation_reviewer(state: AgentState):
    """
    Reviews code documentation quality.
    """
    user_code = state['user_code']

    prompt = f"""You are a technical documentation expert.

Review the code documentation quality:

1. **Docstrings:**
   - Missing module docstrings
   - Missing function/method docstrings
   - Missing class docstrings
   - Incomplete parameter descriptions
   - Missing return value descriptions
   - Missing exception documentation

2. **Comments:**
   - Missing explanatory comments for complex logic
   - Outdated or misleading comments
   - Over-commenting obvious code
   - TODO/FIXME items

3. **Type Annotations:**
   - Missing type hints
   - Incomplete type annotations
   - Complex types without proper documentation

4. **Code Clarity:**
   - Unclear variable names
   - Cryptic abbreviations
   - Missing context for magic numbers

5. **API Documentation:**
   - Public API without documentation
   - Missing usage examples
   - Undocumented side effects

**DO NOT provide corrected code. Only review documentation.**

```python
{user_code}
```

Format your response as:
## Documentation Review

### Missing Documentation
[List here]

### Documentation Quality Issues
[List here]

### Documentation Recommendations
[Priorities for improvement]
"""

    try:
        result = llm.invoke(prompt)
        return {"documentation_report": result.content}
    except Exception as e:
        return {"documentation_report": f"Error during documentation review: {str(e)}"}


def generate_report(state: AgentState):
    """
    Generates a comprehensive executive report combining all analyses.
    """
    user_code = state['user_code']
    code_analysis = state.get('code_analysis', 'Not available')
    security_report = state.get('security_report', 'Not available')
    performance_report = state.get('performance_report', 'Not available')
    best_practices = state.get('best_practices_report', 'Not available')
    complexity_report = state.get('complexity_report', 'Not available')
    documentation_report = state.get('documentation_report', 'Not available')

    prompt = f"""You are a senior technical reviewer creating an executive summary.

Based on the comprehensive analysis reports below, create a unified, well-structured report:

# Analysis Reports

## Code Quality Analysis
{code_analysis}

## Security Assessment
{security_report}

## Performance Evaluation
{performance_report}

## Best Practices Review
{best_practices}

## Complexity Analysis
{complexity_report}

## Documentation Review
{documentation_report}

# Your Task

Create a comprehensive executive report with:

1. **Executive Summary**
   - Overall code quality rating (1-10)
   - Key findings summary
   - Critical issues count by category

2. **Priority Action Items**
   - Top 5 critical issues to address immediately
   - Ranked by impact and effort

3. **Detailed Findings by Category**
   - Consolidate and organize findings
   - Remove redundancy
   - Provide context and impact

4. **Code Health Metrics**
   - Security score
   - Performance score
   - Maintainability score
   - Documentation score

5. **Recommendations**
   - Short-term fixes (< 1 day)
   - Medium-term improvements (1-5 days)
   - Long-term refactoring (> 5 days)

6. **Positive Aspects**
   - What the code does well
   - Good practices followed

**DO NOT provide corrected code in this report.**

Format the report in clear markdown with proper sections and subsections.
"""

    try:
        result = llm.invoke(prompt)
        
        # Add metadata
        metadata = {
            "review_date": datetime.now().isoformat(),
            "code_length": len(user_code),
            "review_sections": [
                "Code Quality",
                "Security",
                "Performance",
                "Best Practices",
                "Complexity",
                "Documentation"
            ]
        }
        
        return {
            "final_documentation": result.content,
            "metadata": metadata
        }
    except Exception as e:
        return {
            "final_documentation": f"Error generating final report: {str(e)}",
            "metadata": {"error": str(e)}
        }


def build_graph():
    """
    Builds the LangGraph workflow for comprehensive code review.
    """
    graph = StateGraph(AgentState)
    
    # Add all analysis nodes
    graph.add_node("code_analyzer", code_analyzer)
    graph.add_node("security_checker", security_checker)
    graph.add_node("performance_evaluator", performance_evaluator)
    graph.add_node("best_practices_checker", best_practices_checker)
    graph.add_node("complexity_analyzer", complexity_analyzer)
    graph.add_node("documentation_reviewer", documentation_reviewer)
    graph.add_node("generate_report", generate_report)

    # Run all analysis nodes in parallel from START
    graph.add_edge(START, "code_analyzer")
    graph.add_edge(START, "security_checker")
    graph.add_edge(START, "performance_evaluator")
    graph.add_edge(START, "best_practices_checker")
    graph.add_edge(START, "complexity_analyzer")
    graph.add_edge(START, "documentation_reviewer")

    # All analysis nodes flow to report generation
    graph.add_edge("code_analyzer", "generate_report")
    graph.add_edge("security_checker", "generate_report")
    graph.add_edge("performance_evaluator", "generate_report")
    graph.add_edge("best_practices_checker", "generate_report")
    graph.add_edge("complexity_analyzer", "generate_report")
    graph.add_edge("documentation_reviewer", "generate_report")
    
    # End after report generation
    graph.add_edge("generate_report", END)

    return graph.compile(checkpointer=MemorySaver())


def main(user_code: str = None, thread_id: str = "1", output_file: Optional[str] = None):
    """
    Main function to run the comprehensive code review.
    
    Args:
        user_code: Python code to review
        thread_id: Thread ID for conversation memory
        output_file: Optional file path to save the report
        
    Returns:
        dict: Complete review results
    """
    if not user_code:
        raise ValueError("user_code cannot be None or empty")
    
    print("Starting comprehensive code review...")
    print(f"Code length: {len(user_code)} characters")
    print("=" * 60)
    
    workflow = build_graph()
    initial_state = {"user_code": user_code}
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = workflow.invoke(initial_state, config=config)
        
        print("\nCode review completed!")
        print("=" * 60)
        
        # Optionally save report to file
        if output_file and result.get('final_documentation'):
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['final_documentation'])
            print(f"📄 Report saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error during code review: {str(e)}")
        raise
