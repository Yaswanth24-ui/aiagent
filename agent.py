import os
from tools import get_available_tools
from llm_mock import LLMMock

class AutonomousAgent:
    """The central Autonomous Agent that coordinates reasoning, tools, and memory."""
    def __init__(self):
        self.tools = get_available_tools()
        self.llm = LLMMock()
        self.memory = []
        self.max_retries = 3

    def run(self, task: str):
        print("="*60)
        print(f"AGENT INITIATED TASK: '{task}'")
        print("="*60)
        
        # 1. Task Decomposition
        sub_tasks = self.llm.decompose_task(task)
        print(f"\n[Planner] Decomposed into {len(sub_tasks)} sub-tasks:")
        for idx, st in enumerate(sub_tasks):
            print(f"  {idx+1}. {st}")
        
        # 2. Sequential Execution Workflow
        for sub_task in sub_tasks:
            print(f"\n---> Executing Sub-Task: '{sub_task}'")
            success = False
            retries = 0
            error_feedback = None
            
            while not success and retries < self.max_retries:
                try:
                    # Reasoning & Tool Selection
                    if error_feedback:
                        print(f"  [Reasoner] Adjusting strategy based on error feedack: '{error_feedback}'")
                        
                    tool_name, tool_args = self.llm.decide_action(sub_task, self.memory, error_feedback)
                    print(f"  [Agent] Selected Action: {tool_name} with arguments: {tool_args}")
                    
                    if tool_name not in self.tools:
                        raise ValueError(f"Tool '{tool_name}' not found.")
                    
                    # Tool/API Execution
                    print(f"  [Executor] Running tool '{tool_name}'...")
                    result = self.tools[tool_name](**tool_args)
                    print(f"  [Executor] API Response: {result}")
                    
                    # Update Memory context for subsequent steps
                    self.memory.append({
                        "task": sub_task,
                        "action": tool_name,
                        "args": tool_args,
                        "result": result
                    })
                    success = True
                    print(f"  [Agent] Sub-Task Completed Successfully!")
                    
                except Exception as e:
                    # Feedback and Retry Loop
                    error_feedback = str(e)
                    print(f"  [Executor/Feedback] Action Failed: {error_feedback}")
                    retries += 1
                    if retries < self.max_retries:
                        print(f"  [Feedback Loop] Retrying action ({retries}/{self.max_retries})...")
            
            if not success:
                error_msg = f"!!! Agent strictly failed to complete sub-task '{sub_task}' after {self.max_retries} attempts."
                print(error_msg)
                
                # Automatically Alert Admin on Failure
                admin_email = os.environ.get("SENDER_EMAIL")
                if admin_email:
                    print(f"  [Failure Handling] Alerting admin ({admin_email}) about task failure...")
                    self.tools.get("send_notification", lambda **x: None)(
                        team_members=[admin_email],
                        message=f"CRITICAL: Agent failed task '{sub_task}'. Last error: {error_feedback}"
                    )
                return False
                
        print("\n" + "="*60)
        print("AGENT COMPLETED ALL MULTI-STEP TASKS SUCCESSFULLY!")
        print("="*60)
        return True
