from typing import Any

class TreeValidationError(Exception):
    pass

def validate_tree(nodes: list[Any]) -> None:
    """
    Validates a list of document structure nodes.
    Supports both SQLAlchemy ORM objects and dictionary representations.
    """
    if not nodes:
        return

    node_map = {}
    order_indices = set()

    for idx, node in enumerate(nodes):
        node_id = getattr(node, "id", None) or node.get("id")
        parent_id = getattr(node, "parent_id", None) or node.get("parent_id")
        order_index = getattr(node, "order_index", None)
        if order_index is None:
            order_index = node.get("order_index")
        page_start = getattr(node, "page_start", None)
        if page_start is None:
            page_start = node.get("page_start")
        page_end = getattr(node, "page_end", None)
        if page_end is None:
            page_end = node.get("page_end")

        if not node_id:
            raise TreeValidationError("Node is missing unique id.")

        node_map[node_id] = {
            "parent_id": parent_id,
            "order_index": order_index,
            "page_start": page_start,
            "page_end": page_end
        }

        # Validate page ranges
        if page_start is not None and page_end is not None:
            if page_start > page_end:
                raise TreeValidationError(f"Node {node_id} has invalid page range: page_start ({page_start}) > page_end ({page_end}).")

        # Validate section boundaries
        metadata = getattr(node, "metadata_json", None) or node.get("metadata_json")
        if metadata and "section_boundary" in metadata:
            boundary = metadata["section_boundary"]
            b_char_start = boundary.get("char_start")
            b_char_end = boundary.get("char_end")
            b_line_start = boundary.get("line_start")
            b_line_end = boundary.get("line_end")
            b_page_start = boundary.get("page_start")
            b_page_end = boundary.get("page_end")
            
            if b_char_start is not None and b_char_end is not None:
                if b_char_start > b_char_end:
                    raise TreeValidationError(f"Node {node_id} has invalid section boundary characters range: {b_char_start} > {b_char_end}.")
            if b_line_start is not None and b_line_end is not None:
                if b_line_start > b_line_end:
                    raise TreeValidationError(f"Node {node_id} has invalid section boundary lines range: {b_line_start} > {b_line_end}.")
            if b_page_start is not None and b_page_end is not None:
                if b_page_start > b_page_end:
                    raise TreeValidationError(f"Node {node_id} has invalid section boundary pages range: {b_page_start} > {b_page_end}.")

        # Validate order index unique check
        if order_index is not None:
            if order_index in order_indices:
                raise TreeValidationError(f"Duplicate order_index found: {order_index}.")
            order_indices.add(order_index)

    # Verify monotonic increasing order_index starting at 0
    if order_indices:
        sorted_orders = sorted(list(order_indices))
        if sorted_orders[0] != 0 or sorted_orders[-1] != len(sorted_orders) - 1:
            raise TreeValidationError(f"Order indices are not contiguous or do not start from 0: {sorted_orders}")

    # Validate parent existence and circular reference checks
    for node_id, data in node_map.items():
        parent_id = data["parent_id"]
        if parent_id:
            if parent_id not in node_map:
                raise TreeValidationError(f"Node {node_id} references a missing parent_id: {parent_id}.")

            # Cycle detection (tortoise and hare or set of visited)
            visited = {node_id}
            curr = parent_id
            while curr:
                if curr in visited:
                    raise TreeValidationError(f"Circular reference detected involving node: {curr}.")
                visited.add(curr)
                curr = node_map[curr]["parent_id"]
