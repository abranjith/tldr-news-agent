# 📰 TL;DR NEWS

An AI-powered CLI tool that fetches and summarizes news articles from multiple sources, providing concise and informative summaries for quick consumption. Built with flexibility to support multiple LLM providers including local models.

## ✨ Features

- **News Search**: Uses underlying search engine to fetch current news on the provided topics (defaults to "top news stores")

- **Flexible LLM Support**: Choose from multiple AI (LLM) providers:
  - Ollama (Local models)
  - Google (Gemini)
  - OpenAI
  - Anthropic (Claude) etc.

- **Smart Summarization**:
  - Summarizes news articles, providing concise and informative summaries on given queries and generates structured markdown report using AI
  - Focus on readability
  - Source attribution

## Sample reports

*Note* - This is for reference only

### Rendered to terminal

![Alt text](./docs/images/console_report.png)


### Markdown file

![Alt text](./docs/images/md_report.png)

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) for package management. Although, uv is recomended pip should work fine as well
- API keys for your chosen LLM provider. Note that for local LLMs (say ollama) API key may not be needed

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd tldr-news-agent
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

4. **Run the tool**:
   ```bash

   # Run with default settings
   uv run python main.py run
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with your API keys:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here

```

### LLM Provider Configuration

The tool supports multiple LLM providers. Note that LLM needs to be support tool usage.
Edit `src/config.yaml` to configure:

```yaml
llm:
  provider: "openai"  # openai, anthropic, ollama, gemini
  
  models:
    openai:
      model: "gpt-4o-mini"
      api_key_env: "OPENAI_API_KEY"
    
    ollama:
      model: "llama3.2:3b"
      base_url: "http://localhost:11434/v1"
```

## 📋 Usage

### Basic Usage

```bash
# Generate full news report with default settings (top news stories)
uv run python main.py run

# Search for specific queries
uv run python main.py run -q "climate change" -q "football news"

# Generate full news report with default settings and render on console (as markdown)
uv run python main.py --display

# Generate with specific LLM provider
uv run python main.py run --provider ollama

# Save to custom file
uv run python main.py run --output my_news_report.md

# Verbose output
uv run python main.py run --verbose

# List available LLM providers
uv run python main.py list-providers

# Show help
uv run python main.py --help
```
### Important Tips

- Needless to say using better LLMs will yield better results. Also make sure to use LLMs that support tool usage
- You can specify multiple queries using `-q` or `--query` option. Use this to search for specific topics or news items just like you would in a search engine
- Make sure to configure your `.env` file with the required API keys for the LLM provider you choose
- Make sure to configure `src/config.yaml` with the correct settings specially if the default settings do not work for you.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Pydantic AI](https://ai.pydantic.dev/)
- Supports multiple search engines - [Google PSE](https://programmablesearchengine.google.com/) and [DuckDuckGo](https://duckduckgo.com/) (also see [DDGS](https://github.com/deedy5/ddgs)) for news search. Default is DuckDuckGo
- Console markdown rendering supported by [Rich](https://github.com/Textualize/rich)
- [Click](https://github.com/pallets/click) for CLI interface