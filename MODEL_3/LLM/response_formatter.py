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
                box=box.ROUNDED,
                padding=(1, 2)
            ))
        else:
            # Simple text response
            self.console.print(Panel(
                response_text,
                title="[bold green]🎓 Tutor Response[/bold green]",
                border_style="green",
                box=box.ROUNDED,
                padding=(1, 2)
            ))
        
        self.console.print()
    
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
    
    def print_correction(self, original: str, corrected: str, explanation: str):
        """
        Print a correction in a structured format.
        
        Args:
            original: User's original text
            corrected: Corrected version
            explanation: Why it was corrected
        """
        self.console.print()
        
        # Original sentence
        self.console.print(Panel(
            f"[red]{original}[/red]",
            title="[bold red]❌ Original[/bold red]",
            border_style="red",
            box=box.SIMPLE
        ))
        
        # Corrected sentence
        self.console.print(Panel(
            f"[green]{corrected}[/green]",
            title="[bold green]✅ Corrected[/bold green]",
            border_style="green",
            box=box.SIMPLE
        ))
        
        # Explanation
        self.console.print(Panel(
            Markdown(explanation),
            title="[bold blue]💡 Explanation[/bold blue]",
            border_style="blue",
            box=box.ROUNDED
        ))
        
        self.console.print()
    
    def print_translation(self, original: str, translated: str, notes: str = None):
        """
        Print a translation in a structured format.
        
        Args:
            original: Original text
            translated: Translated text
            notes: Optional notes/explanation
        """
        self.console.print()
        
        self.console.print(Panel(
            f"[cyan]{original}[/cyan]\n\n[yellow]→[/yellow]\n\n[green]{translated}[/green]",
            title="[bold]🌐 Translation[/bold]",
            border_style="magenta",
            box=box.DOUBLE
        ))
        
        if notes:
            self.console.print(Panel(
                notes,
                title="[bold blue]📝 Notes[/bold blue]",
                border_style="blue",
                box=box.ROUNDED
            ))
        
        self.console.print()
    
    def print_general_answer(self, question: str, answer: str):
        """
        Print a general Q&A response.
        
        Args:
            question: User's question
            answer: LLM's answer
        """
        self.console.print()
        
        # Question
        self.console.print(Panel(
            f"[cyan]{question}[/cyan]",
            title="[bold]❓ Question[/bold]",
            border_style="cyan",
            box=box.ROUNDED
        ))
        
        # Answer
        self.console.print(Panel(
            Markdown(answer),
            title="[bold green]💬 Answer[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2)
        ))
        
        self.console.print()
    
    def print_error(self, error_message: str):
        """Print an error message."""
        self.console.print()
        self.console.print(Panel(
            f"[red]{error_message}[/red]",
            title="[bold red]⚠️  Error[/bold red]",
            border_style="red",
            box=box.HEAVY
        ))
        self.console.print()
    
    def print_thinking(self):
        """Show a thinking indicator."""
        return self.console.status(
            "[bold magenta]🤔 Thinking...[/bold magenta]",
            spinner="dots"
        )


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
    
    # Example 2: Translation
    print("\n" + "="*70)
    print("EXAMPLE 2: Translation")
    print("="*70)
    
    formatter.print_translation(
        original="How do you say 'I love you' in German?",
        translated="Ich liebe dich",
        notes="Use 'Ich hab dich lieb' for friends/family (less intense)"
    )
    
    # Example 3: General question
    print("\n" + "="*70)
    print("EXAMPLE 3: General Question")
    print("="*70)
    
    formatter.print_general_answer(
        question="What's the capital of Germany?",
        answer="The capital of Germany is **Berlin**. It's also the largest city with about 3.7 million people."
    )
    
    # Example 4: Simple formatter
    print("\n" + "="*70)
    print("EXAMPLE 4: Simple Formatter (Less Visual Noise)")
    print("="*70)
    
    simple = SimpleFormatter()
    simple.format_and_print(
        llm_response,
        user_input="Ich habe ins Kino gegangen"
    )