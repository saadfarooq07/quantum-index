from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Button, Log, Label
from textual.binding import Binding
import asyncio
import httpx
import json

class QuantumSearchTUI(App):
    CSS = """
    Screen {
        align: center middle;
    }

    #search-container {
        width: 95%;
        height: 90%;
        border: heavy $accent;
        padding: 1;
    }

    #input-container {
        height: auto;
        margin: 1;
    }

    #results-container {
        height: 1fr;
        margin: 1;
    }

    Input {
        width: 1fr;
        margin: 1;
    }

    Button {
        width: 15;
        margin: 1;
    }

    Log {
        height: 100%;
        border: solid $accent;
        background: $surface-darken-1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("ctrl+s", "search", "Search", show=True),
        Binding("ctrl+c", "clear", "Clear", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.client = httpx.AsyncClient(base_url="http://localhost:8000")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="search-container"):
            with Horizontal(id="input-container"):
                yield Input(placeholder="Enter your search query...", id="search-input")
                yield Button("Search", variant="primary", id="search-button")
            with Vertical(id="results-container"):
                yield Label("Search Results:")
                yield Log(id="results-log", wrap=True, markup=True)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "search-button":
            self.action_search()

    async def action_search(self) -> None:
        query = self.query_one("#search-input").value
        if not query:
            return

        results_log = self.query_one("#results-log")
        results_log.write("[blue]Searching...[/blue]")

        try:
            response = await self.client.post(
                "/search",
                json={"query": query},
                timeout=30.0
            )
            results = response.json()
            
            results_log.clear()
            for idx, result in enumerate(results, 1):
                results_log.write(f"[green]Result {idx}:[/green]")
                results_log.write(f"[yellow]File:[/yellow] {result['path']}")
                results_log.write(f"[yellow]Lines:[/yellow] {result['start_line']}-{result['end_line']}")
                results_log.write(f"[white]{result['content']}[/white]")
                results_log.write("")
        except Exception as e:
            results_log.write(f"[red]Error: {str(e)}[/red]")

    def action_clear(self) -> None:
        self.query_one("#search-input").value = ""
        self.query_one("#results-log").clear()

def main():
    app = QuantumSearchTUI()
    app.run()

if __name__ == "__main__":
    main()
