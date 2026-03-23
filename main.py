import os
from dotenv import load_dotenv
from agent import AutonomousAgent as MockAgent
from real_agent import RealAutonomousAgent as RealAgent

load_dotenv()

def main():
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        print("--- [REAL LLM MODE] API Key detected, initializing Real AI Agent ---")
        agent = RealAgent()
        # If Real Agent initialization failed (e.g. invalid key/quota)
        if not hasattr(agent, 'client'):
            print("--- [AUTO-FALLBACK] Real Agent failed to initialize. Using Simulation Agent ---")
            agent = MockAgent()
    else:
        print("--- [MOCK MODE] No API Key found, using Simulation Agent ---")
        agent = MockAgent()
        
    print("======================================================")
    print("Welcome to the Autonomous AI Agent CLI")
    print("Type 'exit' or 'quit' to close the program.")
    print("======================================================")
    
    while True:
        try:
            task = input("\nEnter a task> ").strip()
            if not task:
                continue
            if task.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break
                
            # Perform multi-step task execution
            success = agent.run(task)
            
            # If the Real Agent fails due to Quota, we can offer to switch to Simulation
            if not success and isinstance(agent, RealAgent):
                print("\n[System] Real Agent failed (likely Quota/API issue). Falling back to Simulation for this session...")
                agent = MockAgent()
                agent.run(task)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            
if __name__ == "__main__":
    main()
