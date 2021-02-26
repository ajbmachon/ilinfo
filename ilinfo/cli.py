# Created by Andre Machon 07/02/2021

import click

from ilinfo import Analyzer, JSONOutput

INI_MAPPING = {
    "ilias.ini.php": {
        "server": ['http_path', 'absolute_path'],
        "clients": ['path', 'inifile', 'datadir', 'default']
    },
    "client.ini.php": {
        "client": ['name', 'access'],
        "db": ['type', 'host', 'user', 'name', 'pass', 'port'],
        'language': ['default'],
        'layout': ['skin', 'style']
    },
}

EXCLUDED_FOLDERS = [
    'Backup', 'backup', '_Examples', 'Dump', 'dump', 'iliasold', 'ilias5_old', 'ilias4_old', 'defekt',
    'ilias5old', 'ilias4old', 'iliasOld', 'iliasold', 'ilias4svn', 'ilias5svn',
    '/opt', '/root', '/etc', '/media', '/mnt', '/lib', '/sbin', '/tmp'
]


@click.group()
@click.option('--debug', default=False) # TODO implement
@click.option('-l', '--log-level') # TODO implement, set params here: default=LOG_LEVEL_INFO, show_default=True
@click.pass_context
def main(ctx, debug, log_level):
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['log_level'] = log_level
    click.secho(f"ILIAS Info CLI", fg='green') # TODO output version dynamically from __about__.py


@main.command()
@click.argument('start-path', type=str, default='/')
# @click.option('-c', '--parse-config') TODO implement this, read config from file
@click.option('-o', '--output-path', type=str)
@click.pass_obj
def analyze(obj, start_path, output_path):
    # TODO analyze obj to set log level etc.
    if output_path:
        processor = JSONOutput(output_path=output_path)
        analyzer = Analyzer(output_processor=processor, excluded_folders=EXCLUDED_FOLDERS)
    else:
        analyzer = Analyzer(excluded_folders=EXCLUDED_FOLDERS)

    json_path = analyzer.analyze_path(start_path)
    click.secho(f"JSON result file was created at: {json_path}", fg='green')


if __name__ == '__main__':
    main()
