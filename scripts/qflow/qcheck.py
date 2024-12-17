#!/usr/bin/env python3
"""
Quandex Core Workflow: Repository Health Check Tool
Analyzes and reports on repository health and organization.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import logging
import argparse
import yaml
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.progress import track

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('qcheck')
console = Console()

@dataclass
class RepoMetrics:
    total_files: int
    total_size: int
    file_types: Dict[str, int]
    large_files: List[Tuple[Path, int]]
    empty_dirs: List[Path]
    unorganized_files: List[Path]

class QuandexChecker:
    def __init__(self, repo_path: str, config_path: str = None):
        self.repo_path = Path(repo_path)
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load check configuration."""
        default_config = {
            'ignore_patterns': [
                '.git',
                'node_modules',
                '__pycache__',
                '*.pyc',
                '.DS_Store',
            ],
            'size_limits': {
                'file_max_mb': 100,
                'repo_max_gb': 1,
            },
            'organization': {
                'services/cortex/models': ['*.model', '*.gguf'],
                'services/cortex/metal': ['*metal*.py', '*gpu*.py'],
                'services/cortex/api': ['*api*.py', '*server*.py'],
                'docs': ['*.md', '!README.md', '!CONTRIBUTING.md'],
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
                
        return default_config
    
    def _run_git_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run a git command safely."""
        try:
            return subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e.stderr}")
            raise

    def check_git_status(self) -> Dict[str, int]:
        """Check git status and return counts of changes."""
        result = self._run_git_command(['status', '--porcelain'])
        changes = {
            'modified': 0,
            'added': 0,
            'deleted': 0,
            'untracked': 0
        }
        
        for line in result.stdout.splitlines():
            status = line[:2]
            if 'M' in status:
                changes['modified'] += 1
            elif 'A' in status:
                changes['added'] += 1
            elif 'D' in status:
                changes['deleted'] += 1
            elif '??' in status:
                changes['untracked'] += 1
                
        return changes

    def collect_metrics(self) -> RepoMetrics:
        """Collect repository metrics."""
        metrics = RepoMetrics(
            total_files=0,
            total_size=0,
            file_types={},
            large_files=[],
            empty_dirs=[],
            unorganized_files=[]
        )
        
        max_file_size = self.config['size_limits']['file_max_mb'] * 1024 * 1024
        
        for root, dirs, files in os.walk(self.repo_path):
            root_path = Path(root)
            
            # Check for ignored paths
            dirs[:] = [d for d in dirs if not any(
                root_path.joinpath(d).match(pattern)
                for pattern in self.config['ignore_patterns']
            )]
            
            # Check empty directories
            if not dirs and not files:
                metrics.empty_dirs.append(root_path)
            
            for file in files:
                if any(root_path.joinpath(file).match(pattern)
                      for pattern in self.config['ignore_patterns']):
                    continue
                    
                file_path = root_path / file
                metrics.total_files += 1
                
                # Collect file size
                size = file_path.stat().st_size
                metrics.total_size += size
                
                # Check file type
                ext = file_path.suffix or 'no_extension'
                metrics.file_types[ext] = metrics.file_types.get(ext, 0) + 1
                
                # Check large files
                if size > max_file_size:
                    metrics.large_files.append((file_path, size))
                
                # Check organization
                if not self._is_file_organized(file_path):
                    metrics.unorganized_files.append(file_path)
        
        return metrics

    def _is_file_organized(self, file_path: Path) -> bool:
        """Check if file is in the correct directory."""
        relative_path = file_path.relative_to(self.repo_path)
        
        for target_dir, patterns in self.config['organization'].items():
            target_path = self.repo_path / target_dir
            if file_path.is_relative_to(target_path):
                return any(
                    not pattern.startswith('!') and file_path.match(pattern[1:])
                    or pattern.startswith('!') and not file_path.match(pattern[1:])
                    for pattern in patterns
                )
        
        return True

    def display_report(self, metrics: RepoMetrics) -> None:
        """Display repository health report."""
        console.print("\n[bold blue]Quandex Repository Health Report[/bold blue]\n")
        
        # Git Status
        git_status = self.check_git_status()
        status_table = Table(title="Git Status")
        status_table.add_column("Type", style="cyan")
        status_table.add_column("Count", style="green")
        for status, count in git_status.items():
            status_table.add_row(status.capitalize(), str(count))
        console.print(status_table)
        
        # Repository Stats
        stats_table = Table(title="\nRepository Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        stats_table.add_row("Total Files", str(metrics.total_files))
        stats_table.add_row("Total Size", f"{metrics.total_size / (1024*1024):.2f} MB")
        console.print(stats_table)
        
        # File Types
        types_table = Table(title="\nFile Types")
        types_table.add_column("Extension", style="cyan")
        types_table.add_column("Count", style="green")
        for ext, count in sorted(metrics.file_types.items(), key=lambda x: x[1], reverse=True):
            types_table.add_row(ext, str(count))
        console.print(types_table)
        
        # Issues
        if any([metrics.large_files, metrics.empty_dirs, metrics.unorganized_files]):
            console.print("\n[bold red]Issues Found:[/bold red]")
            
            if metrics.large_files:
                console.print("\n[yellow]Large Files:[/yellow]")
                for path, size in metrics.large_files:
                    console.print(f"  - {path} ({size / (1024*1024):.2f} MB)")
            
            if metrics.empty_dirs:
                console.print("\n[yellow]Empty Directories:[/yellow]")
                for path in metrics.empty_dirs:
                    console.print(f"  - {path}")
            
            if metrics.unorganized_files:
                console.print("\n[yellow]Unorganized Files:[/yellow]")
                for path in metrics.unorganized_files:
                    console.print(f"  - {path}")
        else:
            console.print("\n[bold green]No issues found! Repository is well-organized.[/bold green]")

def main():
    parser = argparse.ArgumentParser(description="Quandex Repository Health Check Tool")
    parser.add_argument('--repo', default='.', help='Repository path')
    parser.add_argument('--config', help='Custom config file path')
    
    args = parser.parse_args()
    
    checker = QuandexChecker(args.repo, args.config)
    with console.status("[bold blue]Analyzing repository..."):
        metrics = checker.collect_metrics()
    checker.display_report(metrics)

if __name__ == '__main__':
    main()
