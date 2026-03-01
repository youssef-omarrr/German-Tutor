from langchain_core.messages import BaseMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from pathlib import Path
import yaml

from .RAG.tavily_rag import search_web
from .RAG.offline_rag import search_local_books
from .LLM.prompt_templates import SYSTEM_PROMPT
from .LLM.react_agent import AgentState, make_react_agent

load_dotenv()

# Config 
# --------
CONFIG_PATH = Path("MODEL_3/config.yaml")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

# LLM + Tools 
# -----------
tools = [search_web, search_local_books]
llm = ChatGroq(model=config["LLM"]["model"],
            temperature=0.7)
llm_with_tools = llm.bind_tools(tools)

# ReAct agent
# -------------
react_agent = make_react_agent(llm_with_tools)

# Routing Functions 
# -------------------
def should_use_tools(state: AgentState) -> Literal["tools", "end"]:
    """If the agent made tool calls, execute them. Otherwise we're done."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"

# Build Graph 
# ------------
builder = StateGraph(AgentState)

# nodes
builder.add_node("react_agent", react_agent)
builder.add_node("tools", ToolNode(tools))

# entry point goes straight to the agent
builder.add_edge(START, "react_agent")

# ReAct loop: agent → tools → agent → ... → end
builder.add_conditional_edges(
    "react_agent",
    should_use_tools,
    {
        "tools": "tools",
        "end":   END
    }
)
builder.add_edge("tools", "react_agent")   # tool results loop back to agent

# compile
tutor_graph = builder.compile()