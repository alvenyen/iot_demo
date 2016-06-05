#!/usr/bin/python
import os
import cgi, cgitb 
from node_manager import NodeManager
from cgi_utils import send_response

form = cgi.FieldStorage() 

node_id = form.getvalue('node_id')
component = form.getvalue('component')
command = form.getvalue('command')

nm = NodeManager()
nm.control_node(node_id, component, command)
send_response({}, 0)
