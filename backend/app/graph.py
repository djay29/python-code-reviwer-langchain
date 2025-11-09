import re
from datetime import datetime
from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import MessagesState
from dotenv import load_dotenv
import boto3
from python_analyzer import *
from react_analyzer import *
from typing import Optional
from datetime import datetime
from extensions import AgentState
from langgraph.types import Send

def detect_language(code: str) -> str:
    """
    Automatically detect if code is Python or React (JavaScript/TypeScript).
    """
    # React/JS indicators
    react_patterns = [
        r'import\s+.*\s+from\s+[\'"]react[\'"]',
        r'useState|useEffect|useContext|useReducer',
        r'<\w+[\s>].*?>', 
        r'const\s+\w+\s*=\s*\(\s*\)\s*=>',
        r'function\s+\w+\s*\([^)]*\)\s*{',
        r'export\s+(default|const)',
        r'\.jsx?[\'"]',
        r'className=',
        r'props\.',
    ]
    
    # Python indicators
    python_patterns = [
        r'def\s+\w+\s*\(',
        r'class\s+\w+.*:',
        r'import\s+\w+',
        r'from\s+\w+\s+import',
        r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
        r'self\.',
        r'\.py[\'"]',
    ]
    
    react_score = sum(1 for pattern in react_patterns if re.search(pattern, code))
    python_score = sum(1 for pattern in python_patterns if re.search(pattern, code))
    
    language = "react" if react_score > python_score else "python"

    return {"language": language}

def generate_report(state: AgentState):
    """Generates comprehensive report combining all analyses."""
    language = state['language']
    user_code = state['user_code']
    code_analysis = state.get('code_analysis', 'Not available')
    security_report = state.get('security_report', 'Not available')
    performance_report = state.get('performance_report', 'Not available')
    best_practices = state.get('best_practices_report', 'Not available')
    complexity_report = state.get('complexity_report', 'Not available')
    documentation_report = state.get('documentation_report', 'Not available')
    react_specific = state.get('react_specific_report', 'Not analyzed')
    accessibility_report = state.get('accessibility_report', 'Not analyzed')

    sections = f"""
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
{documentation_report}"""

    if language == "react":
        sections += f"""

## React-Specific Analysis
{react_specific}

## Accessibility (a11y) Review
{accessibility_report}"""

    prompt = f"""You are a senior technical reviewer creating an executive summary for {language.upper()} code.

Based on the comprehensive analysis reports below, create a unified, well-structured report:

# Analysis Reports
{sections}

# Your Task

Create a comprehensive executive report with:

1. **Executive Summary**
    - Overall code quality rating (1-10)
    - Key findings summary
    - Critical issues count by category

    2. **Priority Action Items**
    - Top 10 critical issues to address immediately
    - Ranked by impact and effort

    3. **Detailed Findings by Category**
    - Consolidate and organize findings
    - Remove redundancy
    - Provide context and impact

    4. **Code Health Metrics**
    - Security score (1-10)
    - Performance score (1-10)
    - Maintainability score (1-10)
    - Documentation score (1-10)
    {"- Accessibility score (1-10)" if language == "react" else ""}

    5. **Recommendations**
    - Quick fixes (< 1 hour)
    - Short-term fixes (< 1 day)
    - Medium-term improvements (1-5 days)
    - Long-term refactoring (> 5 days)

    6. **Positive Aspects**
    - What the code does well
    - Good practices followed

    7. **Technology-Specific Insights**
    {"- React patterns and hooks usage" if language == "react" else "- Python-specific optimizations"}
    {"- Frontend performance considerations" if language == "react" else "- Backend optimization opportunities"}

**DO NOT provide corrected code in this report.**

Format the report in clear markdown with proper sections."""

    try:
        result = llm.invoke(prompt)
        
        metadata = {
            "review_date": datetime.now().isoformat(),
            "language": language,
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
        
        if language == "react":
            metadata["review_sections"].extend(["React Patterns", "Accessibility"])
        
        return {
            "final_documentation": result.content,
            "metadata": metadata
        }
    except Exception as e:
        return {
            "final_documentation": f"Error generating final report: {str(e)}",
            "metadata": {"error": str(e)}
        }

def python_node(code: str) -> dict:
    return {"language": "python"}

def react_node(code: str) -> dict:
    return {"language": "react"}

def python_parallel_node(state: AgentState):
    return[
        Send("python_code_reviwer",state),
        Send("python_security_checker",state),
        Send("python_performance_evaluator",state),
        Send("python_best_practices_checker",state),
        Send("python_complexity_analyzer",state),
        Send("python_documentation_reviewer",state)
    ]
    
def react_parallel_node(state: AgentState):
    return[
        Send("react_code_analyzer",state),
        Send("react_security_checker",state),
        Send("react_accessibility_checker",state),
        Send("react_performance_evaluator",state),
        Send("react_best_practices_checker",state),
        Send("react_complexity_analyzer",state),
        Send("react_documentation_reviewer",state),
        Send("react_specific_analyzer",state)
    ]
    
def create_workflow():
    graph = StateGraph(AgentState)

    graph.add_node("detect_language",detect_language)

    # graph.add_node("python_parallel_node",python_parallel_node)
    graph.add_node("python_node",python_node)
    graph.add_node("python_code_reviwer",python_code_analyzer)
    graph.add_node("python_security_checker",python_security_checker)
    graph.add_node("python_performance_evaluator",python_performance_evaluator)
    graph.add_node("python_best_practices_checker",python_best_practices_checker)
    graph.add_node("python_complexity_analyzer",python_complexity_analyzer)
    graph.add_node("python_documentation_reviewer",python_documentation_reviewer)

    # graph.add_node("react_parallel_node",react_parallel_node)
    graph.add_node("react_node",react_node)
    graph.add_node("react_code_analyzer",react_code_analyzer)
    graph.add_node("react_specific_analyzer",react_specific_analyzer)
    graph.add_node("react_security_checker",react_security_checker)
    graph.add_node("react_accessibility_checker",react_accessibility_checker)
    graph.add_node("react_performance_evaluator",react_performance_evaluator)
    graph.add_node("react_best_practices_checker",react_best_practices_checker)
    graph.add_node("react_complexity_analyzer",react_complexity_analyzer)
    graph.add_node("react_documentation_reviewer",react_documentation_reviewer)

    graph.add_node("generate_report",generate_report)

    graph.set_entry_point("detect_language")
    graph.add_conditional_edges(
        "detect_language",
        lambda x: x.get("language"),
        {
            "python":"python_node",
            "react":"react_node",
        }
    )

    graph.add_conditional_edges(
        "python_node",
        python_parallel_node,
        ['python_complexity_analyzer','python_code_reviwer','python_documentation_reviewer','python_performance_evaluator','python_security_checker','python_best_practices_checker']
    )

    graph.add_conditional_edges(
        "react_node",
        react_parallel_node,
        ['react_accessibility_checker','react_best_practices_checker','react_code_analyzer','react_complexity_analyzer','react_documentation_reviewer','react_performance_evaluator','react_security_checker','react_specific_analyzer']
    )

    graph.add_edge("python_complexity_analyzer", "generate_report")
    graph.add_edge("python_code_reviwer", "generate_report")
    graph.add_edge("python_documentation_reviewer", "generate_report")
    graph.add_edge("python_performance_evaluator", "generate_report")
    graph.add_edge("python_security_checker", "generate_report")
    graph.add_edge("python_best_practices_checker", "generate_report")


    graph.add_edge("react_specific_analyzer", "generate_report")
    graph.add_edge("react_security_checker", "generate_report")
    graph.add_edge("react_accessibility_checker", "generate_report")
    graph.add_edge("react_performance_evaluator", "generate_report")
    graph.add_edge("react_best_practices_checker", "generate_report")
    graph.add_edge("react_complexity_analyzer", "generate_report")
    graph.add_edge("react_documentation_reviewer", "generate_report")
    graph.add_edge("react_code_analyzer", "generate_report")

    graph.add_edge("generate_report",END)

    return graph.compile()