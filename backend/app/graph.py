from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import MessagesState
from dotenv import load_dotenv
import boto3
from typing import TypedDict, Annotated, Optional
import operator

load_dotenv(".env")

config = boto3.client("bedrock-runtime",region_name="us-east-1")

class AgentState(MessagesState):
    code_analysis: str
    security_report: str
    performance_report: str
    final_documentation: Optional[str]
    user_code: str

llm = ChatBedrockConverse(
    model="us.amazon.nova-premier-v1:0",
    max_tokens=32000
)  

def code_analyzer(state : AgentState):
    '''Analyzes code for potential issues.'''
    user_code = state['user_code']

    prompt = f'''
        You are a expert in the field of code analysis of the python langauge.\n

        Your task is to analyse the user code according to the PEP-8 standards.\n
        Also, follow the below rulse to analyse the code.
        - The code must match the codeing stadards of PEP-8.
        - There should not be any syntex errors.
        - There should not be any unused varialbes, Classes and objects.\n
        
    List out all the errors and non complience of the codeing standars and with
    the code.\n
    DO NOT give the corrected code
    \n\n
    usr_code : {user_code}
    '''

    result = llm.invoke(prompt)
    # print(result)
    return {
        "code_analysis" : result.content 
    }
    
def security_checker(state: AgentState):
    '''Checks code for security vulnerabilities.'''
    user_code = state['user_code']

    prompt = f'''
        You are a expert in the field of code security and cyber-security for the python langauge.\n

        Your task is to analyse the user code for any security issues.\n
        Also, follow the below rulse to analyse the code.
        - There should not be any code that can leak the data.
        - There should not be any logic that can share unwanted data to other users.
        - There should not be any security issues.\n
        
    List out all the security flaws with the code.\n
    DO NOT give the corrected code

    \n\n
    usr_code : {user_code}
    '''

    result = llm.invoke(prompt)
    # print(result)
    return {
        "security_report":result.content
    }    

def performance_evaluator(state: AgentState):
    '''Evaluates code for performance bottlenecks.'''
    user_code = state['user_code']

    prompt = f'''
        You are a expert in the field of code performance of the python langauge.\n

        Your task is to analyse the user code for any performance bottlenacks.\n

        
    List out all the performance issues with the code.\n
    DO NOT give the corrected code

    \n\n
    usr_code : {user_code}
    '''

    result = llm.invoke(prompt)

    return {
        "performance_report":result
    }

def generate_report(state: AgentState):
    '''Generates a comprehensive report based on analyses.'''

    user_code = state['user_code']
    analysis_report = state['code_analysis']
    security_report = state['security_report']
    perforamce_report = state["performance_report"]

    prompt = f'''
        Base of the code analysis report, code security report and code performance report
        generate the comperhancive docuemnt about all the errors, flwas and issues in the code.\n
        DO NOT give the corrected code

    \n\n
    usr_code : {user_code} \n
    analysis_report : {analysis_report}\n
    performance_report : {perforamce_report}\n
    secuirty_report : {security_report}
    '''

    result = llm.invoke(prompt)
    return {
        "final_documentation": result
    }

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("code_analyzer", code_analyzer)
    graph.add_node("security_checker", security_checker)
    graph.add_node("performance_evaluator", performance_evaluator)
    graph.add_node("generate_report", generate_report)

    graph.add_edge(START, "code_analyzer")
    graph.add_edge(START, "security_checker")    
    graph.add_edge(START, "performance_evaluator")

    graph.add_edge("code_analyzer", "generate_report")
    graph.add_edge("security_checker", "generate_report")
    graph.add_edge("performance_evaluator", "generate_report")
    graph.add_edge("generate_report", END)

    return graph.compile(checkpointer=MemorySaver())

def main(user_code:str = None):
    workflow = build_graph()
    intitial_state = {"user_code":user_code}
    config = {"configurable": {"thread_id": "1"}}

    result = workflow.invoke(intitial_state,config=config)
    return result
