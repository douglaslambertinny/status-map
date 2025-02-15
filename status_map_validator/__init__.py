__version__ = "0.5.1"

from collections.abc import Mapping
from copy import deepcopy
from functools import lru_cache

from networkx import DiGraph, ancestors, descendants

from .exceptions import (
    AmbiguousTransitionError,
    FutureTransitionError,
    PastTransitionError,
    StatusNotFoundError,
    TransitionNotFoundError,
)


class StatusMap(Mapping):
    def __init__(self, transitions):
        graph = DiGraph()
        graph.add_nodes_from(transitions.keys())
        nodes = deepcopy(graph.nodes)
        for node in nodes:
            edges = transitions[node]
            if isinstance(edges, dict):
                edges_to_add = ((node, edge, attribute) for edge, attribute in edges.items())
                self._add_transition_validations(node, edges)
            else:
                edges_to_add = ((node, edge) for edge in edges)
            graph.add_edges_from(edges_to_add)
        self._graph = graph

    def __repr__(self):
        return f"StatusMap(statuses={self.statuses})"

    def __str__(self):
        return f"{self.statuses}"

    def __getitem__(self, node):
        return self._graph[node]

    def __len__(self):
        return self._graph.number_of_nodes()

    def __iter__(self):
        return iter(self._graph.nodes)

    @property
    def statuses(self):
        return tuple(self._graph.nodes)

    @staticmethod
    @lru_cache(maxsize=512)
    def get_ancestors(graph, status):
        return ancestors(graph, status)

    @staticmethod
    @lru_cache(maxsize=512)
    def get_descendants(graph, status):
        return descendants(graph, status)

    def _add_transition_validations(self, from_state, transitions):
        """
        This method get the validation methods from the transitions dict 'validation' key
        """
        for to_state, attributes in transitions.items():
            validation_methods = attributes.get("validation", [])
            for validation_method in validation_methods:
                self._add_validation(from_state, to_state, validation_method)

    def _add_validation(self, from_state, to_state, validation_method):
        """
        Add validation method for a transition from one state to another.
        """
        if not hasattr(self, "_validations"):
            self._validations = {}
        if from_state not in self._validations:
            self._validations[from_state] = {}
        self._validations[from_state][to_state] = validation_method

    def get_validations(self, from_state, to_state):
        """
        Get validation methods for a transition.
        """
        return self._validations.get(from_state, {}).get(to_state, [])

    def validate_transition(self, from_status, to_status):
        if not self._graph.has_node(from_status):
            raise StatusNotFoundError(f"from_status {from_status} not found")

        if not self._graph.has_node(to_status):
            raise StatusNotFoundError(f"to_status {to_status} not found")

        if from_status == to_status or self._graph.has_successor(from_status, to_status):
            return

        is_ancestor = to_status in StatusMap.get_ancestors(self._graph, from_status)
        is_descendant = to_status in StatusMap.get_descendants(self._graph, from_status)

        if is_ancestor and is_descendant:
            raise AmbiguousTransitionError(f"from {from_status} to {to_status} is both past and future")

        if is_descendant:
            raise FutureTransitionError(f"from {from_status} to {to_status} should happen in the future")

        if is_ancestor:
            raise PastTransitionError(f"from {from_status} to {to_status} should have happened in the past")

        raise TransitionNotFoundError(f"from {from_status} to {to_status} not found")
