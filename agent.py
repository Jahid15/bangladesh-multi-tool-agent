import os
import sys

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from tools import get_tools

load_dotenv()

SYSTEM_PROMPT = """You are a helpful assistant for Bangladesh data.

Routing rules:
- Data or statistics questions about educational institutions -> InstitutionsDBTool
- Data or statistics questions about hospitals, clinics, health facilities -> HospitalsDBTool
- Data or statistics questions about restaurants, food places, ratings -> RestaurantsDBTool
- General knowledge, definitions, policies, history or culture -> WebSearchTool

When using a DB tool, write a valid SQLite SELECT query. Use COUNT, GROUP BY and ORDER BY for statistics
and LIMIT for lists. If a query fails or returns nothing, fix it and try again.
Always answer the user in clear natural language based on the tool results. Do not invent numbers."""


def build_agent(verbose=True):
    llm = ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5"))
    tools = get_tools()
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=verbose, max_iterations=8, handle_parsing_errors=True)


def ask(executor, question):
    output = executor.invoke({"input": question})["output"]
    if isinstance(output, list):
        output = "".join(block.get("text", "") for block in output if isinstance(block, dict))
    return output


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is missing. Add it to the .env file.")
    executor = build_agent()
    if len(sys.argv) > 1:
        print(ask(executor, " ".join(sys.argv[1:])))
        return
    print("Bangladesh AI Agent. Type 'exit' to quit.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if question:
            print(f"\nAgent: {ask(executor, question)}")


if __name__ == "__main__":
    main()
