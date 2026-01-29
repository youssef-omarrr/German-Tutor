"""
LLM Response Formatter
Makes Groq/LLM outputs look beautiful in the terminal
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import box
import re


class ResponseFormatter:
    """
    Formats LLM responses for beautiful terminal output.
    """
    
    def __init__(self):
        self.console = Console()
    
    def format_and_print(self, response_text: str, user_input: str = None):
        """
        Format and print LLM response beautifully.
        
        Args:
            response_text: Raw LLM output
            user_input: Optional user input to show context
        """
        
        # Show user input if provided
        if user_input:
            self.console.print()
            self.console.print(Panel(
                f"[cyan]{user_input}[/cyan]",
                title="[bold]You said[/bold]",
                border_style="cyan",
                box=box.ROUNDED
            ))
        
        # Format the response
        self.console.print()
        
        # Check if response has markdown formatting
        if self._has_markdown(response_text):
            # Render as markdown
            md = Markdown(response_text)
            self.console.print(Panel(
                md,
                title="[bold green]🎓 Tutor Response[/bold green]",
                border_style="green",
                box=box.DOUBLE,
                padding=(1, 2)
            ))
        else:
            # Simple text response
            self.console.print(Panel(
                response_text,
                title="[bold green]🎓 Tutor Response[/bold green]",
                border_style="green",
                box=box.DOUBLE,
                padding=(1, 2)
            ))
        
        self.console.print()
        return _remove_md(response_text)
    
    def _has_markdown(self, text: str) -> bool:
        """Check if text contains markdown formatting."""
        markdown_patterns = [
            r'\*\*.*?\*\*',  # Bold
            r'\*.*?\*',      # Italic
            r'^#+\s',        # Headers
            r'^\-\s',        # Lists
            r'^\d+\.\s',     # Numbered lists
        ]
        return any(re.search(pattern, text, re.MULTILINE) for pattern in markdown_patterns)
    
        
    import re

class SimpleFormatter:
    """
    Simpler formatter with less visual noise.
    Good for users who prefer minimal formatting.
    """
    
    def __init__(self):
        self.console = Console()
    
    def format_and_print(self, response_text: str, user_input: str = None):
        """Simple formatted output."""
        
        if user_input:
            self.console.print(f"\n[bold cyan]You:[/bold cyan] {user_input}")
        
        self.console.print(f"\n[bold green]Tutor:[/bold green]")
        
        # Render markdown if present
        if '**' in response_text or '*' in response_text:
            self.console.print(Markdown(response_text))
        else:
            self.console.print(response_text)
        
        self.console.print()
        return _remove_md(response_text)

def _remove_md(text: str):
    """Simple markdown removal for natural speech."""
    
    # Remove all markdown formatting
    clean = re.sub(r"#+\s+", "", text)  # Headings
    clean = re.sub(r"[*_`]{1,2}(.*?)[*_`]{1,2}", r"\1", clean)  # Bold/italic/code
    clean = re.sub(r"^>\s+", "", clean, flags=re.MULTILINE)  # Blockquotes
    clean = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", clean)  # Links
    clean = re.sub(r"!\[.*?\]\(.*?\)", "", clean)  # Images
    clean = re.sub(r"```.*?```", "", clean, flags=re.DOTALL)  # Code blocks
    
    # Replace symbols
    clean = clean.replace("/", " slash ")
    clean = clean.replace("&", " and ")
    clean = clean.replace("#", " ")
    
    # Normalize whitespace
    clean = re.sub(r"\s+", " ", clean).strip()
    
    # Add natural pauses by adding extra space after punctuation
    clean = re.sub(r"([.!?;])\s+", r"\1  ", clean)
    clean = re.sub(r",\s+", r", ", clean)
    
    return clean


# ========================================================================
#                           USAGE EXAMPLES
# ========================================================================

if __name__ == "__main__":
    # Example LLM responses
    
    formatter = ResponseFormatter()
    
    # Example 1: Correction with markdown
    print("\n" + "="*70)
    print("EXAMPLE 1: Formatted Correction")
    print("="*70)
    
    llm_response = """Quick fix → **Ich bin ins Kino gegangen**

'Gehen' is a motion verb, so it takes 'sein' not 'haben' in Perfekt. 

**Other ways to say it:**
- *Ich ging ins Kino* (simple past)
- *Ich bin gestern ins Kino gegangen* (with time)

Keep it up! 🎯"""
    
    formatter.format_and_print(
        llm_response,
        user_input="Ich habe ins Kino gegangen"
    )
    
    # Example 2: Simple formatter
    print("\n" + "="*70)
    print("EXAMPLE 2: Simple Formatter (Less Visual Noise)")
    print("="*70)
    
    simple = SimpleFormatter()
    simple.format_and_print(
        llm_response,
        user_input="Ich habe ins Kino gegangen"
    )