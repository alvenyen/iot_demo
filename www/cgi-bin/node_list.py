#!/usr/bin/python
import os
import cgi, cgitb 
from node_manager import NodeManager
from cgi_utils import send_response

nm = NodeManager()
nodes = nm.list_node()
data = {'nodes': nodes}
send_response(data, 0)
