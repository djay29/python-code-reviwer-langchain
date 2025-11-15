from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import MessagesState
from dotenv import load_dotenv
import boto3

from app.utils.extensions import AgentState
load_dotenv(".env")

# Initialize Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

llm = ChatBedrockConverse(
   model="us.amazon.nova-premier-v1:0",
   max_tokens=32000,
   temperature=0.3,  # Lower temperature for more consistent analysis
   bedrock_client=bedrock_client,
   region_name="us-east-1"
   )


def react_code_analyzer(state: AgentState):
   """Analyzes React code for best practices and quality."""
   user_code = state['user_code']

   prompt = f"""You are an expert React/JavaScript/TypeScript code analyst.

Analyze the following React code and provide a detailed report covering:

1. **Code Style & Standards:**
   - ESLint and Prettier compliance
   - Naming conventions (PascalCase for components, camelCase for functions/variables)
   - File organization and structure
   - Import/export statements organization
   - Consistent code formatting

2. **JavaScript/TypeScript Quality:**
   - Syntax errors or potential runtime errors
   - Unused variables, imports, functions
   - Console.log statements left in code
   - Debugging code not removed
   - Proper use of const/let (no var)
   - Arrow function consistency

3. **Type Safety (TypeScript):**
   - Missing type annotations
   - Use of 'any' type
   - Inconsistent type definitions
   - Missing interface/type definitions
   - Prop types validation

4. **Error Handling:**
   - Missing try-catch blocks
   - Unhandled promise rejections
   - Missing error boundaries
   - Poor error messages

5. **Code Structure:**
   - Component size (should be < 300 lines)
   - Function complexity
   - Code duplication
   - Magic numbers/strings

Provide specific line references and categorize by severity (Critical, High, Medium, Low).

**DO NOT provide corrected code. Only list issues.**

```javascript
{user_code}
```

Format your response with clear sections and severity levels."""

   try:
      result = llm.invoke(prompt)
      return {"code_analysis": result.content}
   except Exception as e:
      return {"code_analysis": f"Error during code analysis: {str(e)}"}


def react_specific_analyzer(state: AgentState):
   """Analyzes React-specific patterns, hooks, and best practices."""
   user_code = state['user_code']

   prompt = f"""You are a React expert specializing in React patterns, hooks, and component architecture.

Analyze the following React code for React-specific issues:

1. **Component Architecture:**
   - Component composition issues
   - Props drilling (passing props through multiple levels)
   - Component responsibility violations
   - Smart vs Dumb component separation
   - Component reusability
   - Missing component extraction opportunities

2. **React Hooks Usage:**
   - Incorrect hook usage (violating rules of hooks)
   - Missing dependency arrays in useEffect/useCallback/useMemo
   - Stale closure issues
   - Unnecessary re-renders from hooks
   - Custom hooks that could be extracted
   - useState vs useReducer decisions
   - Missing useCallback for function props
   - Missing useMemo for expensive calculations

3. **State Management:**
   - Unnecessary state
   - State initialization issues
   - Derived state that should be computed
   - Missing state lifting
   - Prop drilling that needs context/Redux
   - Context API misuse
   - Local vs global state decisions

4. **Component Lifecycle:**
   - useEffect cleanup functions missing
   - Effect dependency issues
   - Infinite loops in effects
   - Race conditions
   - Memory leaks from subscriptions

5. **JSX Best Practices:**
   - Key prop issues in lists
   - Inline function definitions causing re-renders
   - Conditional rendering patterns
   - Fragment usage
   - Event handler binding

6. **Props & Data Flow:**
   - Missing prop validation
   - Prop mutation (should be immutable)
   - Callback prop patterns
   - Children prop usage
   - Render props patterns
   - Missing default props

7. **React Patterns:**
   - Higher-Order Components (HOC) issues
   - Render props issues
   - Compound components opportunities
   - Controlled vs uncontrolled components
   - Container/Presentational pattern violations

8. **React 18+ Features:**
   - Missing Suspense boundaries
   - Concurrent rendering issues
   - Transition API opportunities
   - Server Components considerations (if applicable)

**DO NOT provide corrected code. Only identify issues.**

```javascript
{user_code}
```

Format your response as:
## React-Specific Analysis

### Critical React Issues
[Issues that will cause bugs or major problems]

### Hook-Related Issues
[useEffect, useState, custom hooks problems]

### State Management Issues
[State and data flow problems]

### Component Architecture Issues
[Structure and design problems]

### JSX Issues
[JSX-specific problems]

### React Best Practices Violations
[Pattern and convention issues]

### Recommendations
[Priority improvements for React code]"""

   try:
      result = llm.invoke(prompt)
      return {"react_specific_report": result.content}
   except Exception as e:
      return {"react_specific_report": f"Error during React analysis: {str(e)}"}


def react_security_checker(state: AgentState):
   """Performs security analysis for React applications."""
   user_code = state['user_code']

   prompt = f"""You are a web application security expert specializing in React and frontend security.

Conduct a thorough security audit of the following React code:

1. **Cross-Site Scripting (XSS):**
   - dangerouslySetInnerHTML usage
   - Unescaped user input in JSX
   - innerHTML usage
   - eval() or Function() constructor usage
   - User-controlled URLs in href/src

2. **Authentication & Authorization:**
   - Exposed authentication tokens
   - Insecure token storage (localStorage vs httpOnly cookies)
   - Missing authentication checks
   - Client-side only authorization (should be server-side too)
   - JWT handling issues

3. **Data Exposure:**
   - Hardcoded API keys or secrets
   - Sensitive data in client-side code
   - Console.log with sensitive information
   - Exposed environment variables
   - PII handling issues

4. **API Security:**
   - Missing CSRF protection
   - Insecure API calls
   - Missing request validation
   - Exposed API endpoints in code
   - Missing rate limiting considerations
   - CORS misconfiguration indicators

5. **Input Validation:**
   - Missing client-side validation (UX issue)
   - Trust in client-side validation only (security issue)
   - Insufficient sanitization
   - File upload validation issues

6. **Third-Party Dependencies:**
   - Use of vulnerable npm packages
   - Outdated dependencies
   - Suspicious package imports
   - Missing dependency security checks

7. **Secure Communication:**
   - HTTP instead of HTTPS
   - Insecure WebSocket connections
   - Missing security headers consideration

8. **Session Management:**
   - Insecure session handling
   - Missing session timeout
   - Session fixation risks

9. **Content Security:**
   - Missing Content Security Policy considerations
   - Iframe security issues
   - postMessage security

Categorize findings by severity (Critical, High, Medium, Low).

**DO NOT provide corrected code. Only identify vulnerabilities.**

```javascript
{user_code}
```"""

   try:
      result = llm.invoke(prompt)
      return {"security_report": result.content}
   except Exception as e:
      return {"security_report": f"Error during security check: {str(e)}"}


def react_accessibility_checker(state: AgentState):
   """Checks React code for accessibility (a11y) issues."""
   user_code = state['user_code']

   prompt = f"""You are a web accessibility (a11y) expert specializing in React applications.

Review the following React code for accessibility issues:

1. **Semantic HTML:**
   - Use of div/span instead of semantic elements
   - Missing landmark elements (header, nav, main, footer)
   - Incorrect heading hierarchy
   - Missing or incorrect ARIA roles
   - Button vs div onClick issues

2. **ARIA Attributes:**
   - Missing aria-label/aria-labelledby
   - Missing aria-describedby
   - Incorrect ARIA usage
   - Redundant ARIA
   - Missing aria-live regions for dynamic content

3. **Keyboard Navigation:**
   - Missing keyboard event handlers
   - Elements not focusable with keyboard
   - Missing focus management
   - Incorrect tab order
   - Focus trap issues in modals
   - Missing focus indicators

4. **Form Accessibility:**
   - Missing form labels
   - Labels not associated with inputs
   - Missing field validation messages
   - Error message accessibility
   - Missing required field indicators

5. **Interactive Elements:**
   - Click handlers on non-interactive elements
   - Missing button type attributes
   - Links vs buttons confusion
   - Disabled state accessibility

6. **Images & Media:**
   - Missing alt text
   - Decorative images not marked
   - Complex images without proper descriptions
   - Video/audio accessibility (captions, transcripts)

7. **Color & Contrast:**
   - Color-only information
   - Potential contrast issues (note: can't fully check without seeing rendered output)
   - Missing text alternatives

8. **Dynamic Content:**
   - Missing screen reader announcements
   - Live region issues
   - Loading state accessibility
   - Modal/dialog accessibility

9. **Focus Management:**
   - Focus not returned after modal close
   - Missing focus trap in modals
   - Focus on wrong element after actions

10. **React-Specific a11y:**
   - Missing eslint-plugin-jsx-a11y rules
   - Ref usage for focus management
   - Fragment accessibility considerations

Categorize by WCAG level (A, AA, AAA) and severity.

**DO NOT provide corrected code. Only identify issues.**

```javascript
{user_code}
```

Format your response as:
## Accessibility Review

### Critical Accessibility Issues (WCAG Level A)
[Must fix]

### Important Accessibility Issues (WCAG Level AA)
[Should fix]

### Enhanced Accessibility (WCAG Level AAA)
[Nice to have]

### Keyboard Navigation Issues
[List here]

### Screen Reader Issues
[List here]

### Summary & Recommendations
[Priority improvements]"""

   try:
      result = llm.invoke(prompt)
      return {"accessibility_report": result.content}
   except Exception as e:
      return {"accessibility_report": f"Error during accessibility check: {str(e)}"}


def react_performance_evaluator(state: AgentState):
   """Evaluates code for performance issues for React)."""
   user_code = state['user_code']

   prompt = f"""You are a performance optimization expert for React applications.

Analyze the following code for performance bottlenecks:

1. **Algorithm Efficiency:**
   - Time complexity issues (O(n²) or worse where better exists)
   - Space complexity problems
   - Inefficient algorithms or data structures

2. **Memory Management:**
   - Memory leaks
   - Unnecessary object creation
   - Large data structures in memory

3. **I/O Operations:**
   - Blocking I/O operations
   - Missing async/await where beneficial
   - Inefficient file handling
   - Unnecessary network calls

4. **React-Specific Performance:**
   - Unnecessary re-renders
   - Missing React.memo for expensive components
   - Large components not code-split
   - Inline function definitions in render
   - Missing useCallback/useMemo
   - Virtual scrolling opportunities for long lists
   - Bundle size concerns

7. **JavaScript-Specific:**
   - Inefficient DOM manipulation
   - Missing debouncing/throttling
   - Synchronous operations blocking UI
   - Missing Web Workers opportunities
   - Large data processing in main thread

5. **Loops and Iterations:**
   - Nested loops that could be optimized
   - Inefficient iterations

6. **Caching Opportunities:**
   - Repeated expensive computations
   - Missing memoization
   - Cacheable API calls

8. **Concurrency:**
   - Missing parallelization opportunities
   - Thread/async considerations

Provide specific recommendations with estimated performance impact.

**DO NOT provide corrected code. Only identify issues.**

```
{user_code}
```"""

   try:
      result = llm.invoke(prompt)
      return {"performance_report": result.content}
   except Exception as e:
      return {"performance_report": f"Error during performance evaluation: {str(e)}"}


def react_best_practices_checker(state: AgentState):
   """Checks adherence to best practices for react."""
   user_code = state['user_code']

   prompt = f"""You are a React best practices expert and software architect.

Review the code for adherence to best practices:

1. **Design Patterns:**
   - Appropriate use of design patterns
   - Anti-patterns present
   - SOLID principles violations

2. **Modern JavaScript/React:**
   - ES6+ features usage
   - Functional programming patterns
   - Immutability practices
   - Declarative vs imperative code
   - Modern React patterns (hooks vs classes)

3. **Code Organization:**
   - Module/file structure
   - Component/class design
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

7. **Dependencies:**
   - Dependency management
   - Import organization
   - Circular dependency risks

**DO NOT provide corrected code. Only identify areas for improvement.**

```
{user_code}
```"""

   try:
      result = llm.invoke(prompt)
      return {"best_practices_report": result.content}
   except Exception as e:
      return {"best_practices_report": f"Error during best practices check: {str(e)}"}


def react_complexity_analyzer(state: AgentState):
   """Analyzes code complexity for react."""
   user_code = state['user_code']
   language = state['language']

   prompt = f"""You are a software engineering expert specializing in code maintainability.

Analyze the React code complexity and maintainability:

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

5. **Component/Class Metrics:**
   - Components/classes with too many methods
   - God objects
   - Excessive inheritance depth

6. **Maintainability Issues:**
   - Code that's difficult to modify
   - Tight coupling
   - Hidden dependencies

Provide a maintainability score and specific areas that need refactoring.

**DO NOT provide corrected code. Only analyze complexity.**

```
{user_code}
```"""

   try:
      result = llm.invoke(prompt)
      return {"complexity_report": result.content}
   except Exception as e:
      return {"complexity_report": f"Error during complexity analysis: {str(e)}"}


def react_documentation_reviewer(state: AgentState):
   """Reviews code documentation quality for React."""
   user_code = state['user_code']

   prompt = f"""You are a technical documentation expert for React.

Review the code documentation quality:

1. **JSDoc Comments:**
   - Missing JSDoc for functions/components
   - Missing parameter descriptions
   - Missing return type descriptions
   - Missing example usage

3. **TypeScript Types:**
   - Missing interface documentation
   - Missing type descriptions
   - Complex types without explanation
   - Missing prop type documentation

2. **Comments:**
   - Missing explanatory comments for complex logic
   - Outdated or misleading comments
   - Over-commenting obvious code
   - TODO/FIXME items

4. **Code Clarity:**
   - Unclear variable names
   - Cryptic abbreviations
   - Missing context for magic numbers

5. **API Documentation:**
   - Public API without documentation
   - Missing usage examples
   - Undocumented side effects

**DO NOT provide corrected code. Only review documentation.**

```
{user_code}
```"""

   try:
      result = llm.invoke(prompt)
      return {"documentation_report": result.content}
   except Exception as e:
      return {"documentation_report": f"Error during documentation review: {str(e)}"}
