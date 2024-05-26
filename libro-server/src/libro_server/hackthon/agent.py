from langchain.agents import AgentExecutor, ZeroShotAgent
from langchain_openai import ChatOpenAI
import json

llm = ChatOpenAI()

from langchain.callbacks.base import BaseCallbackHandler
from libro_server.hackthon_globals import tool_id_to_run_id, run_id_to_notebooks
from libro_server.hackthon.tool import tools


class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, post_method):
        self.post_method = post_method

    def on_agent_action(self, action, run_id, parent_run_id, **kwargs):
        result = {"status": 200, "runId": str(run_id)}
        print("on_agent_action", result)
        self.post_method(result)

    def on_tool_start(self, serialized, input_str: str, **kwargs):
        """Run when tool starts running."""
        print("on_tool_start")
        tool_id_to_run_id[str(kwargs.get("run_id"))] = str(kwargs.get("parent_run_id"))

    def on_tool_end(self, output: str, **kwargs):
        """Run when tool ends running."""
        print("ON TOOL END!")

    def on_agent_finish(
        self,
        finish,
        *,
        run_id,
        parent_run_id,
        **kwargs,
    ):
        """Run on agent end."""
        if run_id_to_notebooks.get(str(run_id)) is None:
            pass
        else:
            run_id_to_notebooks[str(run_id)]["status"] = "end"
        print("on_agent_finish", run_id_to_notebooks[str(run_id)])


agent_obj = ZeroShotAgent.from_llm_and_tools(llm, tools)

agent = AgentExecutor.from_agent_and_tools(
    agent=agent_obj,
    tools=tools,
)
