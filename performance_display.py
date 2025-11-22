"""
Beautiful performance display using Rich library.
Shows real-time performance metrics in a styled console output.
"""
from typing import Dict, Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box
from datetime import datetime

console = Console()


class PerformanceDisplay:
    """Displays bot performance in a beautiful styled format."""
    
    def __init__(self):
        """Initialize the display."""
        self.console = Console()
    
    def create_performance_table(self, stats: Dict, resolution_metrics: Optional[Dict] = None) -> Table:
        """Create a styled performance table."""
        table = Table(title="📊 Performance Summary", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green", justify="right")
        
        # Basic stats
        table.add_row("Total Trades", f"{stats.get('total_trades', 0)}")
        table.add_row("Total Invested", f"${stats.get('total_invested', 0.0):.2f}")
        
        # Balance info
        starting_bal = stats.get('starting_balance')
        current_bal = stats.get('current_balance')
        if starting_bal is not None:
            table.add_row("Starting Balance", f"${starting_bal:.2f}")
        if current_bal is not None:
            table.add_row("Current Balance", f"${current_bal:.2f}")
        
        # P&L
        total_pnl = stats.get('total_pnl', 0.0)
        pnl_style = "green" if total_pnl >= 0 else "red"
        pnl_symbol = "📈" if total_pnl >= 0 else "📉"
        table.add_row("Total P&L", f"{pnl_symbol} ${total_pnl:.2f}", style=pnl_style)
        
        # ROI
        roi = stats.get('roi', 0.0)
        roi_style = "green" if roi >= 0 else "red"
        roi_symbol = "✅" if roi >= 0 else "❌"
        table.add_row("ROI", f"{roi_symbol} {roi:.2f}%", style=roi_style)
        
        # Resolution metrics if available
        if resolution_metrics and resolution_metrics.get('total_resolved', 0) > 0:
            table.add_row("", "")  # Separator
            table.add_row("Resolved Markets", f"{resolution_metrics['total_resolved']}")
            table.add_row("Wins", f"✅ {resolution_metrics['wins']}", style="green")
            table.add_row("Losses", f"❌ {resolution_metrics['losses']}", style="red")
            win_rate = resolution_metrics.get('win_rate', 0.0)
            win_rate_style = "green" if win_rate >= 50 else "yellow"
            table.add_row("Win Rate", f"{win_rate:.1f}%", style=win_rate_style)
        
        return table
    
    def create_portfolio_table(self, portfolio_summary: Dict) -> Table:
        """Create a portfolio positions table."""
        table = Table(title="💼 Open Positions", box=box.ROUNDED, show_header=True, header_style="bold blue")
        
        table.add_column("Market ID", style="cyan", no_wrap=True)
        table.add_column("Side", style="yellow")
        table.add_column("Amount", style="green", justify="right")
        table.add_column("Entry Prob", style="magenta", justify="right")
        
        positions = portfolio_summary.get('positions', {})
        if not positions:
            table.add_row("No open positions", "", "", "")
        else:
            for market_id, position in positions.items():
                side = position.get('side', 'N/A')
                amount = position.get('amount', 0.0)
                prob = position.get('market_prob', 0.0)
                side_display = f"✅ YES" if side == "YES" else f"❌ NO"
                table.add_row(
                    market_id[:12] + "...",
                    side_display,
                    f"${amount:.2f}",
                    f"{prob:.1%}"
                )
        
        return table
    
    def create_status_panel(self, bot_info: Dict) -> Panel:
        """Create a status panel."""
        status_text = Text()
        status_text.append("🤖 Bot Status\n\n", style="bold")
        status_text.append(f"Target Creator: ", style="cyan")
        status_text.append(f"{bot_info.get('target_creator', 'N/A')}\n", style="green")
        status_text.append(f"Bot Username: ", style="cyan")
        status_text.append(f"{bot_info.get('username', 'N/A')}\n", style="green")
        status_text.append(f"Status: ", style="cyan")
        status_text.append(f"{bot_info.get('status', 'Running')}\n", style="green")
        status_text.append(f"Last Update: ", style="cyan")
        status_text.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="yellow")
        
        return Panel(status_text, title="Status", border_style="blue")
    
    def display_performance(self, stats: Dict, resolution_metrics: Optional[Dict] = None,
                           portfolio_summary: Optional[Dict] = None, bot_info: Optional[Dict] = None,
                           clear_screen: bool = True):
        """Display comprehensive performance dashboard."""
        if clear_screen:
            # Clear screen for clean display
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
        
        self.console.print()
        
        # Header
        header = Panel(
            Text("🎯 Judgmental Prediction Bot - Performance Dashboard", style="bold white on blue", justify="center"),
            box=box.DOUBLE,
            border_style="blue"
        )
        self.console.print(header)
        
        # Main content in columns
        self.console.print()
        
        # Left side - Performance Table
        perf_table = self.create_performance_table(stats, resolution_metrics)
        self.console.print(perf_table)
        
        self.console.print()
        
        # Right side - Portfolio and Status
        if portfolio_summary and portfolio_summary.get('num_positions', 0) > 0:
            portfolio_table = self.create_portfolio_table(portfolio_summary)
            self.console.print(portfolio_table)
            self.console.print()
        
        if bot_info:
            status_panel = self.create_status_panel(bot_info)
            self.console.print(status_panel)
        
        # Footer
        self.console.print()
        footer = Panel(
            Text("Press Ctrl+C to stop | Performance updates in real-time", style="dim white", justify="center"),
            box=box.ROUNDED,
            border_style="yellow"
        )
        self.console.print(footer)
        self.console.print()
    
    def display_simple_summary(self, stats: Dict, resolution_metrics: Optional[Dict] = None):
        """Display a simple one-time summary."""
        self.console.print("\n")
        
        # Performance Panel
        perf_table = self.create_performance_table(stats, resolution_metrics)
        self.console.print(perf_table)
        
        # Resolution details if available
        if resolution_metrics and resolution_metrics.get('total_resolved', 0) > 0:
            self.console.print(f"\n[bold green]✅ Resolved:[/bold green] {resolution_metrics['total_resolved']} markets")
            self.console.print(f"[green]Wins:[/green] {resolution_metrics['wins']} | [red]Losses:[/red] {resolution_metrics['losses']} | [yellow]Win Rate:[/yellow] {resolution_metrics['win_rate']:.1f}%")
        
        self.console.print("\n")

