import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import get_available_tools

load_dotenv()

class RealAutonomousAgent:
    """A fully stateful AI Agent that remembers history and executes multi-step tasks."""
    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self.model = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
        
        if not self.api_key:
            print("WARNING: Neither GEMINI_API_KEY nor OPENROUTER_API_KEY environment variable is set.")
            return

        # OpenRouter uses the OpenAI client format
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        
        # Load tools
        self.tool_functions = get_available_tools()
        
        # PERSISTENT MEMORY
        self.messages = [
            {"role": "system", "content": (
                "You are an Elite Autonomous AI Business Assistant. Your goal is to execute complex tasks flawlessly. "
                "\n\nHOW YOU OPERATE:"
                "\n1. DECOMPOSE: When given a task, first clearly state the sub-tasks you will perform."
                "\n2. TOOLS: Use the provided tools and analyze their outputs carefully."
                "\n3. MEMORY: You remember previous turns. Use past information to complete current tasks."
                "\n4. PROFESSIONALISM: All your responses and emails must be formal, polite, and detailed."
                "\n5. CONTEXT: Pass specific data (links, search results) between tools. Never send empty or generic notifications."
            )}
        ]
        
        # Define Tool Schema
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "check_calendar_availability",
                    "description": "Checks if a calendar slot is available.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_time": {"type": "string", "description": "ISO format start time"},
                            "end_time": {"type": "string", "description": "ISO format end time"}
                        },
                        "required": ["start_time", "end_time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "book_meeting",
                    "description": "Books a real meeting and generates a video link.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "start_time": {"type": "string"},
                            "end_time": {"type": "string"},
                            "attendees": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["title", "start_time", "end_time", "attendees"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_notification",
                    "description": "Sends high-quality professional emails via SMTP.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "team_members": {"type": "array", "items": {"type": "string"}},
                            "message": {"type": "string", "description": "Detailed, professional email body."}
                        },
                        "required": ["team_members", "message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Performs a REAL-TIME internet search for the latest info.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Reads local files.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string"}
                        },
                        "required": ["filename"]
                    }
                }
            }
        ]

    def run(self, task: str):
        if not self.api_key:
            return False
            
        print("\n" + "="*70)
        print(f"AGENT TASK: '{task}'")
        print("="*70)
        
        # Add task to persistent history
        self.messages.append({"role": "user", "content": task})
        
        try:
            # 1. Start with Reasoning & Planning
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools_schema,
                tool_choice="auto"
            )
        except Exception as e:
            print(f"  [ERROR] OpenRouter API failed: {str(e)}")
            return False
            
        message = response.choices[0].message
        self.messages.append(message)
        
        if message.content:
            print(f"\n[Agent Logic]:\n{message.content}")
        
        # Tool execution loop
        while message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                print(f"\n  ---> ACTION: {tool_name}")
                print(f"  ---> ARGS: {args}")
                
                if tool_name in self.tool_functions:
                    try:
                        result = self.tool_functions[tool_name](**args)
                        print(f"  <--- RESULT: Success")
                        
                        tool_msg = {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps(result)
                        }
                        self.messages.append(tool_msg)
                        
                    except Exception as e:
                        print(f"  <--- RESULT: Failed ({str(e)})")
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps({"error": str(e)})
                        })
                else:
                    print(f"  [Error] Tool {tool_name} not found.")
            
            # Get next logic step
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.tools_schema
                )
                message = response.choices[0].message
                self.messages.append(message)
                if message.content:
                    print(f"\n[Agent Summary]:\n{message.content}")
            except Exception as e:
                print(f"  [ERROR] Follow-up failed: {str(e)}")
                return False
                    
        print("\n" + "="*70)
        return True
