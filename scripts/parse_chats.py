#!/usr/bin/env python3
"""
Parse Telegram chat export JSON and extract chat information.
"""

import json
import argparse


def parse_chats(json_file_path):
    """
    Parse the JSON file and extract name, type, and id from all chats.
    
    Args:
        json_file_path: Path to the result.json file
        
    Returns:
        List of dictionaries containing name, type, and id for each chat
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chats_info = []
    
    # Navigate to the chats list
    if 'chats' in data and 'list' in data['chats']:
        for chat in data['chats']['list']:
            chat_info = {
                'name': chat.get('name') or 'N/A',
                'type': chat.get('type') or 'N/A',
                'id': chat.get('id', 'N/A')
            }
            chats_info.append(chat_info)
    
    return chats_info


def filter_chats(chats, name=None, chat_type=None, chat_id=None):
    """
    Filter chats based on provided criteria.
    
    Args:
        chats: List of chat dictionaries
        name: Filter by name (partial match, case-insensitive)
        chat_type: Filter by type
        chat_id: Filter by specific ID
        
    Returns:
        Filtered list of chats
    """
    filtered = chats
    
    if name:
        filtered = [c for c in filtered if name.lower() in c['name'].lower()]
    
    if chat_type:
        filtered = [c for c in filtered if c['type'] == chat_type]
    
    if chat_id is not None:
        filtered = [c for c in filtered if c['id'] == chat_id]
    
    return filtered


def display_chats(chats, show_full=False):
    """
    Display chat information.
    
    Args:
        chats: List of chat dictionaries
        show_full: If True, display full JSON; if False, display table
    """
    if not chats:
        print("No chats found matching the criteria.")
        return
    
    if show_full:
        print(json.dumps(chats, indent=2, ensure_ascii=False))
    else:
        print(f"Total chats found: {len(chats)}\n")
        print("-" * 80)
        print(f"{'Name':<40} {'Type':<20} {'ID':<15}")
        print("-" * 80)
        for chat in chats:
            print(f"{chat['name']:<40} {chat['type']:<20} {chat['id']:<15}")


def main():
    parser = argparse.ArgumentParser(
        description='Parse Telegram chat export and filter chats by name, type, or ID',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all chats
  python3 parse_chats.py
  
  # Find chat by name (shows ID)
  python3 parse_chats.py --name "Marco"
  
  # Find chat by name with full details
  python3 parse_chats.py --name "Marco" --full
  
  # Filter by chat type
  python3 parse_chats.py --type personal_chat
  
  # Find chat by ID
  python3 parse_chats.py --id 777000
  
  # Combine filters
  python3 parse_chats.py --type personal_chat --name "Sara"
  
  # Save filtered results to file
  python3 parse_chats.py --name "Marco" --output marco_chat.json
        """
    )
    
    parser.add_argument(
        '--name',
        type=str,
        help='Filter chats by name (partial match, case-insensitive)'
    )
    
    parser.add_argument(
        '--type',
        type=str,
        help='Filter chats by type (e.g., personal_chat, saved_messages)'
    )
    
    parser.add_argument(
        '--id',
        type=int,
        help='Filter chat by specific ID'
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Show full chat details in JSON format instead of table'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Save results to specified file (JSON format)'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        default='result.json',
        help='Input JSON file (default: result.json)'
    )
    
    parser.add_argument(
        '--save-all',
        action='store_true',
        help='Save all results to chats_list.txt and chats_list.json (only when no filters applied)'
    )
    
    args = parser.parse_args()
    
    # Parse the chats
    chats = parse_chats(args.input)
    
    # Check if any filters are applied
    has_filters = any([args.name, args.type, args.id is not None])
    
    # Filter chats if criteria provided
    if has_filters:
        chats = filter_chats(chats, name=args.name, chat_type=args.type, chat_id=args.id)
    
    # Display results
    display_chats(chats, show_full=args.full)
    
    # Save to output file if specified
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(chats, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {args.output}")
    
    # Save all results to default files (only when no filters and --save-all flag is used)
    if not has_filters and args.save_all:
        print("\n" + "-" * 80)
        output_file = 'chats_list.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Total chats found: {len(chats)}\n\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Name':<40} {'Type':<20} {'ID':<15}\n")
            f.write("-" * 80 + "\n")
            for chat in chats:
                f.write(f"{chat['name']:<40} {chat['type']:<20} {chat['id']:<15}\n")
        
        print(f"Results also saved to {output_file}")
        
        # Optional: Save as JSON
        json_output = 'chats_list.json'
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(chats, f, indent=2, ensure_ascii=False)
        
        print(f"JSON output saved to {json_output}")


if __name__ == '__main__':
    main() 