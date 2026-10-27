from src.agent.router import get_agent

def main():
    agent = get_agent()
    
    print("\n--- Testing Agent ---")
    
    # Test 1: RAG (Should use internal docs)
    print("\n[Test 1: Internal Documents]")
    question_1 = "What is the remote work policy?"
    print(f"User: {question_1}")
    response_1 = agent.invoke({"messages": [("user", question_1)]})
    print(f"Agent: {response_1['messages'][-1].content}")
    
    # Test 2: Calculator (Should use math tool)
    print("\n[Test 2: Math]")
    question_2 = "What is 15% of 2500?"
    print(f"User: {question_2}")
    response_2 = agent.invoke({"messages": [("user", question_2)]})
    print(f"Agent: {response_2['messages'][-1].content}")

if __name__ == "__main__":
    main()