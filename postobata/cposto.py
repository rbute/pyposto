import click

from pyposto.main import step


@step.command('setup2')
@click.pass_context
def setup(ctx):
# def setup():
    # ctx.ensure_object(dict)
    click.secho('Inside setup 2', color='red')
