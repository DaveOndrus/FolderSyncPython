import os

import utils


"""
Object for mapping directory with info about it.
    rel_path - relative path to file/folder
    abs_path - absolute path to file/folder
    is_file - True if object is file False if is a directory
    children - list of Directory objects
    hash_value - hash value if is_file = True
"""
class Directory:
    def __init__(self, path, is_file=False, hash_value=None):
        self.rel_path = None
        self.abs_path = path
        self.is_file = is_file
        self.children = []
        self.hash_value = hash_value

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return self.abs_path + ("/" if not self.is_file else "")

    def compare(self, other):
        if self.rel_path == other.rel_path:
            if self.is_file and other.is_file:
                if self.hash_value == other.hash_value:
                    return "Same"
                else:
                    return "Different"
            if not self.is_file and not other.is_file:
                return "Same"
            else:
                return "Different"

        else:
            return "Different"

    def find_differences(self, other, diff_list):
        for child1 in self.children:
            child2 = next((x for x in other.children if child1.rel_path == x.rel_path), None)
            if child2:
                comparison_result = child1.compare(child2)
                if comparison_result == "Different":
                    diff_list.append(child1)
                if not child1.is_file:
                    child1.find_differences(child2, diff_list)

            else:
                diff_list.append(child1)

    def convert_to_relative_path(self, root_path):
        self.rel_path = os.path.relpath(self.abs_path, root_path)
        for child in self.children:
            child.convert_to_relative_path(root_path)


def generate_tree(root_path):
    root_node = Directory(os.path.abspath(root_path))
    for item in os.listdir(root_path):
        item_path = os.path.join(root_path, item)
        if os.path.isdir(item_path):
            root_node.add_child(generate_tree(item_path))
        else:
            root_node.add_child(Directory(item_path, is_file=True, hash_value=utils.compute_hash(item_path)))
    return root_node


def print_tree(node, indent=0):
    print("  " * indent + str(node))
    for child in node.children:
        print_tree(child, indent + 1)
