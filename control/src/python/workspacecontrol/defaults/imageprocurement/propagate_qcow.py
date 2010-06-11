from commands import getstatusoutput
import os
import string
from propagate_adapter import PropagationAdapter
from workspacecontrol.api.exceptions import *

class propadapter(PropagationAdapter):

    def __init__(self, params, common):
        PropagationAdapter.__init__(self, params, common)
        self.qcow_create = None

    def validate(self):
        self.c.log.debug("validating qcow propagation adapter")

        self.qcow_create = self.p.get_conf_or_none("propagation", "qcow_create")
        if not self.qcow_create:
            raise InvalidConfig("no path to qcow-create")

        if os.path.isabs(self.qcow_create):
            if not os.access(self.qcow_create, os.F_OK):
                raise InvalidConfig("qcow-create is configured with an absolute path, but it does not seem to exist: '%s'" % self.qcow_create)

            if not os.access(self.qcow_create, os.X_OK):
                raise InvalidConfig("qcow-create is configured with an absolute path, but it does not seem executable: '%s'" % self.qcow_create)

        self.c.log.debug("qcow-create configured: %s" % self.qcow_create)

    def validate_propagate_source(self, imagestr):
        return

    def validate_unpropagate_target(self, imagestr):
        return

    def propagate(self, remote_source, local_absolute_target):
        self.c.log.info("QCOW propagation - remote source: %s" % remote_source)
        self.c.log.info("QCOW propagation - local target: %s" % local_absolute_target)

        size = "12G" # FIXME
        backing_image = self.backing_image
        if not os.path.isfile(backing_image):
            errmsg = "QCOW backing file %s does not exist" % backing_image
            self.c.log.error(errmsg)
            raise UnexpectedError(errmsg)
        cmd = "%s %s %s %s" % (self.qcow_create, size, local_absolute_target, backing_image)
        self.c.log.info("Running QCOW command: %s" % cmd)

        ret,output = getstatusoutput(cmd)
        if ret:
            errmsg = "problem running command: '%s' ::: return code" % cmd
            errmsg += ": %d ::: output:\n%s" % (ret, output)
            self.c.log.error(errmsg)
            raise UnexpectedError(errmsg)
        self.c.log.info("QCOW disk creation complete.")

    def unpropagate(self, local_absolute_source, remote_target):
        raise UnexpectedError(errmsg)
