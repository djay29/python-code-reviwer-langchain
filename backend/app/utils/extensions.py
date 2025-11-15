from langchain_aws import ChatBedrockConverse
from langgraph.graph.message import MessagesState
from dotenv import load_dotenv
import boto3
from typing import Optional

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
    language: str
    
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
