import asyncio
import time
from typing import List, Dict
import os
from openai import OpenAI
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def simple_tool(arg: dict) -> str:
    """Simple tool that returns a short response after a small delay."""
    time.sleep(0.1)
    return f"Processed {arg}"


def create_assistant(parallel: bool, complexity: str) -> str:
    """Create an assistant with the simple_tool function."""
    tool_params = {
        "simple": {
            "type": "object",
            "properties": {"arg": {"type": "string"}},
            "required": ["arg"],
        },
        "medium": {
            "type": "object",
            "properties": {
                "arg": {"type": "string"},
                "priority": {"type": "integer", "minimum": 1, "maximum": 5},
                "category": {"type": "string", "enum": ["A", "B", "C"]},
            },
            "required": ["arg", "priority", "category"],
        },
        "complex": {
            "type": "object",
            "properties": {
                "arg": {"type": "string"},
                "priority": {"type": "integer", "minimum": 1, "maximum": 5},
                "category": {"type": "string", "enum": ["A", "B", "C"]},
                "metadata": {
                    "type": "object",
                    "properties": {
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "source": {"type": "string"},
                    },
                    "required": ["tags", "timestamp", "source"],
                },
            },
            "required": ["arg", "priority", "category", "metadata"],
        },
    }

    assistant = client.beta.assistants.create(
        name="Function Profiler",
        instructions=f"""You are testing function call performance. 
        When asked to process something, you should make multiple tool calls {'in parallel' if parallel else 'sequentially'}.
        If sequentially, you can only call one function at a time. If prompted for many tool calls,
        wait for each tool call to finish before asking for the next.
        Always use the simple_tool function for processing.
        Use appropriate complexity level ({complexity}) when making tool calls.""",
        model="gpt-4o-mini",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "simple_tool",
                    "description": "A simple tool that processes input",
                    "parameters": tool_params[complexity],
                },
            }
        ],
    )
    return assistant.id


def run_assistant(assistant_id: str, num_tools: int, complexity: str) -> Dict:
    """Run assistant with specified number of tool calls."""
    start_time = time.time()

    thread = client.beta.threads.create()

    complexity_examples = {
        "simple": "just use the basic argument",
        "medium": "include priority and category information",
        "complex": "include full metadata with tags, timestamp, and source",
    }

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Please make {num_tools} tool calls to process this message. {complexity_examples[complexity]}",
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant_id
    )

    tool_call_lengths = []
    tool_start_time = time.time()
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "completed":
            break
        elif run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_call_lengths.append(len(tool_calls))
            tool_outputs = []

            for tool_call in tool_calls:
                output = simple_tool(tool_call.function.arguments)
                tool_outputs.append({"tool_call_id": tool_call.id, "output": output})

            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
            )

        time.sleep(0.5)

    tool_end_time = time.time()
    end_time = time.time()

    client.beta.assistants.delete(assistant_id)

    return {
        "total_time": end_time - start_time,
        "tool_execution_time": tool_end_time - tool_start_time,
        "tool_calls": tool_call_lengths,
        "num_tools": num_tools,
        "complexity": complexity,
    }


def main():
    scenarios = [
        {"num_tools": 1, "parallel": False, "complexity": "simple"},
        {"num_tools": 2, "parallel": False, "complexity": "simple"},
        {"num_tools": 5, "parallel": False, "complexity": "simple"},
        {"num_tools": 1, "parallel": True, "complexity": "simple"},
        {"num_tools": 2, "parallel": True, "complexity": "simple"},
        {"num_tools": 5, "parallel": True, "complexity": "simple"},
        {"num_tools": 1, "parallel": False, "complexity": "medium"},
        {"num_tools": 2, "parallel": False, "complexity": "medium"},
        {"num_tools": 5, "parallel": False, "complexity": "medium"},
        {"num_tools": 1, "parallel": True, "complexity": "medium"},
        {"num_tools": 2, "parallel": True, "complexity": "medium"},
        {"num_tools": 5, "parallel": True, "complexity": "medium"},
        {"num_tools": 1, "parallel": False, "complexity": "complex"},
        {"num_tools": 2, "parallel": False, "complexity": "complex"},
        {"num_tools": 5, "parallel": False, "complexity": "complex"},
        {"num_tools": 1, "parallel": True, "complexity": "complex"},
        {"num_tools": 2, "parallel": True, "complexity": "complex"},
        {"num_tools": 5, "parallel": True, "complexity": "complex"},
    ]

    headers = [
        "Parallel",
        "Tools",
        "Complexity",
        "Tool Calls",
        "Total Time (s)",
        "Tool Time (s)",
    ]
    table_data = []

    results = []
    for scenario in scenarios:
        assistant_id = create_assistant(scenario["parallel"], scenario["complexity"])
        result = run_assistant(
            assistant_id, scenario["num_tools"], scenario["complexity"]
        )
        results.append(result)

        # Format data for table
        print(f"\nScenario: {scenario}")

        table_data.append(
            [
                "Yes" if scenario["parallel"] else "No",
                scenario["num_tools"],
                scenario["complexity"],
                result["tool_calls"],
                f"{result['total_time']:.2f}",
                f"{result['tool_execution_time']:.2f}",
            ]
        )

    # Print the table
    print("\nFunction Call Profiling Results:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


if __name__ == "__main__":
    main()
