from fabric.api import task, env, settings
import re

# import the preconfigured tasks that ship with cotton. Loading fabfile submodules
# here will expose their tasks to the fab command-line.
from cotton.fabfile import set_env, system, project, postfix, util

# load your custom settings from this module
set_env('cotton_settings')


# Add fabric tasks unique to your application deployment here.  The ship() task is an example of a
# minimal deployment. If you do nothing else, you need to push your your code to the remote host(s),
# and update the virtual environments with any changes in your python dependencies list.
#
# If you import env from fabric.api, you can access the entirety of the fabric shared environment,
# including all of the configuration loaded at runtime from both the cotton defaults and your local
# cotton_settings.py file.
#
# Remember that if you are using cotton to configure your base system as well as manage your
# application deployments, you'll want to run the system.bootstrap() task before deploying
# your application for the first time:
#
# fab system.bootstrap
#
# Note that if you choose not to use cotton's system module to manage your server configs,
# you'll need to make sure the packages listed in requirements/apt.txt are present.
#

@task
def fixup():
    """
    Fix up initial problems for slack challenge part 2
    """

    close_tmp_filehandles()
    clear_iptables()
    terminate('nc,named')

    # we must upload these templates before executing other tasks, as without
    # proper name resolution many things (eg. apt) wil. fail.
    util.upload_template_and_reload('resolv_conf')
    util.upload_template_and_reload('etc_hosts')


@task
def init():
    """
    Bootstrap the base system
    """

    if env.user != 'root':
        raise Exception("Please execute the init task as root, thus: fab -u root init")

    # WAT for some reason system.bootstrap() trashes the debconf selections made by the
    # postfix.install() task. Until this bug is resolved, we must install postfix first. *mutter*
    postfix.install()
    system.bootstrap()
    project.install()


@task
def ship():
    """
    Deploy the current branch to production
    """
    # system.unbanips()
    project.git_push()
    project.install_dependencies()
    system.ensure_running()


@task
def close_tmp_filehandles():
    """
    Attempt to close any open filehandles for deleted files in the /tmp/ directory
    """
    if env.user != 'root':
        raise Exception("Please execute the truncate_tmp_filehandles task as root.")

    # get the list of filehandles still open for unlinked entries
    res = system.run("lsof +L1 |tail -n +2")

    # COMMAND  PID USER   FD   TYPE DEVICE   SIZE/OFF NLINK  NODE NAME
    # named   3290 root    2u   CHR  136,0        0t0     0     3 /dev/pts/0 (deleted)
    # named   3290 root    3w   REG  202,1 9610481664     0 53245 /tmp/tmp.cbiX32y92o (deleted)

    for l in res.split("\n"):
        (cmd, pid, user, fd, typ, dev, size, numlink, node, name, foo) = l.split()

        # we only care about filehandles in /tmp/, for now
        if name[0:5] != '/tmp/':
            continue
        print "Attempting to terminate %s (PID %s)" % (cmd, pid)
        if not (killproc(pid, cmd, signal=15) or killproc(pid, cmd, signal=9)):
            raise Exception("Could not kill %s (PID %s)!" % (cmd, pid))


@task
def clear_iptables():
    """
    Remove bogus DROP rules from the firewall's INPUT chain
    """

    # WAT: This task wouldn't be necessary if cotton's firewall task reset the firewall before
    # applying its own rules. Ho hum.

    # 1    DROP       tcp  --  anywhere             anywhere             tcp dpt:http
    res = system.sudo("iptables -L INPUT --line-numbers |tail -n +3")
    for l in res.split("\n"):
        try:
            (num, action, proto, opt, src, dest, foo, rule) = l.split()
        except ValueError:
            continue
        if action != 'DROP':
            continue
        system.sudo("iptables -D INPUT %s" % num)


@task
def terminate(procs):
    """
    Attempt to stop the specified procs
    """

    # hacky regex to match `ps aux` output. Sufficient for our purposes here,
    # but definitely not the way to do things For Reals(tm)
    ps_re = re.compile(
        '(\S+)\s+(\d+)\s+([\d\.]+)'  # USER, PID, CPU
        '\s+([\d\.]+)\s+(\S+)\s+(\S+)'  # MEM, VSZ, RSS
        '\s+(\S+)\s+(\S+)\s+(\S+)'  # TTY, STAT, START
        '\s+(\S+)\s+(\S+)(.*)',  # TIME, CMD, ARGS
    )

    for p in procs.split(','):

        # USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
        # root      3286  0.0  0.0  14396   508 ?        S    01:12   0:00 nc -k -l 0.0.0.0 80

        # NB: process names must match exactly in the process table, so if ps reports the full path
        # to the executable, so must the procs parameter.
        res = system.sudo("ps aux |grep \"%s\"" % p)
        for l in res.split("\n"):
            m = ps_re.match(l)
            (pid, cmd) = (m.group(2), m.group(11))
            try:
                if cmd != p:
                    continue
            except:
                continue

            # Send a TERM first, to be polite. If it won't go away, KILL it.
            # WAT: This makes me uncomfortable. We are also being kind of cavalier about
            # child processes; by iterating over the ps output from top to bottom, we should
            # always hit the parent process first, but we're just sort of jazz-handsing it.
            print "Attempting to terminate %s (PID %s)" % (cmd, pid)
            if not (killproc(pid, cmd, signal=15) or killproc(pid, cmd, signal=9)):
                raise Exception("Could not kill %s (PID %s)!" % (cmd, pid))


def killproc(pid, cmd, signal=15):
    """
    Terminate the specified PID and verify the command goes away
    """

    # send a TERM to the process holding the filehandle open; a well-behaved proc will
    # close the filehandle on exit. We then wait three seconds to give it a chance to comply.
    system.sudo("kill -%s %s; sleep 3" % (signal, pid))

    # If the proc is still running and still has the same pid, it ignored us. bad proc!
    # If ps exits with non-zero status, the pid is no longer assigned. Good proc!
    # If ps exists with zero status, but the pid is assigned to a different proc, we're still ok.
    with settings(warn_only=True):
        res = system.sudo("ps %s" % pid, show=False)
    return not (pid in res and cmd in res)
