import tempfile

from blar_graph.db_managers import Neo4jManager
from blar_graph.graph_construction.core.graph_builder import GraphConstructor
from git import Repo  # Assuming you are using GitPython library for cloning

from django_blar_graph.models import Repos


def get_repository_from_db(repo_id, user):
    try:
        repository = Repos.objects.get(repo_id=repo_id, user=user)
        return repository
    except Repos.DoesNotExist:
        return None


def clone_repo_from_github(repo_db: Repos, branch):
    # Create a temporary directory to clone the repository
    try:
        with tempfile.TemporaryDirectory(prefix="temp_repos_") as temp_dir:
            print(temp_dir)
            Repo.clone_from(repo_db.url, temp_dir, branch=branch)
            graph_manager = Neo4jManager(repo_db.repo_id)
            print(repo_db.repo_id)
            graph_manager.query(
                f"MATCH (n {{repo_id: '{repo_db.repo_id}'}}) DETACH DELETE n"
            )
            graph_constructor = GraphConstructor(graph_manager, "python")
            graph_constructor.build_graph(temp_dir)
            graph_manager.close()

        return True

        return True
    except Exception as e:
        # Handle exceptions if cloning fails
        print("Error:", e)
        return None
