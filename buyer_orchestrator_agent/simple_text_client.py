"""
Simple text client example for the Buyer Orchestrator Agent.
This demonstrates how to use the send_text_to_agent function for direct text interaction.
"""
import asyncio
from dotenv import load_dotenv

from agent import root_agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from __main__ import send_text_to_agent, APP_NAME

load_dotenv()


async def main():
    """Example of using text input with the agent."""
    # Set up the agent components
    session_service = InMemorySessionService()
    
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
        memory_service=InMemoryMemoryService(),
        artifact_service=InMemoryArtifactService(),
    )

    print("🛒 Buyer Orchestrator Agent - Text Client")
    print("=" * 50)
    print("Type your messages below. Type 'quit' to exit.")
    print()

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            if not user_input:
                continue

            print("Agent: ", end="", flush=True)
            
            # Send to agent and get response
            response = await send_text_to_agent(user_input, runner, session_service)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
