#!/usr/bin/env python3
"""
AI News Analyst - Main Entry Point

This is the main entry point for the AI News Analyst application.
It provides a simple interface to run news analysis using RAG and Wikipedia search.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.workflow.news_analysis_workflow import run_news_analysis


def main():
    """Main function to run the AI News Analyst"""
    print("=== AI News Analyst ===")
    print("Ask me anything about recent news or general knowledge!")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("Enter your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            if not user_input:
                print("Please enter a question.")
                continue
                
            print("\n=== Analyzing... ===")
            result = run_news_analysis(user_input)
            print("\n=== AI Response ===")
            print(result)
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.\n")

if __name__ == "__main__":
    main()