from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Label

class SimpleApp(App):
    """A simple Textual app to test the environment."""
    
    BINDINGS = [("q", "quit", "Quit")]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Hello from Quantum TUI!")
        yield Footer()

if __name__ == "__main__":
    app = SimpleApp()
    app.run()
