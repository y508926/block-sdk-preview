import os, sys
import errno
from pysys import log

def run(args):
    log.info('Configuring designer for Analytics Builder')

    # Check the command has been executing from Apama command prompt
    apama_home = os.getenv('APAMA_HOME', '')
    if not apama_home: raise BuildException(
        'APAMA_HOME is not set in this environment - this command is intended to be executed from within an Apama command prompt.')

    filename = "%s/../Designer/extensions/analyticsBuilder.ste" % apama_home
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    # Creating .ste file under designer extensions folder
    try:
        with open(filename, "w") as f:
            f.write('VARIABLE ; PAB_SDK ; %s ; R \n' % (os.path.abspath(os.path.dirname(sys.argv[0])).replace('\\', '/'),))
            f.write('BUNDLE_CATALOG ; PAB_SDK/bundles')
    except IOError as e:
        if e.errno == errno.EACCES:
            raise
        else:
            log.exception(e)
