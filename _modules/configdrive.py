# -*- coding: utf-8 -*-


import gzip
import json
import logging
import os
import StringIO
import shutil
import six
import tempfile
import yaml


HAS_LIBS = False
try:
  from oslo_utils import uuidutils
  from oslo_utils import fileutils
  from oslo_concurrency import processutils
  from oslo_serialization import base64
  HAS_LIBS = True
except ImportError:
    pass

LOG = logging.getLogger(__name__)


def __virtual__():
    '''
    Only load this module if mkisofs is installed on this minion.
    '''
    if not HAS_LIBS:
        return False

    for path in os.environ["PATH"].split(os.pathsep):
        if os.access(os.path.join(path, 'mkisofs'), os.X_OK):
            return True

    return False

class ConfigDriveBuilder(object):
    """Build config drives, optionally as a context manager."""

    def __init__(self, image_file):
        self.image_file = image_file
        self.mdfiles=[] # List with (path, data)

    def __enter__(self):
        fileutils.delete_if_exists(self.image_file)
        return self

    def __exit__(self, exctype, excval, exctb):
        self.make_drive()

    def add_file(self, path, data):
        self.mdfiles.append((path, data))

    def _add_file(self, basedir, path, data):
        filepath = os.path.join(basedir, path)
        dirname = os.path.dirname(filepath)
        fileutils.ensure_tree(dirname)
        with open(filepath, 'wb') as f:
            # the given data can be either text or bytes. we can only write
            # bytes into files.
            if isinstance(data, six.text_type):
                data = data.encode('utf-8')
            f.write(data)

    def _write_md_files(self, basedir):
        for data in self.mdfiles:
            self._add_file(basedir, data[0], data[1])

    def _make_iso9660(self, path, tmpdir):

        processutils.execute('mkisofs',
                      '-o', path,
                      '-ldots',
                      '-allow-lowercase',
                      '-allow-multidot',
                      '-l',
                      '-V', 'config-2',
                      '-r',
                      '-J',
                      '-quiet',
                      tmpdir,
                      attempts=1,
                      run_as_root=False)

    def make_drive(self):
        """Make the config drive.
        :raises ProcessExecuteError if a helper process has failed.
        """
        try:
          tmpdir = tempfile.mkdtemp()
          self._write_md_files(tmpdir)
          self._make_iso9660(self.image_file, tmpdir)
        finally:
          shutil.rmtree(tmpdir)


def generate(dst, hostname, domainname, instance_id=None, public_keys=None,
             user_data=None, network_data=None, ironic_format=False):
    ''' Generate config drive

    :param dst: destination file to place config drive.
    :param hostname: hostname of Instance.
    :param domainname: instance domain.
    :param instance_id: UUID of the instance.
    :param public_keys: dict of public keys.
    :param user_data: custom user data dictionary.
    :param network_data: custom network info dictionary.
    :param ironic_format: create base64 of gzipped ISO format

    CLI Example:
    .. code-block:: bash
        salt '*' configdrive.generate dst=/tmp/my_cfgdrive.iso hostname=host1
    '''
    instance_md = {}
    public_keys = public_keys or {}

    instance_md['uuid'] = instance_id or uuidutils.generate_uuid()
    instance_md['hostname'] = '%s.%s' % (hostname, domainname)
    instance_md['name'] = hostname
    instance_md['public_keys'] = public_keys

    data = json.dumps(instance_md)

    if user_data:
        user_data = '#cloud-config\n\n' + yaml.dump(user_data, default_flow_style=False)

    LOG.debug('Generating config drive for %s' % hostname)

    with ConfigDriveBuilder(dst) as cfgdrive:
        cfgdrive.add_file('openstack/latest/meta_data.json', data)
        if user_data:
            cfgdrive.add_file('openstack/latest/user_data', user_data)
        if network_data:
             cfgdrive.add_file('openstack/latest/network_data.json',
                               json.dumps(network_data))
        cfgdrive.add_file('openstack/latest/vendor_data.json', '{}')
        cfgdrive.add_file('openstack/latest/vendor_data2.json', '{}')

    b64_gzip = None
    if ironic_format:
        with open(dst) as f:
            with tempfile.NamedTemporaryFile() as tmpzipfile:
                g = gzip.GzipFile(fileobj=tmpzipfile, mode='wb')
                shutil.copyfileobj(f, g)
                g.close()
                tmpzipfile.seek(0)
                b64_gzip = base64.encode_as_bytes(tmpzipfile.read())
        with open(dst, 'w') as f:
            f.write(b64_gzip)

    LOG.debug('Config drive was built %s' % dst)
    res = {}
    res['meta-data'] = data
    if user_data:
        res['user-data'] = user_data
    if b64_gzip:
        res['base64_gzip'] = b64_gzip
    return res
