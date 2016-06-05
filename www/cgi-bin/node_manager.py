import inspect
import json
import os
import subprocess
import shlex
import time
import tempfile

CGI_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
NODE_META_FILE = '{}/node_meta.json'.format(CGI_PATH)

class DoCommandTimedOut(RuntimeError):
    pass


class DoCommandError(RuntimeError):
    def __init__(self, stderr, errno=0, stdout=''):
        RuntimeError.__init__(self, stderr)
        self.errno, self.stdout, self.stderr = errno, stdout, stderr

    def __str__(self):
        return "DoCommandError: errno {} stdout '{}' stderr '{}'" \
               .format(self.errno, self.stdout, self.stderr)

def do_cmd(cmd, force=False):
    cmdstr = cmd.encode('utf-8')
    with tempfile.TemporaryFile('w+') as outfp:
        with tempfile.TemporaryFile('w+') as errfp:
            p = subprocess.Popen([cmdstr],
                                 stdout=outfp,
                                 stderr=errfp,
                                 shell=True,
                                 close_fds=True)
            p.wait()
            outfp.flush()   # don't know if this is needed
            outfp.seek(0)
            output = outfp.read()
            errfp.flush()   # don't know if this is needed
            errfp.seek(0)
            err = errfp.read()

    # prevent UnicodeDecodeError if invalid char in error/output
    err_str = unicode(err, 'utf-8', 'ignore')
    out_str = unicode(output, 'utf-8', 'ignore')
    if p.returncode != 0:
        if force:
            return ""
        else:
            raise DoCommandError(err, p.returncode, output)

    return output

class NodeManager:
    def __init__(self):
        self._meta = None
        self.load_meta()

    def load_meta(self):
        raw_meta = None
        with open(NODE_META_FILE, 'r') as f:
            raw_meta = f.read()

        if raw_meta:
            self._meta = json.loads(raw_meta)
        else:
            self._meta = None
            raise Exception("Cannot load node meta")

    def save_meta(self):
        if self._meta is not None:
            with open(NODE_META_FILE, 'w') as f:
                f.write(json.dumps(self._meta, sort_keys=True, indent=4))
        else:
            raise Exception("Current node meta is empty")

    def refresh_nodes_state(self):
        # XXX: Do the real stuff here
        pass

    def list_node(self):
        """Return a node list

        **Example return**:
            {
                "1": {
                    "node_id": "1", 
                    "node_name": "node-1", 
                    "online": true
                }, 
                "2": {
                    "node_id": "2", 
                    "node_name": "node-2", 
                    "online": true
                }, 
                "3": {
                    "node_id": "3", 
                    "node_name": "node-3", 
                    "online": false
                }
            }
        """
        if self._meta:
            # XXX: Do the real stuff here
            return self._meta['nodes']
        else:
            return []

    def add_node(self, node_id, node_name):
        if not node_id or not node_name:
            Exception("Invalid node id or name")

        if node_id in self._meta['nodes']:
            Exception("Node {} already exists".format(node_id))

        node_info = {
            'node_id': node_id,
            'node_name': node_name,
            'online': False,
            'components': {
                'led': {
                    'component_name': 'led', 
                    'state': 'off'
                }
            }
        }
        self._meta['nodes'][node_id] = node_info
        self.save_meta()

    def delete_node(self, node_id):
        if node_id not in self._meta['nodes']:
            Exception("Node {} does not exist".format(node_id))

        del self._meta['nodes'][node_id]
        self.save_meta()

    def control_node(self, node_id, component, command):
        if node_id not in self._meta['nodes']:
            raise Exception("Cannot find node: {}".format(node_id))

        if component not in self._meta['nodes'][node_id]['components']:
            raise Exception("Cannot find component {} in node: {}".format(component, node_id))

        if component == 'led':
            if command == 'on':
                do_cmd("ledon {}".format(node_id), force=True)
                # XXX: Do the real stuff here
                self._meta['nodes'][node_id]['components'][component]['state'] = 'on'
                self.save_meta()
            else:
                raise Exception("Did not support command: {}".format(command))
        else:
            raise Exception("Did not have component: {}".format(component))
