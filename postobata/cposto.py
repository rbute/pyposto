import click

from pyposto.main import step


@step.command('setup2')
@click.pass_obj
def setup(obj):
    click.secho(f'Inside setup 2. obj: {obj}', color='red')
