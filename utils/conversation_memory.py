import os
import json
from datetime import datetime
from typing import List, Dict, Optional


class ConversationMemory:
    def __init__(self, storage_dir="conversation_history", max_history=10):
        """
        Initialize conversation memory with text file storage
        
        Args:
            storage_dir: Directory to store conversation history files
            max_history: Maximum number of Q&A exchanges to keep per user
        """
        self.storage_dir = storage_dir
        self.max_history = max_history
        
        # Create directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
    
    def _get_user_file_path(self, user_id: str) -> str:
        """Get the file path for a user's conversation history"""
        # Sanitize user_id to be safe for filenames
        safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ('_', '-'))
        return os.path.join(self.storage_dir, f"{safe_user_id}.txt")
    
    def add_exchange(self, user_id: str, question: str, answer: str) -> None:
        """
        Add a Q&A exchange to the user's conversation history
        
        Args:
            user_id: User identifier (e.g., LINE user ID or "user" for now)
            question: User's question
            answer: Bot's answer
        """
        file_path = self._get_user_file_path(user_id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Read existing history
        history = self._read_history(user_id)
        
        # Append new exchange
        exchange = {
            "timestamp": timestamp,
            "question": question,
            "answer": answer
        }
        history.append(exchange)
        
        # Keep only max_history recent exchanges
        if len(history) > self.max_history:
            history = history[-self.max_history:]
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            for ex in history:
                f.write(f"[{ex['timestamp']}]\n")
                f.write(f"Q: {ex['question']}\n")
                f.write(f"A: {ex['answer']}\n")
                f.write("\n---\n\n")
    
    def _read_history(self, user_id: str) -> List[Dict]:
        """
        Read conversation history from file
        
        Returns:
            List of conversation exchanges as dictionaries
        """
        file_path = self._get_user_file_path(user_id)
        
        if not os.path.exists(file_path):
            return []
        
        history = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the file content
            exchanges = content.split('\n---\n')
            for exchange_text in exchanges:
                exchange_text = exchange_text.strip()
                if not exchange_text:
                    continue
                
                lines = exchange_text.split('\n')
                if len(lines) >= 3:
                    timestamp_line = lines[0]
                    question_line = lines[1]
                    answer_line = lines[2]
                    
                    # Extract timestamp
                    timestamp = timestamp_line.strip('[]').strip()
                    
                    # Extract question (remove "Q: " prefix)
                    question = question_line[3:] if question_line.startswith('Q: ') else question_line
                    
                    # Extract answer (handle multi-line answers)
                    answer_lines = []
                    for i in range(2, len(lines)):
                        if lines[i].startswith('A: '):
                            answer_lines.append(lines[i][3:])
                        elif answer_lines:  # continuation of answer
                            answer_lines.append(lines[i])
                    answer = '\n'.join(answer_lines)
                    
                    history.append({
                        "timestamp": timestamp,
                        "question": question,
                        "answer": answer
                    })
        except Exception as e:
            print(f"Error reading history for {user_id}: {e}")
            return []
        
        return history
    
    def get_history(self, user_id: str) -> List[Dict]:
        """
        Get conversation history for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of conversation exchanges
        """
        return self._read_history(user_id)
    
    def format_history_for_prompt(self, user_id: str) -> str:
        """
        Format conversation history for inclusion in LLM prompt
        
        Args:
            user_id: User identifier
            
        Returns:
            Formatted string of conversation history, empty if no history
        """
        history = self.get_history(user_id)
        
        if not history:
            return ""
        
        formatted = "=== PREVIOUS CONVERSATION HISTORY ===\n"
        formatted += "You have access to the following conversation history with this user.\n"
        formatted += "Use this context to provide continuity and reference previous discussions when relevant.\n\n"
        
        for i, exchange in enumerate(history, 1):
            formatted += f"[{exchange['timestamp']}]\n"
            formatted += f"User: {exchange['question']}\n"
            formatted += f"You: {exchange['answer']}\n\n"
        
        formatted += "=== END OF CONVERSATION HISTORY ===\n\n"
        return formatted
    
    def clear_history(self, user_id: str) -> bool:
        """
        Clear conversation history for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if history was cleared, False if no history existed
        """
        file_path = self._get_user_file_path(user_id)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    def get_conversation_count(self, user_id: str) -> int:
        """Get the number of conversation exchanges for a user"""
        return len(self.get_history(user_id))
    
    def user_has_history(self, user_id: str) -> bool:
        """Check if a user has any conversation history"""
        file_path = self._get_user_file_path(user_id)
        return os.path.exists(file_path) and os.path.getsize(file_path) > 0
