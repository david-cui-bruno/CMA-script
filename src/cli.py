"""
Command Line Interface for CMA Analysis
"""
import click
import asyncio
from src.core.cma_service import CMAService
import json

@click.group()
def cli():
    """CMA Analysis Tool CLI"""
    pass

@cli.command()
@click.option('--address', required=True, help='Property address to analyze')
@click.option('--radius', default=1.0, help='Search radius in miles')
@click.option('--output', help='Output file path (optional)')
def analyze(address: str, radius: float, output: str):
    """Perform CMA analysis for a property"""
    async def run_analysis():
        cma_service = CMAService()
        results = await cma_service.analyze_property(address)
        
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"Analysis saved to: {output}")
        else:
            click.echo(json.dumps(results, indent=2, default=str))
    
    asyncio.run(run_analysis())

if __name__ == '__main__':
    cli() 