import os
import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any

class CalendarAPI:
    def check_calendar(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """Checks if a calendar slot is available."""
        # Mock logic: busy if it starts at 11am
        if "11:00:00" in start_time:
            return {
                "status": "busy",
                "message": "Slot is already occupied",
                "available": False
            }
        return {
            "status": "available",
            "message": "Slot is free",
            "available": True
        }

    def book_meeting(self, title: str, start_time: str, end_time: str, attendees: list[str]) -> Dict[str, Any]:
        """Mock Calendar API to book a meeting and generate a REAL Jitsi video link."""
        if not title or not start_time or not end_time:
            raise ValueError("title, start_time, and end_time are required to book a meeting.")
        
        event_id = str(uuid.uuid4())
        # Generate a safe, alphanumeric meeting name for Jitsi
        safe_title = "".join(c for c in title if c.isalnum())
        meeting_link = f"https://meet.jit.si/CervAI_{safe_title}_{uuid.uuid4().hex[:6]}"
        
        return {
            "status": "success",
            "event_id": event_id,
            "meeting_link": meeting_link,
            "message": f"Meeting '{title}' booked successfully from {start_time} to {end_time}.",
            "attendees": attendees
        }

class NotificationSystem:
    def send_notification(self, team_members: list[str], message: str) -> Dict[str, Any]:
        """Sends real emails to specified team members using SMTP."""
        sender_email = os.environ.get("SENDER_EMAIL")
        sender_password = os.environ.get("SENDER_PASSWORD") # App Password
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))

        if not sender_email or not sender_password:
            # Fallback to Mock if credentials are not configured yet
            print(f"!!! [NOTIFICATION FAILED] SENDER_EMAIL or SENDER_PASSWORD not set in .env.")
            return {
                "status": "simulation", 
                "message": "Missing credentials. Simulation mode.",
                "would_have_sent_to": team_members
            }

        if not team_members:
            raise ValueError("No recipients provided in 'team_members' list.")

        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = f"Autonomous AI Agent <{sender_email}>"
        msg['To'] = ", ".join(team_members)
        msg['Subject'] = "Autonomous Agent Notification"
        
        body = (
            f"Hello team members {team_members},\n\n"
            f"The AI Agent has completed a task and wants you to know:\n\n"
            f"--- TASK MESSAGE ---\n"
            f"{message}\n"
            f"---------------------\n\n"
            f"Sent by your AI Assistant."
        )
        msg.attach(MIMEText(body, 'plain'))

        # SMTP Execution
        print(f"  [NotificationSystem] Attempting SMTP login for {sender_email}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(1)
            server.starttls() 
            server.login(sender_email, sender_password)
            print(f"  [NotificationSystem] Login Successful. Sending email to {team_members}...")
            text = msg.as_string()
            server.sendmail(sender_email, team_members, text)
        
        print(f"  [NotificationSystem] REAL EMAIL SENT successfully to: {team_members}")
        return {
            "status": "success",
            "message": f"Real email sent to {len(team_members)} recipients.",
            "recipients": team_members
        }

class FileSystemTools:
    def list_files(self, path: str = ".") -> Dict[str, Any]:
        """Lists files in a given directory."""
        try:
            files = os.listdir(path)
            return {"status": "success", "files": files}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def read_file(self, filename: str) -> Dict[str, Any]:
        """Reads the content of a file."""
        try:
            with open(filename, 'r') as f:
                content = f.read()
            return {"status": "success", "content": content}
        except Exception as e:
            return {"status": "error", "message": str(e)}

class WebSearchAPI:
    def web_search(self, query: str) -> Dict[str, Any]:
        """Performs a real web search for information using the Tavily API."""
        api_key = os.environ.get("TAVILY_API_KEY")
        
        if not api_key:
            return {
                "status": "simulation", 
                "message": "Missing TAVILY_API_KEY. Using mock mode.",
                "result": "Simulation: Today's top AI news involves LLM agents."
            }
            
        try:
            from tavily import TavilyClient
            tavily = TavilyClient(api_key=api_key)
            
            print(f"  [WebSearchTools] Searching the internet for: '{query}'...")
            # We use 'context' format which is optimized for AI summarizing
            response = tavily.search(query=query, search_depth="basic", max_results=5)
            
            return {
                "status": "success",
                "query": query,
                "results": response['results'],
                "search_summary": "Retrieved search results from live internet."
            }
        except Exception as e:
            print(f"  [WebSearchTools] CRITICAL ERROR during Tavily search: {str(e)}")
            return {"status": "error", "message": str(e)}

class DatabaseAPI:
    def query_user_records(self, user_name: str) -> Dict[str, Any]:
        """Queries a mock database for user profile and contact details."""
        db = {
            "John Doe": {"email": "john@example.com", "department": "Engineering"},
            "Alice Smith": {"email": "alice@example.com", "department": "Product"},
            "Bob Jones": {"email": "bob@example.com", "department": "Design"}
        }
        return db.get(user_name, {"status": "not_found", "message": f"User {user_name} not found in database."})

def get_available_tools():
    calendar = CalendarAPI()
    notification = NotificationSystem()
    fs = FileSystemTools()
    web = WebSearchAPI()
    db = DatabaseAPI()
    
    return {
        "check_calendar_availability": calendar.check_calendar,
        "book_meeting": calendar.book_meeting,
        "send_notification": notification.send_notification,
        "list_files": fs.list_files,
        "read_file": fs.read_file,
        "web_search": web.web_search,
        "query_user_records": db.query_user_records
    }
