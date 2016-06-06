import sys, time, os, atexit
import errno
from signal import signal, SIGTERM, SIGKILL, SIGUSR1
from threading import Event

class Daemon(object):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', kill_timeout=90):
        """
        Constructor.

        @param  pidfile:    path of the pid file
        @type   pidfile:    string
        @param  stdin:      path of the stdin
        @type   stdin:      string
        @param  stdout:     path of the stdout
        @type   stdout:     string
        @param  stderr:     path of the stderr
        @type   stderr:     string
        """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self._kill_timeout = kill_timeout
        self._daemon_stopped = Event()
        self.first_loop = True

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

    def delpid(self):
        """
        Delete the pid file.
        """
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        pid = self.get_pid()

        if pid:
            try:
                # Check if process is running
                os.kill(pid, 0)
                sys.stderr.write('Process {} from pidfile {} is alive. Daemon already running?\n'.format(pid, self.pidfile))
                sys.exit(0)
            except OSError as e:
                if e.errno != errno.ESRCH:
                    raise

        # Start the daemon
        self.prepare_start()
        self.daemonize()
        signal(SIGTERM, self.handle_term)
        daemon_name = self.__class__.__name__
        try:
            self.run()
        except Exception:
            pass

    def get_pid(self):
        # Get the pid from the pidfile
        try:
            pid = int(file(self.pidfile).read().strip())
        except IOError:
            pid = None
        return pid

    def stop(self):
        """
        Stop the daemon
        """
        pid = self.get_pid()

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        pgid = os.getpgid(pid)
        # Try killing the daemon process
        try:
            waiting_killed = 0
            while 1:
                if waiting_killed == 0:
                    os.kill(pid, SIGTERM)
                elif waiting_killed < self._kill_timeout:
                    os.kill(pid, 0)
                else:
                    # Use kill pg to force kill all subprocess
                    os.killpg(pgid, SIGKILL)
                time.sleep(1)
                waiting_killed = waiting_killed + 1
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def prepare_start(self):
        """
        You should override this method when you subclass Daemon. It will be called before the process has been
        daemonized by start() or restart().
        """

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """

    def terminate(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by stop() or restart().
        """

    def is_daemon_running(self, wait=0):
        # do not wait for first loop
        if self.first_loop and wait > 0:
            wait = 0
            self.first_loop = False
        return not self._daemon_stopped.wait(wait)

    def handle_term(self, sig, frm):
        if self.is_daemon_running():
            self._daemon_stopped.set()
            self.terminate()
