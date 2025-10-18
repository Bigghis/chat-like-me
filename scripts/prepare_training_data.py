#!/usr/bin/env python3
"""
Script to prepare Telegram chat data for LLM fine-tuning.

This script:
1. Filters chats (personal only by default, or includes groups with --include-groups)
2. Filters out people/groups with too few messages
3. Removes automated/service messages
4. Groups messages into conversational blocks
5. Formats data in LLM training format with name metadata
6. Saves output to JSONL file

Output format includes name metadata for each message to support multi-person conversations:
{"role": "user", "name": "PersonName", "content": "message text"}
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any


class ChatDataProcessor:
    def __init__(self, 
                 min_messages: int = 20,
                 turn_window_minutes: int = 5,
                 conversation_gap_minutes: int = 60,
                 your_name: str = "Pasquale",
                 include_groups: bool = False):
        """
        Initialize the chat data processor.
        
        Args:
            min_messages: Minimum number of messages for a contact to be included
            turn_window_minutes: Time window (in minutes) to group messages as one turn
            conversation_gap_minutes: Time gap (in minutes) to separate conversations
            your_name: Your name in the chats (to identify your messages)
            include_groups: Whether to include group chats (default: False, only personal)
        """
        self.min_messages = min_messages
        self.turn_window_seconds = turn_window_minutes * 60
        self.conversation_gap_seconds = conversation_gap_minutes * 60
        self.your_name = your_name
        self.include_groups = include_groups
        
    def load_chats(self, input_file: str) -> List[Dict]:
        """Load chats from JSON file."""
        print(f"Loading chats from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if 'chats' in data and 'list' in data['chats']:
            # Full Telegram export: {"chats": {"list": [...]}}
            chats = data['chats']['list']
        elif isinstance(data, list):
            # Array of chats: [...]
            chats = data
        elif isinstance(data, dict) and 'messages' in data:
            # Single chat object (extracted conversation): {"name": "...", "messages": [...]}
            chats = [data]
            print(f"  (Single conversation file detected)")
        else:
            raise ValueError("Unexpected JSON structure. Expected full export, chat list, or single conversation.")
        
        print(f"Loaded {len(chats)} chat(s)")
        return chats
    
    def filter_personal_chats(self, chats: List[Dict]) -> List[Dict]:
        """Filter to keep only personal chats, or include groups if flag is set."""
        if self.include_groups:
            # Include personal chats and group chats
            filtered_chats = [
                chat for chat in chats 
                if chat.get('type') in ['personal_chat', 'private_group', 'private_supergroup']
            ]
            personal_count = sum(1 for c in filtered_chats if c.get('type') == 'personal_chat')
            group_count = len(filtered_chats) - personal_count
            print(f"Found {personal_count} personal chats and {group_count} group chats")
        else:
            # Only personal chats
            filtered_chats = [
                chat for chat in chats 
                if chat.get('type') == 'personal_chat'
            ]
            print(f"Found {len(filtered_chats)} personal chats")
        return filtered_chats
    
    def filter_by_message_count(self, chats: List[Dict]) -> List[Dict]:
        """Filter out chats with too few messages."""
        filtered_chats = []
        for chat in chats:
            # Count actual message types (not service messages)
            messages = chat.get('messages', [])
            message_count = sum(1 for msg in messages if msg.get('type') == 'message')
            
            if message_count >= self.min_messages:
                filtered_chats.append(chat)
                print(f"  ✓ {chat.get('name', 'Unknown')}: {message_count} messages")
            else:
                print(f"  ✗ {chat.get('name', 'Unknown')}: {message_count} messages (below threshold)")
        
        print(f"\nKept {len(filtered_chats)} chats with >= {self.min_messages} messages")
        return filtered_chats
    
    def extract_text(self, message: Dict) -> str:
        """Extract text from a message."""
        # Handle different text formats
        if isinstance(message.get('text'), str):
            return message['text']
        elif isinstance(message.get('text'), list):
            # Text is an array of text entities
            text_parts = []
            for entity in message['text']:
                if isinstance(entity, dict) and 'text' in entity:
                    text_parts.append(entity['text'])
                elif isinstance(entity, str):
                    text_parts.append(entity)
            return ''.join(text_parts)
        return ''
    
    def is_valid_message(self, message: Dict) -> bool:
        """Check if message is valid (not service, automated, etc.)."""
        # Skip service messages
        if message.get('type') != 'message':
            return False
        
        # Skip messages with no text
        text = self.extract_text(message)
        if not text or not text.strip():
            return False
        
        # Skip messages from Telegram official account
        from_name = message.get('from', '')
        if from_name in ['Telegram', 'Group', 'Channel']:
            return False
        
        # Skip messages with media only (no meaningful text)
        if len(text.strip()) < 2:
            return False
        
        return True
    
    def group_messages_into_turns(self, messages: List[Dict]) -> List[List[Dict]]:
        """
        Group messages into turns based on time windows.
        Messages from the same person within turn_window_seconds are grouped together.
        """
        if not messages:
            return []
        
        turns = []
        current_turn = [messages[0]]
        current_sender = messages[0].get('from')
        current_time = int(messages[0].get('date_unixtime', 0))
        
        for message in messages[1:]:
            msg_sender = message.get('from')
            msg_time = int(message.get('date_unixtime', 0))
            
            # Check if this message belongs to the current turn
            if (msg_sender == current_sender and 
                msg_time - current_time <= self.turn_window_seconds):
                current_turn.append(message)
                current_time = msg_time
            else:
                # Start a new turn
                turns.append(current_turn)
                current_turn = [message]
                current_sender = msg_sender
                current_time = msg_time
        
        # Add the last turn
        if current_turn:
            turns.append(current_turn)
        
        return turns
    
    def group_turns_into_conversations(self, turns: List[List[Dict]]) -> List[List[List[Dict]]]:
        """
        Group turns into conversations based on time gaps.
        Conversations are separated if there's a gap > conversation_gap_seconds.
        """
        if not turns:
            return []
        
        conversations = []
        current_conversation = [turns[0]]
        
        for i in range(1, len(turns)):
            prev_turn_last_msg = current_conversation[-1][-1]
            curr_turn_first_msg = turns[i][0]
            
            prev_time = int(prev_turn_last_msg.get('date_unixtime', 0))
            curr_time = int(curr_turn_first_msg.get('date_unixtime', 0))
            
            time_gap = curr_time - prev_time
            
            if time_gap <= self.conversation_gap_seconds:
                current_conversation.append(turns[i])
            else:
                # Start a new conversation
                conversations.append(current_conversation)
                current_conversation = [turns[i]]
        
        # Add the last conversation
        if current_conversation:
            conversations.append(current_conversation)
        
        return conversations
    
    def get_participants(self, conversation: List[List[Dict]], chat_name: str, 
                         chat_type: str) -> List[str]:
        """Get list of unique participants in a conversation."""
        participants = set()
        for turn in conversation:
            for msg in turn:
                sender = msg.get('from', '')
                if sender:
                    participants.add(sender)
        
        # For group chats, return the list of participants
        # For personal chats, return just the contact name
        if chat_type == 'personal_chat':
            return [chat_name]
        else:
            return sorted(list(participants - {self.your_name}))
    
    def format_conversation_for_training(self, 
                                        conversation: List[List[Dict]], 
                                        contact_name: str,
                                        chat_type: str = 'personal_chat') -> Dict:
        """
        Format a conversation into the LLM training format with name metadata.
        
        Returns a dict with:
        - messages: list of {"role": "system/user/assistant", "name": "...", "content": "..."}
        """
        formatted_messages = []
        
        # Get participants for system message
        participants = self.get_participants(conversation, contact_name, chat_type)
        
        # Add system message
        if chat_type == 'personal_chat':
            system_prompt = f"You are {self.your_name}, chatting with {contact_name}. Respond naturally in their conversational style."
        else:
            # Group chat
            participants_str = ', '.join(participants)
            system_prompt = f"You are {self.your_name} in a group chat '{contact_name}' with {participants_str}. Respond naturally in the conversational style."
        
        formatted_messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Process each turn in the conversation
        for turn in conversation:
            # Get all messages in this turn
            turn_texts = [self.extract_text(msg) for msg in turn]
            combined_text = ' '.join(turn_texts).strip()
            
            if not combined_text:
                continue
            
            # Determine the role and name based on who sent the message
            sender = turn[0].get('from')
            if sender == self.your_name:
                role = "assistant"
            else:
                role = "user"
            
            # Add message with name metadata
            formatted_messages.append({
                "role": role,
                "name": sender,
                "content": combined_text
            })
        
        return {"messages": formatted_messages}
    
    def process_chats(self, chats: List[Dict]) -> List[Dict]:
        """Process all chats and return formatted training data."""
        all_training_data = []
        
        for chat in chats:
            contact_name = chat.get('name', 'Unknown')
            chat_type = chat.get('type', 'personal_chat')
            messages = chat.get('messages', [])
            
            print(f"\nProcessing chat with {contact_name} (type: {chat_type})...")
            
            # Filter valid messages
            valid_messages = [msg for msg in messages if self.is_valid_message(msg)]
            print(f"  Valid messages: {len(valid_messages)}/{len(messages)}")
            
            if not valid_messages:
                continue
            
            # Group messages into turns
            turns = self.group_messages_into_turns(valid_messages)
            print(f"  Grouped into {len(turns)} turns")
            
            # Group turns into conversations
            conversations = self.group_turns_into_conversations(turns)
            print(f"  Grouped into {len(conversations)} conversations")
            
            # Format each conversation for training
            for i, conversation in enumerate(conversations):
                # Only include conversations with at least 2 turns (back-and-forth)
                if len(conversation) >= 2:
                    formatted = self.format_conversation_for_training(conversation, contact_name, chat_type)
                    # Only include if there's at least one user and one assistant message
                    roles = [msg['role'] for msg in formatted['messages']]
                    if 'user' in roles and 'assistant' in roles:
                        all_training_data.append(formatted)
            
            print(f"  Generated {len([c for c in conversations if len(c) >= 2])} training examples")
        
        return all_training_data
    
    def save_training_data(self, training_data: List[Dict], output_file: str):
        """Save training data to JSONL file."""
        print(f"\nSaving {len(training_data)} training examples to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in training_data:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"✓ Saved successfully!")
        
        # Print statistics
        total_messages = sum(len(ex['messages']) for ex in training_data)
        print(f"\nStatistics:")
        print(f"  Total conversations: {len(training_data)}")
        print(f"  Total messages: {total_messages}")
        print(f"  Avg messages per conversation: {total_messages / len(training_data):.1f}")


def main():
    parser = argparse.ArgumentParser(
        description='Prepare Telegram chat data for LLM fine-tuning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process personal chats only (default)
  python prepare_training_data.py result.json
  
  # Include group chats as well
  python prepare_training_data.py result.json --include-groups
  
  # Customize filtering parameters
  python prepare_training_data.py result.json --min-messages 50 --your-name "John"
  
  # Adjust time windows
  python prepare_training_data.py result.json --turn-window 10 --conversation-gap 120
        """
    )
    
    parser.add_argument('input_file', help='Path to the Telegram JSON export file')
    parser.add_argument('--output', '-o', default='training_data.jsonl',
                        help='Output JSONL file (default: training_data.jsonl)')
    parser.add_argument('--min-messages', type=int, default=20,
                        help='Minimum messages per contact to include (default: 20)')
    parser.add_argument('--turn-window', type=int, default=5,
                        help='Minutes to group messages as one turn (default: 5)')
    parser.add_argument('--conversation-gap', type=int, default=60,
                        help='Minutes gap to separate conversations (default: 60)')
    parser.add_argument('--your-name', default='Pasquale',
                        help='Your name in the chats (default: Pasquale)')
    parser.add_argument('--include-groups', action='store_true',
                        help='Include group chats (default: only personal chats)')
    
    args = parser.parse_args()
    
    # Create processor
    processor = ChatDataProcessor(
        min_messages=args.min_messages,
        turn_window_minutes=args.turn_window,
        conversation_gap_minutes=args.conversation_gap,
        your_name=args.your_name,
        include_groups=args.include_groups
    )
    
    # Load and process chats
    chats = processor.load_chats(args.input_file)
    personal_chats = processor.filter_personal_chats(chats)
    filtered_chats = processor.filter_by_message_count(personal_chats)
    
    if not filtered_chats:
        print("\nNo chats meet the criteria. Try lowering --min-messages")
        return
    
    # Process chats into training data
    training_data = processor.process_chats(filtered_chats)
    
    if not training_data:
        print("\nNo training data generated. Check your data and parameters.")
        return
    
    # Save training data
    processor.save_training_data(training_data, args.output)


if __name__ == '__main__':
    main()

