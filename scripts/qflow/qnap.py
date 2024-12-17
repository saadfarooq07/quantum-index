#!/usr/bin/env python3
"""
Quandex Core Workflow: Repository Snapshot Tool
Creates and manages repository snapshots for easy restoration.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict
import logging
import argparse
import yaml
from datetime import datetime
import json
from rich.console import Console
from rich.progress import track

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('qnap')
console = Console()

class QuandexSnapshot:
    def __init__(self, repo_path: str, config_path: str = None):
        self.repo_path = Path(repo_path)
        self.config = self._load_config(config_path)
        self.snapshots_dir = self.repo_path / '.quandex' / 'snapshots'
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load snapshot configuration."""
        default_config = {
            'ignore_patterns': [
                '.git',
                'node_modules',
                '__pycache__',
                '*.pyc',
                '.DS_Store',
                'venv*',
                'volumes',
            ],
            'max_snapshots': 5,
            'snapshot_name_format': '%Y%m%d_%H%M%S'
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

    def _get_git_status(self) -> Dict:
        """Get git repository status."""
        status = {
            'branch': '',
            'commit': '',
            'changes': []
        }
        
        # Get current branch
        result = self._run_git_command(['branch', '--show-current'])
        status['branch'] = result.stdout.strip()
        
        # Get current commit
        result = self._run_git_command(['rev-parse', 'HEAD'])
        status['commit'] = result.stdout.strip()
        
        # Get changes
        result = self._run_git_command(['status', '--porcelain'])
        status['changes'] = [line.strip() for line in result.stdout.splitlines()]
        
        return status

    def create_snapshot(self, name: str = None) -> str:
        """Create a new repository snapshot."""
        if not name:
            name = datetime.now().strftime(self.config['snapshot_name_format'])
        
        snapshot_path = self.snapshots_dir / name
        if snapshot_path.exists():
            raise ValueError(f"Snapshot '{name}' already exists")
        
        # Create snapshot directory
        snapshot_path.mkdir(parents=True)
        
        # Copy repository files
        console.print(f"\n[bold blue]Creating snapshot '{name}'...[/bold blue]")
        for item in track(list(self.repo_path.iterdir()), description="Copying files"):
            if item.name == '.quandex' or any(
                item.match(pattern) for pattern in self.config['ignore_patterns']
            ):
                continue
            
            if item.is_file():
                shutil.copy2(item, snapshot_path)
            else:
                shutil.copytree(item, snapshot_path / item.name)
        
        # Save metadata
        metadata = {
            'created_at': datetime.now().isoformat(),
            'git': self._get_git_status(),
        }
        
        with open(snapshot_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Clean old snapshots
        self._clean_old_snapshots()
        
        console.print(f"[bold green]Snapshot '{name}' created successfully![/bold green]")
        return name

    def restore_snapshot(self, name: str) -> None:
        """Restore repository from a snapshot."""
        snapshot_path = self.snapshots_dir / name
        if not snapshot_path.exists():
            raise ValueError(f"Snapshot '{name}' not found")
        
        # Check git status
        git_status = self._get_git_status()
        if git_status['changes']:
            if not console.input(
                "[bold yellow]Repository has uncommitted changes. Continue? [y/N]: [/bold yellow]"
            ).lower().startswith('y'):
                return
        
        # Restore files
        console.print(f"\n[bold blue]Restoring snapshot '{name}'...[/bold blue]")
        
        # Remove current files (except ignored ones)
        for item in track(list(self.repo_path.iterdir()), description="Cleaning current files"):
            if item.name == '.quandex' or any(
                item.match(pattern) for pattern in self.config['ignore_patterns']
            ):
                continue
            
            if item.is_file():
                item.unlink()
            else:
                shutil.rmtree(item)
        
        # Copy snapshot files
        for item in track(list(snapshot_path.iterdir()), description="Restoring files"):
            if item.name == 'metadata.json':
                continue
            
            target = self.repo_path / item.name
            if item.is_file():
                shutil.copy2(item, target)
            else:
                shutil.copytree(item, target)
        
        console.print(f"[bold green]Snapshot '{name}' restored successfully![/bold green]")

    def list_snapshots(self) -> None:
        """List all available snapshots."""
        snapshots = []
        for path in self.snapshots_dir.iterdir():
            if path.is_dir():
                metadata_file = path / 'metadata.json'
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    snapshots.append({
                        'name': path.name,
                        'created_at': metadata['created_at'],
                        'git_branch': metadata['git']['branch'],
                        'git_commit': metadata['git']['commit'][:8]
                    })
        
        if not snapshots:
            console.print("[yellow]No snapshots found[/yellow]")
            return
        
        from rich.table import Table
        table = Table(title="Repository Snapshots")
        table.add_column("Name", style="cyan")
        table.add_column("Created At", style="green")
        table.add_column("Git Branch", style="blue")
        table.add_column("Git Commit", style="magenta")
        
        for snapshot in sorted(snapshots, key=lambda x: x['created_at'], reverse=True):
            table.add_row(
                snapshot['name'],
                snapshot['created_at'],
                snapshot['git_branch'],
                snapshot['git_commit']
            )
        
        console.print(table)

    def _clean_old_snapshots(self) -> None:
        """Clean old snapshots if exceeding max limit."""
        snapshots = sorted(
            [p for p in self.snapshots_dir.iterdir() if p.is_dir()],
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        while len(snapshots) > self.config['max_snapshots']:
            shutil.rmtree(snapshots.pop())

def main():
    parser = argparse.ArgumentParser(description="Quandex Repository Snapshot Tool")
    parser.add_argument('--repo', default='.', help='Repository path')
    parser.add_argument('--config', help='Custom config file path')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Create snapshot
    create_parser = subparsers.add_parser('create', help='Create a new snapshot')
    create_parser.add_argument('--name', help='Snapshot name (default: timestamp)')
    
    # Restore snapshot
    restore_parser = subparsers.add_parser('restore', help='Restore from a snapshot')
    restore_parser.add_argument('name', help='Snapshot name to restore')
    
    # List snapshots
    subparsers.add_parser('list', help='List all snapshots')
    
    args = parser.parse_args()
    
    snapper = QuandexSnapshot(args.repo, args.config)
    
    if args.command == 'create':
        snapper.create_snapshot(args.name)
    elif args.command == 'restore':
        snapper.restore_snapshot(args.name)
    elif args.command == 'list':
        snapper.list_snapshots()

if __name__ == '__main__':
    main()
