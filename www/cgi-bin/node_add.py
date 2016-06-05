#!/usr/bin/python
import os
import cgi, cgitb 
from node_manager import NodeManager
from cgi_utils import send_response

form = cgi.FieldStorage() 

node_id = form.getvalue('node_id')
node_name = form.getvalue('node_name')

nm = NodeManager()
nm.add_node(node_id, node_name)
send_response({}, 0)