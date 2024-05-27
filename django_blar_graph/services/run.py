import os
from sys import path as syspath

from blar_graph.db_managers import Neo4jManager
from blar_graph.graph_construction.core.graph_builder import GraphConstructor
from git import Repo  # Assuming you are using GitPython library for cloning

graph_manager = Neo4jManager("5c8ecf8ea3089d04f12c717afe0cdc9a86e70ddbebb668a3e376afd069862e67")
print(syspath)

graph_constructor = GraphConstructor(graph_manager, "python")
graph_constructor.build_graph("temp_repos/code-base-agent")
graph_manager.close()