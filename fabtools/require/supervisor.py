"""
Supervisor processes
====================

This module provides high-level tools for managing long-running
processes using `supervisor`_.

.. _supervisor: http://supervisord.org/

"""
from __future__ import with_statement

from fabtools.files import watch
from fabtools.supervisor import update_config, process_status, start_process


def process(name, **kwargs):
    """
    Require a supervisor process to be running.

    Keyword arguments will be used to build the program configuration
    file. Some useful arguments are:

    - ``command``: complete command including arguments (**required**)
    - ``directory``: absolute path to the working directory
    - ``user``: run the process as this user
    - ``stdout_logfile``: absolute path to the log file

    You should refer to the `supervisor documentation`_ for the
    complete list of allowed arguments.

    .. note:: the default values for the following arguments differs from
              the ``supervisor`` defaults:

              - ``autorestart``: defaults to ``true``
              - ``redirect_stderr``: defaults to ``true``

    Example::

        from fabtools import require

        require.supervisor.process('myapp',
            command='/path/to/venv/bin/myapp --config production.ini --someflag',
            directory='/path/to/working/dir',
            user='alice',
            stdout_logfile='/path/to/logs/myapp.log',
            )

    .. _supervisor documentation: http://supervisord.org/configuration.html#program-x-section-values
    """
    from fabtools import require
    require.deb.package('supervisor')
    require.service.started('supervisor')

    # Set default parameters
    params = {}
    params.update(kwargs)
    params.setdefault('autorestart', 'true')
    params.setdefault('redirect_stderr', 'true')

    # Build config file from parameters
    lines = []
    lines.append('[program:%(name)s]' % locals())
    for key, value in sorted(params.items()):
        lines.append("%s=%s" % (key, value))

    # Upload config file
    filename = '/etc/supervisor/conf.d/%(name)s.conf' % locals()
    with watch(filename, callback=update_config, use_sudo=True):
        require.file(filename, contents='\n'.join(lines), use_sudo=True)

    # Start the process if needed
    if process_status(name) == 'STOPPED':
        start_process(name)
