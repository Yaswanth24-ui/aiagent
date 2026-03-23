import re
import os

class LLMMock:
    def __init__(self):
        self.notification_tries = 0
        self.history = [] # Persistent memory for the simulation

    def extract_emails(self, text):
        return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text) or [os.environ.get("SENDER_EMAIL", "fallback@example.com")]

    def decompose_task(self, task: str) -> list[str]:
        """Mock task decomposition into multiple steps dynamically."""
        sub_tasks = []
        task_lower = task.lower()
        
        # Keyword-based reasoning logic to break tasks down
        if "book" in task_lower and ("meeting" in task_lower or "calendar" in task_lower):
            sub_tasks.append("Check calendar availability")
            sub_tasks.append(f"Book the meeting: {task[:30]}...")
            
        if "notify" in task_lower or "send" in task_lower or "mail" in task_lower or "email" in task_lower:
            emails = self.extract_emails(task)
            sub_tasks.append(f"Compose and send professional notification to {', '.join(emails)}")
            
        if "search" in task_lower or "find" in task_lower or "weather" in task_lower or "news" in task_lower:
            sub_tasks.append(f"Perform internet search for info related to: {task[:30]}...")
            
        # Fallback if no matching tools or complex task
        if not sub_tasks:
            sub_tasks.append(f"Process generic user request: {task[:30]}...")
            
        # Record task in history
        self.history.append({"task": task, "subtasks": sub_tasks})
        return sub_tasks

    def decide_action(self, sub_task: str, memory: list, error_feedback: str = None) -> tuple[str, dict]:
        """Mock reasoning and tool selection based on sub-task and context."""
        sub_task_l = sub_task.lower()
        
        # 1. Check Availability
        if "check calendar" in sub_task_l or "available" in sub_task_l:
            return "check_calendar_availability", {
                "start_time": "2026-03-25T14:00:00Z",
                "end_time": "2026-03-25T15:00:00Z"
            }

        # 2. Book Meeting
        elif "book" in sub_task_l and "meeting" in sub_task_l:
            return "book_meeting", {
                "title": "Strategy Sync",
                "start_time": "2026-03-25T14:00:00Z",
                "end_time": "2026-03-25T15:00:00Z",
                "attendees": ["manager@team.com"]
            }
        
        # 3. Notify Team / Send Email
        elif "notify" in sub_task_l or "send" in sub_task_l or "email" in sub_task_l:
            # Look into task memory to find details (like links)
            context = "Simulated Task Update"
            for item in memory:
                if item.get("action") == "book_meeting":
                    link = item["result"].get("meeting_link", "https://meeting.link")
                    context = f"Meeting booked! Link: {link}"
                elif item.get("action") == "web_search":
                    # Extract search result from mock search
                    res = item["result"].get("results", "Latest AI News")
                    context = f"Search Report: {res}"
            
            recipients = self.extract_emails(sub_task)
            return "send_notification", {
                "team_members": recipients,
                "message": f"Hello,\n\nI have completed your request: {sub_task}\n\nDetails:\n{context}\n\nBest regards,\nCerv AI Assistant"
            }
            
        # 4. Search
        elif "search" in sub_task_l or "find" in sub_task_l:
            return "web_search", {"query": sub_task}
            
        # Fallback to avoid 'unknown_tool'
        return "send_notification", {
            "team_members": [os.environ.get("SENDER_EMAIL", "admin@example.com")],
            "message": f"Task summary for: {sub_task}\nStatus: Successfully completed via fallback reasoning."
        }
