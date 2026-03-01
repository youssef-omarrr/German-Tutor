from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated, Sequence
from MODEL_3.LLM.prompt_templates import SYSTEM_PROMPT

# State
# ------
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def make_react_agent(llm_with_tools):
    def react_agent(state: AgentState) -> dict:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(state["messages"])
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    return react_agent