import os
from lvrt_adapter import PlatformAdapter, PlatformInputAdapter
from workspacecontrol.api.exceptions import *
import lvrt_model

class vmmadapter(PlatformAdapter):
    
    def __init__(self, params, common):
        PlatformAdapter.__init__(self, params, common)
        other_uri = self.p.get_conf_or_none("libvirt_connections", "xen3")
        if other_uri:
            self.connection_uri = other_uri
        else:
            self.connection_uri = "xen:///"
        self.c.log.debug("Xen libvirt URI: '%s'" % self.connection_uri)

    def validate(self):
        self.c.log.debug("validating libvirt xen3 adapter")
    
        # not required to be present
        pygrubpath = self.p.get_conf_or_none("xencreation", "pygrub")
        if pygrubpath and not os.access(pygrubpath, os.F_OK):
            raise InvalidConfig("pygrub path does not seem to exist: '%s'" % pygrubpath)

class intakeadapter(PlatformInputAdapter):
    def __init__(self, params, common):
        PlatformInputAdapter.__init__(self, params, common)
        
    def fill_model(self, dom, local_file_set, nic_set, kernel):
        dom._type = "xen"
        dom.os.type = "xen"
        
        dom.on_poweroff = self.p.get_conf_or_none("xencreation", "on_poweroff")
        dom.on_reboot = self.p.get_conf_or_none("xencreation", "on_reboot")
        dom.on_crash = self.p.get_conf_or_none("xencreation", "on_crash")
        
        # values: "tap:aio", "tap:qcow" or "file".  If None, assume file
        driver = self.p.get_conf_or_none("xencreation", "disk_driver")
        if not driver:
            driver = "file"
        if driver != "tap:aio" and driver != "tap:qcow" and driver != "file":
            raise InvalidConfig("unknown xen disk driver value: %s" % driver)
        for disk in dom.devices.disks:
            disk.driver = driver
            
        for lf in local_file_set.flist():
            if lf.physical:
                for disk in dom.devices.disks:
                    if disk.target == lf.mountpoint:
                        disk._type = "block"
                        self.c.log.debug("set as block device: '%s' with mountpoint '%s'" % (disk.source, disk.target))
        
        script = self.p.get_conf_or_none("xencreation", "bridge_script")
        if script:
            for interface in dom.devices.interfaces:
                interface.script_path = script
        
        if kernel.onboard_kernel:
            pygrub = self.p.get_conf_or_none("xencreation", "pygrub")
            if not pygrub:
                raise UnexpectedError("hard disk image boot was requested but this functionality is disabled (no pygrub path)")
            dom.bootloader = pygrub
            return # *** EARLY RETURN ***
            
        if not kernel.kernel_path:
            raise UnexpectedError("no kernel_path")
            
        self.c.log.debug("kernel_path: %s" % kernel.kernel_path)
        
        dom.os.kernel = kernel.kernel_path

        if kernel.initrd_path:
            dom.os.initrd = kernel.initrd_path
            
        rootmountpoint = None
        for lf in local_file_set.flist():
            if lf.rootdisk:
                rootmountpoint = lf.mountpoint
        if not rootmountpoint:
            raise UnexpectedError("cannot find root disk's mountpoint")
            
        rootstring = "ro root=/dev/%s" % rootmountpoint
        if kernel.kernel_args:
            dom.os.cmdline = "%s %s" % (rootstring, kernel.kernel_args)
        else:
            dom.os.cmdline = "%s" % (rootstring)
            

