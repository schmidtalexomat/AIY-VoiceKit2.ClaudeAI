import requests
import json
import config

class ClaudeClient:
    def __init__(self):
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": config.CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01"
        }
        self.conversation_history = []
        print("Claude HTTP client ready")
    
    def ask_claude(self, question):
        """Ask Claude via HTTP and return answer"""
        if not question or question.strip() == "":
            return "No question asked"
        
        try:
            print(f"asking Claude: '{question}'")
            
            # Add user message to history (clean, without prompt)
            self.conversation_history.append({
                "role": "user", 
                "content": question
            })
            
            # Keep conversation manageable
            if len(self.conversation_history) > config.MAX_CONVERSATION_TURNS * 2:
                # Remove oldest exchange (user + assistant)
                self.conversation_history = self.conversation_history[2:]
            
            # Build messages with system prompt
            payload = {
            "model": config.CLAUDE_MODEL,
            "max_tokens": config.CLAUDE_MAX_TOKENS,
            "system": "Answer briefly and precisely in German. Use simple text without markdown formatting.",
            "messages": self.conversation_history
            }
            
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data['content'][0]['text'].strip()
                
                # Add Claude's response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": answer
                })
                
                print(f"Claude answers: '{answer}'")
                return answer
            else:
                print(f"Claude API error: {response.status_code}")
                return "Sorry, I cannot answer right now"
                
        except Exception as e:
            print(f"Claude HTTP error: {e}")
            return "Connection error to Claude"
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        print("conversation reset")
