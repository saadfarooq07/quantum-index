from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, DataTable, Label, ProgressBar, Pretty
from textual.binding import Binding
from textual.reactive import reactive
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import asyncio
from typing import Dict, List

class CircularProgress(Container):
    """A circular progress indicator with label"""
    progress = reactive(0.0)
    label = reactive("")
    
    def __init__(self, label: str):
        super().__init__()
        self.label = label
    
    def compose(self) -> ComposeResult:
        yield Label(self.label, classes="progress-label")
        yield ProgressBar(total=100, show_eta=False)
    
    def watch_progress(self, value: float):
        """Update progress bar when progress changes"""
        self.query_one(ProgressBar).update(progress=int(value * 100))

class MetricsPanel(Container):
    """Enhanced panel showing quantum metrics and Metal acceleration status"""
    def compose(self) -> ComposeResult:
        yield Label("Quantum Metrics", classes="title")
        with Horizontal():
            yield CircularProgress("Token\nConfidence")
            yield CircularProgress("Context\nCoherence")
            yield CircularProgress("Retrieval\nRelevance")
            yield CircularProgress("Human\nTrust")
        yield DataTable()
    
    def update_metrics(self, metrics: Dict[str, float]):
        # Update circular progress indicators
        progress_bars = self.query(CircularProgress)
        for progress, value in zip(progress_bars, metrics.values()):
            progress.progress = value
        
        # Update detailed metrics table
        table = self.query_one(DataTable)
        table.clear()
        table.add_columns("Metric", "Value", "Status")
        for key, value in metrics.items():
            status = self._get_status_text(value)
            table.add_row(key, f"{value:.4f}", status)
    
    def _get_status_text(self, value: float) -> Text:
        if value >= 0.8:
            return Text("GOOD", style="bold green")
        elif value >= 0.6:
            return Text("WARNING", style="bold yellow")
        return Text("CRITICAL", style="bold red")

class TokenStateView(Container):
    """Enhanced view showing current token states and probabilities"""
    def compose(self) -> ComposeResult:
        yield Label("Token States", classes="title")
        yield DataTable()
        yield Label("Active Tokens", classes="subtitle")
        with Horizontal():
            yield Progress(
                SpinnerColumn(),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
            )
    
    def update_states(self, states: List[Dict]):
        table = self.query_one(DataTable)
        table.clear()
        table.add_columns("Token", "Confidence", "Coherence", "Status")
        for state in states:
            status = self._get_status_indicator(state)
            table.add_row(
                state["token"],
                f"{state['confidence']:.4f}",
                f"{state['coherence']:.4f}",
                status
            )
    
    def _get_status_indicator(self, state: Dict) -> Text:
        avg = (state["confidence"] + state["coherence"]) / 2
        if avg >= 0.8:
            return Text("●", style="bold green")
        elif avg >= 0.6:
            return Text("●", style="bold yellow")
        return Text("●", style="bold red")

class RealityGuardPanel(Container):
    """Enhanced panel showing reality check status and warnings"""
    warning_count = reactive(0)
    
    def compose(self) -> ComposeResult:
        yield Label("Reality Guard", classes="title")
        with Horizontal():
            yield Label("Active Warnings:", classes="warning-label")
            yield Label("0", id="warning-count")
        yield DataTable()
        yield Pretty({})  # For detailed warning info
    
    def update_warnings(self, warnings: List[Dict]):
        table = self.query_one(DataTable)
        table.clear()
        table.add_columns("Type", "Severity", "Message", "Status")
        
        self.warning_count = len(warnings)
        self.query_one("#warning-count").update(str(self.warning_count))
        
        for warning in warnings:
            status = self._get_severity_indicator(warning["severity"])
            table.add_row(
                warning["type"],
                warning["severity"],
                warning["message"],
                status
            )
        
        # Update detailed warning info
        self.query_one(Pretty).update({
            "total_warnings": self.warning_count,
            "severity_breakdown": self._get_severity_breakdown(warnings),
            "latest_warning": warnings[-1] if warnings else None
        })
    
    def _get_severity_indicator(self, severity: str) -> Text:
        colors = {
            "HIGH": "bold red",
            "MEDIUM": "bold yellow",
            "LOW": "bold green"
        }
        return Text("⬤", style=colors.get(severity, "bold white"))
    
    def _get_severity_breakdown(self, warnings: List[Dict]) -> Dict[str, int]:
        breakdown = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for warning in warnings:
            breakdown[warning["severity"]] += 1
        return breakdown

class QuantumTUI(App):
    """Enhanced TUI application for quantum system monitoring"""
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
        background: $surface;
    }
    
    .title {
        background: $accent;
        color: $text;
        padding: 1;
        text-align: center;
        text-style: bold;
        border: tall $accent;
    }
    
    .subtitle {
        color: $text-muted;
        padding: 1;
    }
    
    .progress-label {
        text-align: center;
        padding-bottom: 1;
    }
    
    CircularProgress {
        width: 1fr;
        height: auto;
        padding: 1;
    }
    
    .warning-label {
        color: $warning;
        padding: 1;
    }
    
    MetricsPanel {
        height: 100%;
        border: solid $accent;
    }
    
    TokenStateView {
        height: 100%;
        border: solid $accent;
    }
    
    RealityGuardPanel {
        height: 100%;
        border: solid $accent;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "toggle_focus", "Toggle Focus"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield MetricsPanel()
            yield TokenStateView()
        yield RealityGuardPanel()
        yield Footer()
    
    def on_mount(self) -> None:
        """Start the update loop when the app starts"""
        self.update_timer = asyncio.create_task(self._update_loop())
    
    async def _update_loop(self):
        """Periodically update the UI with new data"""
        while True:
            # Get metrics from quantum system
            metrics = await self._fetch_metrics()
            self.query_one(MetricsPanel).update_metrics(metrics)
            
            # Get token states
            states = await self._fetch_token_states()
            self.query_one(TokenStateView).update_states(states)
            
            # Get reality guard warnings
            warnings = await self._fetch_warnings()
            self.query_one(RealityGuardPanel).update_warnings(warnings)
            
            await asyncio.sleep(1)  # Update every second
    
    async def _fetch_metrics(self) -> Dict[str, float]:
        """Fetch current metrics from the quantum system"""
        # TODO: Implement actual metrics fetching
        return {
            "Token Confidence": 0.95,
            "Context Coherence": 0.87,
            "Retrieval Relevance": 0.92,
            "Human Trust": 0.90
        }
    
    async def _fetch_token_states(self) -> List[Dict]:
        """Fetch current token states"""
        # TODO: Implement actual token state fetching
        return [
            {"token": "quantum", "confidence": 0.95, "coherence": 0.88},
            {"token": "reality", "confidence": 0.92, "coherence": 0.85},
            {"token": "check", "confidence": 0.89, "coherence": 0.91}
        ]
    
    async def _fetch_warnings(self) -> List[Dict]:
        """Fetch current reality guard warnings"""
        # TODO: Implement actual warning fetching
        return [
            {
                "type": "Coherence",
                "severity": "LOW",
                "message": "Slight context deviation detected"
            }
        ]
    
    async def action_refresh(self) -> None:
        """Manually refresh the display"""
        metrics = await self._fetch_metrics()
        self.query_one(MetricsPanel).update_metrics(metrics)
        
        states = await self._fetch_token_states()
        self.query_one(TokenStateView).update_states(states)
        
        warnings = await self._fetch_warnings()
        self.query_one(RealityGuardPanel).update_warnings(warnings)

if __name__ == "__main__":
    app = QuantumTUI()
    app.run()
