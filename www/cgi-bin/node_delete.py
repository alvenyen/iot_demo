#!/usr/bin/python
import os
import cgi, cgitb 
from node_manager import NodeManager
from cgi_utils import send_response

form = cgi.FieldStorage() 

node_ids = form.getvalue('node_id_list').split(',')

nm = NodeManager()
for node_id in node_ids:
    nm.delete_node(node_id)
send_response({}, 0)