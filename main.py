#!/usr/bin/env python3
"""
News Summary CLI Tool

A CLI tool for generating AI-powered news summaries from multiple sources.
Supports multiple LLM providers including OpenAI, Anthropic, Ollama, and Azure OpenAI.
"""

import asyncio
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator import NewsOrchestrator
from src.config_loader import ConfigLoader

# Load environment variables
load_dotenv()
console = Console()

@click.command()
@click.option(
    "--query",
    "-q",
    multiple=True,
    default=["top news stories"],
    help="Search query for news. You can specify multiple queries (e.g., -q query1 -q query2). Defaults to 'top news stories' if not provided."
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "anthropic", "ollama", "gemini"]),
    help="LLM provider to use (defaults to configuration setting)"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (defaults to what is set in configuration or current directory/reports if not specified)"
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to custom configuration file"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output"
)
@click.option(
    "--display",
    "-d",
    is_flag=True,
    help="Display output on console instead of saving to file"
)
def main(query, provider, output, config, verbose, display):
    """
    Generate AI-powered news summaries from multiple sources.
    
    This tool fetches and summarizes news based on the provided query
    
    Examples:
        tldr-news-agent                          # Generate full report with default settings
        tldr-news-agent --provider ollama        # Use local Ollama LLM
        tldr-news-agent --output my_news.md      # Save to custom file
    """
    asyncio.run(_async_main(query, provider, output, config, verbose, display))


async def _async_main(query, provider, output, config, verbose, display):
    """Async main function."""
    try:
        # Initialize configuration
        config_loader = ConfigLoader(config) if config else ConfigLoader()
        
        if verbose:
            click.echo("🔧 Configuration loaded successfully")
            if provider:
                click.echo(f"🤖 Using LLM provider: {provider}")
            
        # Initialize orchestrator
        orchestrator = NewsOrchestrator(config_loader, provider)
        
        # Run full report
        click.echo("🚀 Starting comprehensive news summary generation...")
        
        report = await orchestrator.generate_news_report(*query, save_to_file=not display, output_path=output)
        
        click.echo("✅ All Done!")
        if display:
            markdown = Markdown(report)
            console.print(markdown)

    except KeyboardInterrupt:
        click.echo("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except (ValueError, ImportError, KeyError, ConnectionError) as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@click.group()
def cli():
    """News Summary CLI - AI-powered news summarization tool."""
    # This is the main CLI group that holds all subcommands

@cli.command()
def list_providers():
    """List available LLM providers and their configuration."""
    try:
        config_loader = ConfigLoader()
        llm_config = config_loader.get_llm_config()
        
        click.echo("🤖 Available LLM Providers:")
        click.echo("=" * 40)
        
        current_provider = llm_config.get("provider", "ollama")
        models = llm_config.get("models", {})
        
        for provider_name, model_config in models.items():
            status = "✅ (current)" if provider_name == current_provider else "⚪"
            click.echo(f"{status} {provider_name}")
            click.echo(f"   Model: {model_config.get('model', 'N/A')}")
            
            if provider_name == "ollama":
                base_url = model_config.get('base_url')
                click.echo(f"   Base URL: {base_url}")
            elif 'api_key_env' in model_config:
                api_key_env = model_config['api_key_env']
                import os
                has_key = "✅" if os.getenv(api_key_env) else "❌"
                click.echo(f"   API Key ({api_key_env}): {has_key}")
            
            click.echo()
    
    except (ValueError, ImportError, KeyError) as e:
        click.echo(f"❌ Error loading configuration: {str(e)}", err=True)


@cli.command()
@click.option(
    "--host",
    "-h",
    default="127.0.0.1",
    help="Host address to bind to (default: 127.0.0.1)"
)
@click.option(
    "--port",
    "-p",
    type=int,
    default=5000,
    help="Port to bind to (default: 5000)"
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="Enable debug mode"
)
def serve(host, port, debug):
    """Start the web server to browse news reports."""
    try:
        click.echo("🌐 Starting TLDR News Agent web server...")
        click.echo(f"📍 Server will be available at: http://{host}:{port}")
        click.echo("📰 Browse your news reports in a beautiful web interface!")
        click.echo("🛑 Press Ctrl+C to stop the server")
        click.echo()
        
        # Import and start the Flask app
        from src.server import app
        app.run(debug=debug, host=host, port=port)
        
    except ImportError as e:
        click.echo(f"❌ Error importing server module: {str(e)}", err=True)
        click.echo("💡 Make sure Flask is installed: pip install flask", err=True)
        sys.exit(1)
    except OSError as e:
        if "Address already in use" in str(e):
            click.echo(f"❌ Port {port} is already in use. Try a different port with --port", err=True)
        else:
            click.echo(f"❌ Network error: {str(e)}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        sys.exit(1)


# Add CLI commands to main
cli.add_command(main, name="run")

if __name__ == "__main__":
    # Use CLI in all cases
    cli()
