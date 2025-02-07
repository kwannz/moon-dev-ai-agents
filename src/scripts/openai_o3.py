"""
OpenAI O3-mini Test Script
Tests OpenAI API integration
"""

import os
import openai
from termcolor import cprint

def test_o3_mini():
    # Initialize client with correct env variable name
    cprint("O3-mini test launching...", "cyan")
    api_key = os.getenv('OPENAI_KEY')  # Changed to match your .env setup
    
    if not api_key:
        cprint("❌ Error: OPENAI_KEY environment variable not found", "red")
        return
        
    openai.api_key = api_key
    
    # Test prompt
    prompt = "What is the meaning of life?"
    
    cprint("Processing request...", "yellow")
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        
        cprint("O3-mini model responded successfully!", "green")
        print("\nGenerated Response:")
        print(response.choices[0].text.strip())
        
    except Exception as e:
        cprint(f"❌ Error: {str(e)}", "red")

if __name__ == "__main__":
    cprint("OpenAI O3-mini Test", "magenta")
    test_o3_mini()
