# Telegram Chat to LLM Training Dataset Scripts
These scripts are particularly useful when you need to transform exported Telegram chat history into training datasets for fine-tuning Large Language Models (LLMs). The tools help you process massive Telegram JSON exports, extract specific conversations, and format them into the OpenAI chat template format.

## Overview

When you export your Telegram chat history, you get a large `result.json` file containing all your conversations. These scripts help you:

1. **Parse** the exported data to identify available chats
2. **Extract** specific conversations of interest
3. **Transform** the conversations into properly formatted training data

## Prerequisites

- Python 3.7+
- Exported Telegram chat data in JSON format (see [How to Export Telegram Chats](#how-to-export-telegram-chats))

## Installation

```bash
git clone <repository-url>
cd <repository-name>
pip install -r requirements.txt  # if applicable
```

## Scripts

### 1. `parse_chats.py` - Chat Discovery

**Purpose:** Parse the massive `result.json` file to get an overview of all available chats with their names, types, and IDs.

**Usage:**

```bash
python parse_chats.py --save-all --input result.json
```

**Output Example:**

```
--------------------------------------------------------------------------------
Name                                     Type                 ID             
--------------------------------------------------------------------------------
Giuliana                                 personal_chat        164456975     
Barbara                                  personal_chat        1141451558     
Marco                                    personal_chat        626965680       
Dove per la svolta                       private_group        1437880907   
```

**Parameters:**
- `--input`: Path to the Telegram export JSON file (required)
- `--save-all`: Save the list of chats to a file for future reference

This script helps you identify the chat IDs you'll need for the next step.

---

### 2. `extract_conversation.py` - Conversation Extraction

**Purpose:** Extract a single conversation from the main export file into a separate, manageable JSON file.

**Usage:**

```bash
python extract_conversation.py result.json --id 460911860 --output out-specific-id.json
```

**Output Example:**

```
Found conversation:
  ID: 460911860
  Name: Lorenzo
  Type: personal_chat
  Messages: 379089
```

**Parameters:**
- `result.json`: Path to the main Telegram export file (required)
- `--id`: The chat ID to extract (obtained from `parse_chats.py`)
- `--output`: Output filename for the extracted conversation

This creates a dedicated file containing only the specified conversation, making it easier to process individual chats.

---

### 3. `prepare_training_data.py` - Training Data Preparation

**Purpose:** Transform extracted conversations into the OpenAI chat template format (JSONL) ready for LLM fine-tuning. This script performs data cleaning, structuring, and formatting automatically.

**Usage:**

```bash
python prepare_training_data.py result.json --output training_data.jsonl
```

**Key Features:**

The script automatically:
- Cleans and filters messages
- Groups consecutive messages into conversation turns
- Structures data into user/assistant format
- Outputs JSONL format compatible with LLM training

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--output` | training_data.jsonl | Output file path |
| `--min-messages` | 20 | Minimum messages required per contact |
| `--turn-window` | 5 | Time window (minutes) to group consecutive messages from same person |
| `--conversation-gap` | 60 | Time gap (minutes) that separates distinct conversations |
| `--your-name` | UserName | Your name in chats (identifies assistant role messages) |
| `--include-groups` | False | Include group conversations (default: personal chats only) |

**Advanced Examples:**

```bash
# Stricter filtering with wider time windows
python prepare_training_data.py result.json \
  --min-messages 50 \
  --turn-window 10 \
  --conversation-gap 120 \
  --your-name "YourName"

# Include group chats
python prepare_training_data.py result.json --include-groups

# Custom output location
python prepare_training_data.py result.json --output datasets/my_training_data.jsonl
```

**Output Format:**

The script generates a JSONL file where each line represents a complete conversation in the OpenAI chat template format:

```json
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

## Complete Workflow

Here's the recommended step-by-step process:

### Step 1: Export Telegram Data

Export your Telegram chat history using Telegram Desktop:
1. Settings → Advanced → Export Chat History
2. Select the chats you want to export
3. Choose JSON format
4. Wait for the export to complete (can take a while for large histories)

### Step 2: Discover Available Chats

```bash
python parse_chats.py --save-all --input result.json
```

Review the output to identify which chats you want to use for training.

### Step 3: (Optional) Extract Specific Conversations

If you want to work with individual conversations separately:

```bash
python extract_conversation.py result.json --id <CHAT_ID> --output conversation_<NAME>.json
```

Repeat for each conversation of interest.

### Step 4: Prepare Training Data

Transform the conversations into training format:

```bash
python prepare_training_data.py result.json \
  --output training_data.jsonl \
  --min-messages 20 \
  --your-name "YourName"
```

### Step 5: Fine-tune Your Model

Use the generated `training_data.jsonl` file with your preferred fine-tuning framework (OpenAI API, Hugging Face, etc.).

## How to Export Telegram Chats

To get the `result.json` file needed by these scripts:

1. Open **Telegram Desktop** (not mobile app)
2. Go to **Settings** → **Advanced** → **Export Chat History**
3. Select which chats to export
4. Choose **JSON** as the export format
5. Disable media export (optional, but recommended to reduce file size)
6. Click **Export** and wait for completion
7. Find the `result.json` file in your export folder


## Use Cases

- Create a personalized chatbot that mimics your writing style
- Train a model to understand your communication patterns
- Build conversational AI with your personality
- Research and experiment with personal language models

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see [LICENSE](../LICENSE) file for details.

## Acknowledgments

Built as part of the LLM Chat Like Me project. See the [blog post](https://bigghis.github.io) for more details on the methodology and motivation.
