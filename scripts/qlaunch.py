#!/usr/bin/env python3
import asyncio
import click
from pathlib import Path
from q0rtex.core.launcher import QTermLauncher
from q0rtex.config import load_config

@click.command()
@click.option('--config', type=click.Path(), default='~/.q0rtex/config.yaml', help='Configuration file path')
@click.option('--warp-mode', is_flag=True, help='Run in Warp terminal compatibility mode')
@click.option('--metal-accel', is_flag=True, default=True, help='Enable Metal acceleration')
async def launch(config, warp_mode, metal_accel):
    """Launch qTerm with specified configuration and mode."""
    config_path = Path(config).expanduser()
    launcher = QTermLauncher(
        config=load_config(config_path),
        warp_mode=warp_mode,
        metal_acceleration=metal_accel
    )
    
    # Initialize quantum state
    await launcher.init_quantum_state()
    
    # Start continue plugin if available
    if launcher.config.get('continue_enabled', True):
        await launcher.init_continue_plugin()
    
    # Launch terminal
    await launcher.launch()
    
if __name__ == '__main__':
    asyncio.run(launch())

