# Chat Like Me 💬

Create your own personalized AI chatbot that talks just like you! This project provides a complete end-to-end solution: from exporting your Telegram chats, to fine-tuning a language model, to deploying it as a Telegram bot.

## Overview

**Chat Like Me** is a complete toolkit for creating a personalized AI chatbot:

1. 📊 **Data Preparation Scripts** - Convert Telegram chat exports into LLM training datasets
2. 🎯 **Fine-tuning Configuration** - Ready-to-use Axolotl config for model training
3. 🤖 **Telegram Bot** - Deploy your fine-tuned model as an interactive Telegram bot

### What Can You Do With This?

- 🤖 Train a chatbot that sounds like you
- 📊 Analyze your communication patterns
- 🎨 Build conversational AI with your personality
- 🔬 Research and experiment with personal language models

## Features

### Data Preparation
- ✨ Easy-to-use command-line scripts
- 🔍 Parse and discover all chats in your Telegram export
- 📤 Extract specific conversations by ID
- 🎯 Smart filtering by message count, chat type, and more
- ⏰ Intelligent grouping of messages into conversation turns
- 📝 Automatic formatting into OpenAI chat template format (JSONL)
- 👥 Support for both personal and group chats
- 🧹 Built-in data cleaning and validation

### Fine-tuning
- 🔧 Pre-configured Axolotl setup for efficient training
- 💾 Optimized LoRA/QLoRA configurations
- 🚀 Works with popular base models (Llama, Mistral, etc.)

### Deployment
- 🤖 Ready-to-deploy Telegram bot
- 💬 Natural conversation interface
- ⚡ Efficient inference with your fine-tuned model

## Quick Start

### Prerequisites

- Python 3.7 or higher
- Exported Telegram chat data in JSON format

### Installation

```bash
git clone https://github.com/yourusername/chat-like-me.git
cd chat-like-me
```

No external dependencies needed! All scripts use Python standard library.

## Usage

### Step 1: Export Your Telegram Chats

1. Open **Telegram Desktop** (not mobile app)
2. Go to **Settings** → **Advanced** → **Export Chat History**
3. Select the chats you want to export
4. Choose **JSON** as the export format
5. Disable media export (optional, to reduce file size)
6. Click **Export** and wait for completion
7. Locate the `result.json` file in your export folder

### Step 2: Discover Available Chats

```bash
python scripts/parse_chats.py --save-all --input result.json
```

This will show you all available chats with their IDs, types, and names:

```
--------------------------------------------------------------------------------
Name                                     Type                 ID             
--------------------------------------------------------------------------------
Giuliana                                 personal_chat        164456975     
Marco                                    personal_chat        626965680       
Family Group                             private_group        1437880907   
```

### Step 3: (Optional) Extract Specific Conversations

If you want to work with individual conversations separately:

```bash
python scripts/extract_conversation.py result.json --id 460911860 --output chat_with_marco.json
```

### Step 4: Prepare Training Data

Transform your conversations into LLM training format:

```bash
python scripts/prepare_training_data.py result.json \
  --output training_data.jsonl \
  --min-messages 20 \
  --your-name "YourName"
```

### Step 5: Fine-tune Your Model

Use the included Axolotl configuration to fine-tune your model:

```bash
# Configure your training parameters in config/axolotl_config.yml
# Then run the training (see Fine-tuning section below)
```

Or use the generated `training_data.jsonl` file with your preferred fine-tuning platform:
- Axolotl (included configuration)
- OpenAI API
- Hugging Face
- Your custom training pipeline

### Step 6: Deploy Your Telegram Bot

Once your model is trained, deploy it as a Telegram bot:

```bash
# Configure your bot token in bot/config.py
# Run the bot (see Deployment section below)
python bot/telegram_bot.py
```

## Project Structure

```
chat-like-me/
├── scripts/              # Data preparation scripts
│   ├── parse_chats.py
│   ├── extract_conversation.py
│   └── prepare_training_data.py
├── config/              # Fine-tuning configurations
│   └── axolotl_config.yml
├── bot/                 # Telegram bot source code
│   ├── telegram_bot.py
│   └── config.py
├── README.md
└── LICENSE
```

## Detailed Documentation

### Part 1: Data Preparation Scripts

#### 1. `parse_chats.py` - Chat Discovery

Parse the Telegram export to identify all available chats.

**Basic Usage:**
```bash
python scripts/parse_chats.py --input result.json
```

**Filter by name:**
```bash
python scripts/parse_chats.py --name "Marco" --input result.json
```

**Filter by type:**
```bash
python scripts/parse_chats.py --type personal_chat --input result.json
```

#### 2. `extract_conversation.py` - Conversation Extraction

Extract a specific conversation by ID into a separate file.

**Usage:**
```bash
python scripts/extract_conversation.py result.json --id 168168628 --output my_chat.json
```

**List all conversations:**
```bash
python scripts/extract_conversation.py result.json --list
```

#### 3. `prepare_training_data.py` - Training Data Preparation

Transform conversations into OpenAI-compatible training format.

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--output` | training_data.jsonl | Output file path |
| `--min-messages` | 20 | Minimum messages required per contact |
| `--turn-window` | 5 | Time window (minutes) to group consecutive messages |
| `--conversation-gap` | 60 | Time gap (minutes) that separates conversations |
| `--your-name` | Pasquale | Your name in chats (identifies your messages) |
| `--include-groups` | False | Include group conversations |

**Advanced Examples:**

```bash
# Stricter filtering with custom time windows
python scripts/prepare_training_data.py result.json \
  --min-messages 50 \
  --turn-window 10 \
  --conversation-gap 120 \
  --your-name "YourName"

# Include group chats
python scripts/prepare_training_data.py result.json --include-groups

# Custom output location
python scripts/prepare_training_data.py result.json --output datasets/my_data.jsonl
```

**Output Format:**

The script generates a JSONL file where each line represents a complete conversation:

```json
{"messages": [
  {"role": "system", "content": "You are YourName, chatting with Marco..."},
  {"role": "user", "name": "Marco", "content": "Hey, how are you?"},
  {"role": "assistant", "name": "YourName", "content": "I'm great! How about you?"}
]}
```

### Part 2: Fine-tuning with Axolotl

_(Configuration files and detailed instructions coming soon)_

The `config/` directory will contain pre-configured Axolotl YAML files optimized for training a personalized chatbot on your data.

**Key features:**
- LoRA/QLoRA configuration for efficient training
- Optimized hyperparameters for conversational models
- Support for various base models (Llama, Mistral, etc.)
- Memory-efficient training on consumer GPUs

### Part 3: Telegram Bot Deployment

_(Bot source code and setup instructions coming soon)_

The `bot/` directory will contain a complete Telegram bot implementation that:
- Loads your fine-tuned model
- Handles conversations naturally
- Supports context management
- Includes deployment scripts

## How It Works

### End-to-End Pipeline

1. **📥 Data Export**: Export your Telegram chat history to JSON
2. **🔍 Data Parsing**: Parse and discover available conversations
3. **🎯 Data Filtering**: Filter by message count, chat type, and relevance
4. **📊 Data Processing**: 
   - Remove service/automated messages
   - Group messages into conversation turns
   - Format for LLM training
5. **🎓 Model Fine-tuning**: Train a model on your conversational style using Axolotl
6. **🚀 Bot Deployment**: Deploy your personalized model as a Telegram bot
7. **💬 Interact**: Chat with your AI clone!

## Data Privacy & Security

⚠️ **Important**: Your chat data is personal and sensitive. These scripts:

- Run entirely **locally** on your machine
- Do **not** send data to any external service
- Do **not** require internet connection
- Give you full control over what data to export and process

**Recommendations:**
- Keep your exported JSON files secure
- Don't share your training data publicly unless you're comfortable with it
- Review the generated training data before using it
- Consider anonymizing sensitive information if needed

## Use Cases

### 🤖 Personal AI Assistant
Deploy a bot that responds to messages in your style when you're busy or unavailable.

### ✍️ Writing Assistant
Generate message drafts and responses in your unique voice.

### 📊 Communication Analysis
Study and understand your conversation patterns and communication style.

### 🎭 Digital Clone
Create an interactive AI version of yourself for creative projects or experiments.

### 🎓 Research & Learning
Explore fine-tuning techniques and conversational AI development.

## Project Status

- ✅ **Data Preparation Scripts** - Complete and tested
- 🚧 **Fine-tuning Configuration** - Coming soon
- 🚧 **Telegram Bot** - Coming soon

## Troubleshooting

### Data Preparation

**"No chats meet the criteria"**  
Try lowering the `--min-messages` threshold or check if your export contains valid conversations.

**"Unexpected JSON structure"**  
Ensure you exported in JSON format from Telegram Desktop, not mobile.

**Unicode/Encoding Issues**  
The scripts handle UTF-8 encoding automatically, but ensure your terminal supports Unicode.

### Fine-tuning & Deployment

_(Troubleshooting guides will be added as features are released)_

## Contributing

Contributions are welcome! Feel free to:

- 🐛 Report bugs
- 💡 Suggest new features
- 🔧 Submit pull requests
- 📖 Improve documentation

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with ❤️ for anyone who wants to create personalized AI models. 

For more details on the methodology and motivation, visit the [project blog](https://bigghis.github.io).

## Support

If you find this project useful, please consider:
- ⭐ Starring the repository
- 🐦 Sharing it with others
- 🤝 Contributing improvements

---

**Disclaimer**: This project is for educational and personal use. Ensure you have the right to process and use the chat data you're working with. Respect privacy and obtain necessary consents if you plan to use conversations involving other people.

