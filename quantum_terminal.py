from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Log, Static, Input, Button, Label, DataTable
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from textual.reactive import reactive
from services.cortex.quantum_scaffold import QuantumScaffold
from services.cortex.resource_manager import ResourceManager, ResourcePriority
from services.cortex.process_analyzer import ProcessAnalyzer, ProcessMetrics
import psutil
import os
import time
import logging
import asyncio
from datetime import datetime

class SystemMetrics(Static):
    def __init__(self):
        super().__init__()
        self.update_task = None

    def on_mount(self):
        self.update_task = asyncio.create_task(self._update_metrics())

    async def _update_metrics(self):
        while True:
            metrics = {
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage("/").percent
            }
            self.update(
                f"[bold]System Metrics[/]\n"
                f"CPU: {metrics['cpu']:.1f}%\n"
                f"Memory: {metrics['memory']:.1f}%\n"
                f"Disk: {metrics['disk']:.1f}%"
            )
            await asyncio.sleep(1)

class ResourceMonitor(Static):
    def __init__(self, resource_manager: ResourceManager = None, **kwargs):
        super().__init__(**kwargs)
        self.resource_manager = resource_manager
        self.update_task = None
    
    async def on_mount(self) -> None:
        """Start the update task when mounted."""
        self.update_task = asyncio.create_task(self._update_display())
    
    async def on_unmount(self) -> None:
        """Cancel the update task when unmounted."""
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
    
    async def _update_display(self) -> None:
        """Update the display periodically."""
        while True:
            try:
                if self.resource_manager:
                    metrics = await self.resource_manager.get_resource_metrics()
                    
                    # Format display text
                    text = f"[b]System Resources[/b]\n"
                    text += f"CPU: {metrics.get('cpu_percent', 0):.1f}%\n"
                    text += f"Memory: {metrics.get('memory_percent', 0):.1f}%\n"
                    text += f"Used: {metrics.get('memory_used', 0) / (1024**3):.2f} GB\n"
                    text += f"Total: {metrics.get('memory_total', 0) / (1024**3):.2f} GB"
                    
                    self.update(text)
                
                await asyncio.sleep(2)  # Update every 2 seconds
            except Exception as e:
                logging.error(f"Error updating resource display: {e}")
                await asyncio.sleep(5)  # Wait before retrying

class ServiceStatus(Static):
    def __init__(self):
        super().__init__()
        self.update_task = None

    def on_mount(self):
        self.update_task = asyncio.create_task(self._update_status())

    async def _update_status(self):
        while True:
            services = {
                "Quantum Engine": "Running",
                "M3 Neural Engine": "Active",
                "Resource Manager": "Monitoring"
            }
            self.update(
                f"[bold]Service Status[/]\n" +
                "\n".join(f"{name}: {status}" for name, status in services.items())
            )
            await asyncio.sleep(5)

class ProcessViewer(Static):
    """Interactive process viewer with real-time insights."""
    
    def __init__(self):
        super().__init__()
        self.selected_pid = None
        self.process_table = DataTable()
        self.process_details = Static()
        self.update_task = None
        
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield DataTable(id="process-table")
        yield Static(id="process-info")
        
    async def on_mount(self) -> None:
        """Set up the process table."""
        table = self.query_one("#process-table")
        table.add_columns(
            "PID", "Name", "CPU %", "Memory %", "Threads",
            "Anomaly", "Context", "Cluster"
        )
        
        # Start update task
        self.update_task = asyncio.create_task(self._update_display())
        
    async def _update_display(self) -> None:
        """Update the process display periodically."""
        while True:
            try:
                # Get process graph and clusters
                process_graph = self.app.process_web.interaction_graph
                clusters = {
                    p: i for i, c in enumerate(self.app.process_web.clusters)
                    for p in c.processes
                }
                
                # Update table
                table = self.query_one("#process-table")
                table.clear()
                
                for pid, data in process_graph.nodes(data=True):
                    if isinstance(pid, int):  # Skip network nodes
                        table.add_row(
                            str(pid),
                            data['name'],
                            f"{data['cpu_percent']:.1f}",
                            f"{data['memory_percent']:.1f}",
                            str(data['num_threads']),
                            self._format_score(data['anomaly_score']),
                            self._format_score(data['context_score']),
                            f"C{clusters.get(pid, '-')}"
                        )
                
                # Update details if process is selected
                if self.selected_pid:
                    await self._update_process_details()
                
                await asyncio.sleep(1)
            except Exception as e:
                self.app.log.error(f"Error updating process display: {e}")
                await asyncio.sleep(5)
    
    def _format_score(self, score: float) -> str:
        """Format a score with color based on value."""
        if score > 0.8:
            return f"[red]{score:.2f}[/]"
        elif score > 0.5:
            return f"[yellow]{score:.2f}[/]"
        return f"[green]{score:.2f}[/]"
    
    async def _update_process_details(self) -> None:
        """Update the process details panel."""
        info_panel = self.query_one("#process-info")
        
        # Get process and cluster insights
        process_insights = self.app.process_analyzer.get_process_insights(self.selected_pid)
        cluster_insights = self.app.process_web.get_cluster_insights(self.selected_pid)
        
        if not process_insights:
            info_panel.update("Process not found")
            return
            
        # Format process information
        process = process_insights["process"]
        details = [
            "[bold]Process Details[/]",
            f"Name: {process['name']}",
            f"PID: {process['pid']}",
            f"Status: {process['status']}",
            f"CPU: {process['cpu_percent']:.1f}% (trend: {process_insights['cpu_trend']:.1f}%)",
            f"Memory: {process['memory_percent']:.1f}% (trend: {process_insights['mem_trend']:.1f}%)",
            f"Threads: {process['num_threads']}",
            f"Anomaly Score: {self._format_score(process['anomaly_score'])}",
            f"Context Score: {self._format_score(process['context_score'])}",
            "",
            "[bold]Related Processes[/]"
        ]
        
        # Add related process information
        for related in process_insights["related_processes"][:5]:  # Show top 5
            details.append(
                f"• {related['pid']} ({related['relationship']})"
            )
            
        # Add cluster information if available
        if cluster_insights:
            cluster = cluster_insights["cluster"]
            details.extend([
                "",
                "[bold]Cluster Information[/]",
                f"Cluster Size: {len(cluster.processes)} processes",
                f"Center Process: {cluster.center_pid}",
                f"Similarity Score: {self._format_score(cluster.similarity_score)}",
                f"Resource Impact: {self._format_score(cluster.resource_impact)}",
                f"Interaction Score: {self._format_score(cluster.interaction_score)}"
            ])
        
        info_panel.update("\n".join(details))
    
    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the process table."""
        self.selected_pid = int(event.row_key.value)
        await self._update_process_details()
        
    async def on_unmount(self) -> None:
        """Clean up the update task."""
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass

class CommandInput(Input):
    def __init__(self):
        super().__init__(placeholder="Enter command...")

    async def on_submit(self, value: str):
        if value.strip():
            try:
                # Get the log widget and write the command
                log = self.app.query_one(Log)
                log.write(f"> {value}")
                
                # Process the command through quantum scaffold
                response = await self.app.scaffold.process_user_state({
                    "command": value,
                    "timestamp": time.time()
                })
                log.write(f"Response: {response}")
            except Exception as e:
                log.write(f"[red]Error: {str(e)}[/]")
            finally:
                self.value = ""

class QuantumTerminal(App):
    CSS = """
    #app-grid {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
        height: 100%;
    }
    
    #sidebar {
        width: 100%;
        height: 100%;
        background: $panel;
        border-right: solid $primary;
    }
    
    #main {
        width: 100%;
        height: 100%;
    }
    
    #process-table {
        height: 60%;
        border: solid $primary;
    }
    
    #process-details {
        height: 40%;
        border-top: solid $primary;
        padding: 1;
    }
    
    #process-info {
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource_manager = None
        self.scaffold = None
    
    async def on_mount(self) -> None:
        """Initialize after terminal is mounted."""
        # Initialize resource manager
        self.resource_manager = await ResourceManager().start()
        self.scaffold = QuantumScaffold()
        
        # Register terminal process
        await self.resource_manager.register_process(
            os.getpid(),
            "quantum_terminal",
            ResourcePriority.HIGH
        )
        
        # Initialize components that need resource manager
        resource_monitor = self.query_one("#resource-monitor")
        resource_monitor.resource_manager = self.resource_manager
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with Container(id="app-grid"):
            # Sidebar with system metrics and status
            with Container(id="sidebar"):
                yield SystemMetrics()
                yield ResourceMonitor(resource_manager=self.resource_manager, id="resource-monitor")
                yield ServiceStatus()
            
            # Main area with process viewer
            with Container(id="main"):
                yield ProcessViewer()
                
        yield Footer()
    
    async def on_unmount(self) -> None:
        if self.resource_manager:
            await self.resource_manager.unregister_process(os.getpid())
    
    def action_refresh(self) -> None:
        """Refresh all metrics and status displays"""
        try:
            # Update system metrics
            metrics = self.query_one(SystemMetrics)
            if metrics and metrics.update_task:
                metrics.update_task.cancel()
            new_metrics = SystemMetrics()
            new_metrics.add_class("metrics")
            metrics.remove()
            self.query_one("#sidebar").mount(new_metrics)
            
            # Update service status
            status = self.query_one(ServiceStatus)
            if status and status.update_task:
                status.update_task.cancel()
            new_status = ServiceStatus()
            new_status.add_class("status")
            status.remove()
            self.query_one("#sidebar").mount(new_status)
            
        except Exception as e:
            log = self.query_one(Log)
            log.write(f"[red]Error refreshing: {str(e)}[/]")

if __name__ == "__main__":
    app = QuantumTerminal()
    app.run()
