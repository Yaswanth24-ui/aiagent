import os
from flask import Flask, request, jsonify, send_from_directory
from agent import AutonomousAgent
from real_agent import RealAutonomousAgent
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static')

class WebFriendlyAgent(AutonomousAgent):
    """Subclass to collect logs for the web UI."""
    def __init__(self):
        super().__init__()
        self.logs = []

    def record_log(self, type, content, status='success'):
        self.logs.append({"type": type, "content": content, "status": status})

    def run_web(self, task):
        self.logs = []
        self.record_log("PLANNER", f"Decomposing task: '{task}'")
        sub_tasks = self.llm.decompose_task(task)
        
        for idx, st in enumerate(sub_tasks):
            self.record_log("SUBTASK", f"{idx+1}. {st}")
        
        for sub_task in sub_tasks:
            success = False
            retries = 0
            error_feedback = None
            
            while not success and retries < self.max_retries:
                try:
                    tool_name, tool_args = self.llm.decide_action(sub_task, self.memory, error_feedback)
                    self.record_log("REASONER", f"Selected {tool_name} with {tool_args}")
                    
                    if tool_name not in self.tools:
                        raise ValueError(f"Tool '{tool_name}' not found.")
                    
                    result = self.tools[tool_name](**tool_args)
                    self.record_log("EXECUTOR", f"Tool {tool_name} response.", "success")
                    self.record_log("RESULT", result)
                    
                    self.memory.append({"task": sub_task, "action": tool_name, "args": tool_args, "result": result})
                    success = True
                except Exception as e:
                    error_feedback = str(e)
                    self.record_log("FEEDBACK", f"Error: {error_feedback}", "error")
                    retries += 1
            
            if not success:
               self.record_log("FAILURE", f"Failed subtask after {self.max_retries} retries.", "error")
               return False
               
        self.record_log("COMPLETION", "All subtasks completed successfully!")
        return True

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    task = data.get('task')
    
    if not task:
        return jsonify({"status": "error", "error": "No task provided"}), 400

    # Deterministic choice: Mock for now so the user can see it work instantly 
    # unless they specifically want the Real one. 
    # But for a "Simple Website" demo, Mock is better to show the steps clearly.
    agent = WebFriendlyAgent()
    success = agent.run_web(task)
    
    return jsonify({
        "status": "success" if success else "failure",
        "steps": agent.logs
    })

if __name__ == '__main__':
    print("AI Agent Web Interface running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
