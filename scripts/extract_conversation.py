#!/usr/bin/env python3
"""
Script to extract a specific conversation by ID from a Telegram JSON export
and save it to a separate file.
"""

import json
import argparse
import sys
from pathlib import Path


def extract_conversation(input_file, conversation_id, output_file=None):
    """
    Extract a conversation by ID from the JSON export.
    
    Args:
        input_file (str): Path to the input JSON file
        conversation_id (int): ID of the conversation to extract
        output_file (str, optional): Path to save the extracted conversation
    
    Returns:
        dict: The extracted conversation, or None if not found
    """
    try:
        # Read the input JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Navigate to the chats list
        if 'chats' in data and 'list' in data['chats']:
            chats_list = data['chats']['list']
        elif isinstance(data, list):
            # If the root is already a list
            chats_list = data
        else:
            print("Error: Unexpected JSON structure. Expected 'chats.list' or a list at root.")
            return None
        
        # Search for the conversation by ID
        conversation = None
        for chat in chats_list:
            if chat.get('id') == conversation_id:
                conversation = chat
                break
        
        if conversation is None:
            print(f"Error: Conversation with ID {conversation_id} not found.")
            print(f"Available IDs: {[chat.get('id') for chat in chats_list[:10]]}...")
            return None
        
        # Display some info about the conversation
        chat_type = conversation.get('type', 'unknown')
        num_messages = len(conversation.get('messages', []))
        chat_name = conversation.get('name', 'N/A')
        
        print(f"Found conversation:")
        print(f"  ID: {conversation_id}")
        print(f"  Name: {chat_name}")
        print(f"  Type: {chat_type}")
        print(f"  Messages: {num_messages}")
        
        # Save to output file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)
            print(f"\nConversation saved to: {output_file}")
        
        return conversation
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file. {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def list_conversations(input_file):
    """
    List all available conversations with their IDs.
    
    Args:
        input_file (str): Path to the input JSON file
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Navigate to the chats list
        if 'chats' in data and 'list' in data['chats']:
            chats_list = data['chats']['list']
        elif isinstance(data, list):
            chats_list = data
        else:
            print("Error: Unexpected JSON structure.")
            return
        
        print(f"Found {len(chats_list)} conversations:\n")
        print(f"{'ID':<15} {'Type':<20} {'Name':<40} {'Messages'}")
        print("-" * 90)
        
        for chat in chats_list:
            chat_id = chat.get('id', 'N/A')
            chat_type = chat.get('type', 'N/A')
            chat_name = chat.get('name', 'N/A')
            num_messages = len(chat.get('messages', []))
            
            # Truncate name if too long
            if len(str(chat_name)) > 37:
                chat_name = str(chat_name)[:37] + "..."
            
            print(f"{chat_id:<15} {chat_type:<20} {chat_name:<40} {num_messages}")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract a specific conversation by ID from Telegram JSON export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all conversations
  python extract_conversation.py input.json --list
  
  # Extract conversation by ID
  python extract_conversation.py input.json --id 168168628
  
  # Extract and save to specific file
  python extract_conversation.py input.json --id 168168628 --output my_chat.json
        """
    )
    
    parser.add_argument('input_file', help='Path to the input JSON file')
    parser.add_argument('--id', type=int, dest='conversation_id',
                        help='ID of the conversation to extract')
    parser.add_argument('--output', '-o', dest='output_file',
                        help='Output file path (default: conversation_<ID>.json)')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List all available conversations')
    
    args = parser.parse_args()
    
    # List conversations
    if args.list:
        list_conversations(args.input_file)
        return
    
    # Extract conversation
    if args.conversation_id is None:
        parser.error("Please specify --id or use --list to see available conversations")
    
    # Generate output filename if not provided
    output_file = args.output_file
    if output_file is None:
        output_file = f"conversation_{args.conversation_id}.json"
    
    # Extract the conversation
    conversation = extract_conversation(args.input_file, args.conversation_id, output_file)
    
    if conversation is None:
        sys.exit(1)


if __name__ == '__main__':
    main()
