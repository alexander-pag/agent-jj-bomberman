from graphviz import Digraph


class TreeVisualizer:
    def __init__(self):
        self.tree = Digraph(format="png")  # Crea un grafo dirigido
        self.node_id = 0  # Para identificar nodos únicos
        self.nodes = {}  # Para mapear posiciones a nodos únicos
        self.prunes = []  # Lista de podas (nodo, motivo)

    def add_node(self, label, parent=None, pruned=False, agent=None):
        """Agrega un nodo al grafo."""
        node_name = f"node_{self.node_id}"
        if pruned:
            label = f"{label}\nPruned {agent}"
            self.tree.node(
                node_name, label, color="red", style="filled", fillcolor="pink"
            )
        else:
            self.tree.node(node_name, label, color="black")

        if parent:
            self.tree.edge(parent, node_name, color="red" if pruned else "black")

        self.node_id += 1
        return node_name

    def save(self, filename):
        self.tree.render(filename, cleanup=True)
