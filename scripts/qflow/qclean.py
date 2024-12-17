#!/usr/bin/env python3
"""
Quandex Core Workflow: Repository Cleaning Tool
Provides automated cleaning and organization of Quandex repositories.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Set, Dict
import logging
import argparse
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('qclean')

class QuandexCleaner:
    def __init__(self, repo_path: str, config_path: str = None):
        self.repo_path = Path(repo_path)
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load cleaning configuration."""
        default_config = {
            'ignore_patterns': [
                '.git',
                'node_modules',
                '__pycache__',
                '*.pyc',
                '.DS_Store',
                'venv*',
                'volumes',
                '*.egg-info',
            ],
            'clean_patterns': [
                'Miniconda*',
                'conda_init*.sh',
                'tmp_*',
                '*.tmp',
            ],
            'organize_dirs': {
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

    def check_git_status(self) -> bool:
        """Check if repository is clean."""
        result = self._run_git_command(['status', '--porcelain'])
        return not bool(result.stdout.strip())

    def find_files_to_clean(self) -> Set[Path]:
        """Find files matching clean patterns."""
        to_clean = set()
        for pattern in self.config['clean_patterns']:
            for path in self.repo_path.rglob(pattern):
                if not any(path.match(ignore) for ignore in self.config['ignore_patterns']):
                    to_clean.add(path)
        return to_clean

    def organize_files(self) -> Dict[str, List[Path]]:
        """Organize files into their proper directories."""
        moves = {}
        for target_dir, patterns in self.config['organize_dirs'].items():
            target_path = self.repo_path / target_dir
            target_path.mkdir(parents=True, exist_ok=True)
            
            for pattern in patterns:
                exclude = pattern.startswith('!')
                if exclude:
                    pattern = pattern[1:]
                
                for path in self.repo_path.rglob(pattern):
                    if exclude:
                        continue
                    if not any(path.match(ignore) for ignore in self.config['ignore_patterns']):
                        moves.setdefault(target_dir, []).append(path)
        
        return moves

    def clean(self, dry_run: bool = True) -> None:
        """Clean the repository."""
        logger.info("Starting Quandex repository cleaning...")
        
        # Check git status
        if not dry_run and not self.check_git_status():
            logger.warning("Repository has uncommitted changes!")
            if not input("Continue anyway? [y/N]: ").lower().startswith('y'):
                return
        
        # Find files to clean
        to_clean = self.find_files_to_clean()
        if to_clean:
            logger.info("Files to clean:")
            for path in sorted(to_clean):
                logger.info(f"  - {path}")
            
            if not dry_run:
                for path in to_clean:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path)
        
        # Organize files
        moves = self.organize_files()
        if moves:
            logger.info("Files to organize:")
            for target_dir, files in moves.items():
                logger.info(f"  {target_dir}:")
                for path in sorted(files):
                    logger.info(f"    - {path}")
            
            if not dry_run:
                for target_dir, files in moves.items():
                    target_path = self.repo_path / target_dir
                    for path in files:
                        new_path = target_path / path.name
                        if not new_path.exists():
                            shutil.move(str(path), str(new_path))
        
        if dry_run:
            logger.info("Dry run complete. Use --apply to make changes.")
        else:
            logger.info("Repository cleaning complete!")

def main():
    parser = argparse.ArgumentParser(description="Quandex Repository Cleaning Tool")
    parser.add_argument('--repo', default='.', help='Repository path')
    parser.add_argument('--config', help='Custom config file path')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    
    args = parser.parse_args()
    
    cleaner = QuandexCleaner(args.repo, args.config)
    cleaner.clean(dry_run=not args.apply)

if __name__ == '__main__':
    main()
