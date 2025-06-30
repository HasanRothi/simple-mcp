# streamlit_ui.py
import streamlit as st
from simple_client import get_mcp_tools, call_mcp_tool
import subprocess
import json
import asyncio


def call_ollama(prompt):
    result = subprocess.run(
        ["ollama", "run", "llama3.2", prompt],
        capture_output=True, text=True
    )
    return result.stdout.strip()


st.title("🧠 FastMCP + Ollama (Dynamic Tools)")

query = st.text_input("Ask something:")

if st.button("Submit"):
    st.write("🔍 Query:", query)

    # Step 1: Get all available tools
    tools = asyncio.run(get_mcp_tools())
    st.write("🔍 Tool objects:", tools)

    tool_descriptions = "\n".join([
        f"- {tool.name}: {tool.description or ''}"
        for tool in tools
    ])

    # Step 2: Ask LLM to select tool & input
    tool_selection_prompt = f"""
User query: "{query}"

Available tools:
{tool_descriptions}

Choose the best tool (if any), and provide the tool name and input JSON.

Respond in format:
TOOL_NAME: <tool_name>
TOOL_INPUT: <input_as_json>
"""
    st.info("🧠 Asking Ollama to select a tool dynamically...")
    llm_decision = call_ollama(tool_selection_prompt)
    st.write("🧠 LLM Choose:", llm_decision)

    try:
        tool_name = llm_decision.split("TOOL_NAME:")[1].split("\n")[0].strip()
        tool_input = llm_decision.split("TOOL_INPUT:")[1].strip()
        tool_input = json.loads(tool_input)

        tool_output = asyncio.run(call_mcp_tool(tool_name, tool_input))
        st.write("🧠 tool_output", tool_output)

        if len(tool_input) > 0:
            st.write("🧠 tool_output formatted", json.loads(tool_output[0].text))
            tool_output = json.loads(tool_output[0].text)

        # Step 3: Generate final answer using tool output
        final_prompt = f"User asked: {query}. Tool output: {tool_output}. Provide the final response. Provide answer only based on tool output."
        st.write(final_prompt)
        response = call_ollama(final_prompt)
        st.success("🤖 LLM Response:")
        st.write(response)

    except Exception as e:
        st.error(f"Failed to parse tool info: {e}")
        st.write("Full output:", llm_decision)
