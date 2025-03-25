# next_crawler.py

import os
import sys
import re
from collections import defaultdict, deque

PAGE_PATTERNS = [r'page\.(js|jsx|ts|tsx)$']
LAYOUT_PATTERNS = [r'layout\.(js|jsx|ts|tsx)$']
DYNAMIC_ROUTE_PATTERN = r'\[(.+?)\]'

class NextjsNode:
    def __init__(self, name, path, node_type='folder'):
        self.name = name
        self.path = path
        self.node_type = node_type
        self.children = []
        self.has_component = node_type in ['page', 'layout']
    
    def add_child(self, child):
        self.children.append(child)
    
    def get_mermaid_id(self):
        clean_path = self.path.replace('/', '_').replace('.', '_').replace('-', '_')
        clean_path = re.sub(r'[^\w]', '_', clean_path)
        return f"{clean_path}"
    
    def get_mermaid_label(self):
        if self.node_type == 'page':
            return f"{self.name}"
        elif self.node_type == 'layout':
            return f"{self.name}"
        elif self.node_type == 'dynamic':
            param_name = re.search(DYNAMIC_ROUTE_PATTERN, self.name)
            if param_name:
                return f"[{param_name.group(1)}]"
            return self.name
        else:
            return self.name
    
    def get_mermaid_style(self):
        node_id = self.get_mermaid_id()
        
        if self.node_type == 'page':
            return f"style {node_id} fill:#9f9,stroke:#6c6,stroke-width:1px"
        elif self.node_type == 'layout':
            return f"style {node_id} fill:#ff9,stroke:#cc6,stroke-width:1px"
        elif self.node_type == 'dynamic':
            return f"style {node_id} fill:#9cf,stroke:#69c,stroke-width:1px"
        else:
            return ""
    
    def has_component_in_subtree(self):
        if self.has_component:
            return True
        
        for child in self.children:
            if child.has_component_in_subtree():
                return True
        
        return False

def is_page_file(filename):
    return any(re.search(pattern, filename) for pattern in PAGE_PATTERNS)

def is_layout_file(filename):
    return any(re.search(pattern, filename) for pattern in LAYOUT_PATTERNS)

def is_dynamic_route(dirname):
    return bool(re.search(DYNAMIC_ROUTE_PATTERN, dirname))

def crawl_nextjs_project(root_path):
    if not os.path.exists(root_path):
        print(f"Error: Path '{root_path}' does not exist")
        sys.exit(1)
    
    root_name = os.path.basename(root_path)
    root = NextjsNode(root_name, root_name)
    
    path_to_node = {root_name: root}
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        rel_path = os.path.relpath(dirpath, os.path.dirname(root_path))
        if rel_path == '.':
            rel_path = root_name
        
        if rel_path in path_to_node:
            current_node = path_to_node[rel_path]
        else:
            parent_path = os.path.dirname(rel_path)
            dir_name = os.path.basename(rel_path)
            
            node_type = 'dynamic' if is_dynamic_route(dir_name) else 'folder'
            current_node = NextjsNode(dir_name, rel_path, node_type)
            
            if parent_path in path_to_node:
                path_to_node[parent_path].add_child(current_node)
            
            path_to_node[rel_path] = current_node
        
        for dirname in dirnames:
            child_path = os.path.join(rel_path, dirname)
            node_type = 'dynamic' if is_dynamic_route(dirname) else 'folder'
            child_node = NextjsNode(dirname, child_path, node_type)
            current_node.add_child(child_node)
            path_to_node[child_path] = child_node
        
        for filename in filenames:
            if is_page_file(filename) or is_layout_file(filename):
                child_path = os.path.join(rel_path, filename)
                node_type = 'page' if is_page_file(filename) else 'layout'
                child_node = NextjsNode(filename, child_path, node_type)
                current_node.add_child(child_node)
                path_to_node[child_path] = child_node
    
    return root

def prune_tree(node):
    pruned_children = []
    
    for child in node.children:
        if child.has_component_in_subtree():
            pruned_child = prune_tree(child)
            pruned_children.append(pruned_child)
    
    node.children = pruned_children
    return node

def generate_mermaid(root_node):
    mermaid_lines = ["flowchart TD"]
    edges = []
    styles = []
    
    queue = deque([root_node])
    visited = set()
    
    while queue:
        node = queue.popleft()
        node_id = node.get_mermaid_id()
        
        if node_id in visited:
            continue
        
        visited.add(node_id)
        
        mermaid_lines.append(f"    {node_id}[\"{node.get_mermaid_label()}\"]")
        
        style = node.get_mermaid_style()
        if style:
            styles.append(f"    {style}")
        
        for child in node.children:
            child_id = child.get_mermaid_id()
            edges.append(f"    {node_id} --> {child_id}")
            queue.append(child)
    
    mermaid_lines.extend(edges)
    mermaid_lines.extend(styles)
    
    return "\n".join(mermaid_lines)

def save_to_file(content, filename="nextjs_project_structure.mmd"):
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Mermaid diagram saved to {filename}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python nextjs_crawler.py /path/to/nextjs/src/app")
        sys.exit(1)
    
    root_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "nextjs_project_structure.mmd"
    
    try:
        root_node = crawl_nextjs_project(root_path)
        pruned_root = prune_tree(root_node)
        mermaid_diagram = generate_mermaid(pruned_root)
        save_to_file(mermaid_diagram, output_file)
        print("Render this diagram on https://mermaid.live or MD")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()