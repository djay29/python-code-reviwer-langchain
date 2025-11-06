import re
from datetime import datetime
from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import MessagesState
from dotenv import load_dotenv
import boto3
from typing import Optional
from python_analyzer import *
from react_analyzer import *
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


def detect_language(code: str) -> str:
    """
    Automatically detect if code is Python or React (JavaScript/TypeScript).
    """
    # React/JS indicators
    react_patterns = [
        r'import\s+.*\s+from\s+[\'"]react[\'"]',
        r'useState|useEffect|useContext|useReducer',
        r'<\w+[\s>].*?>',  # JSX tags
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
    
    return "react" if react_score > python_score else "python"

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