import sys

import click

from league_vcs import core


@click.group()
def main():
    """A version control system for League of Legends.

    Long gone are the days of manually copying your game files before every patch, only to forget where you kept them.
    This is the solution to all your first-world problems.

    In addition to being a quick and easy way to keep old versions of League of Legends, it only stores the changes
    between patches, taking less space on your computer."""


@main.command(name='clean')
def clean_command():
    """Clean the current patch directory."""
    core.repo.clean()
    print('Cleaned!')


@main.command(name='list')
def list_command():
    """List all the currently-stored LoL versions."""
    tags = core.repo.list()
    if tags:
        print('Available patches:')
    else:
        print('No patches found!')
    current_patch = core.repo.current()
    for tag in sorted(tags, reverse=True):
        print(' -', tag, '(current)' if current_patch == tag else '')


@main.command(name='drop')
@click.argument('patch')
def drop_command(patch):
    """Remove a patch from the repository and free up space."""
    if patch not in core.repo.list():
        return print(f'Patch {patch} does not exist!', file=sys.stderr)

    if not click.confirm(f'Are you sure you want to drop patch {patch}? THIS CANNOT BE UNDONE.'):
        return

    core.repo.drop(patch)


@main.command(name='add')
@click.argument('directory', type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True))
def add_command(directory):
    """Add a game version to the repository, if it doesn't exist."""
    core.add(directory)


@main.command(name='restore')
@click.argument('patch')
def restore_command(patch):
    """Manually restore a specific patch."""
    try:
        core.repo.restore(patch)
    except AssertionError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


@main.command(name='current')
def current_command():
    """Show the current client version."""
    patch = core.repo.current()
    print(f'Currently on patch {patch}' if patch else 'None')


@main.command(name='watch')
@click.argument('replay', type=click.Path(exists=True, readable=True, resolve_path=True))
def watch_command(replay):
    """Load the required game version and launch the replay."""
    core.watch(replay)


@main.command(name='path')
def path_command():
    """The path to the restored game folder."""
    print(core.repo.current_path() if core.repo.current() else 'No current patch!')


@main.command(name='wipe')
def wipe_command():
    """The nuclear button. Removes all patches."""
    if click.confirm('Are you sure you want to remove all patches? THIS CANNOT BE UNDONE.'):
        core.repo.wipe()


if __name__ == '__main__':
    main()
