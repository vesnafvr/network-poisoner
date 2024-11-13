import pandas as pd
import networkx as nx
import random
from itertools import combinations

def modify_network_structure(input_file, output_file, degree_change=1.2, min_edges=None, max_edges=None):
    """
    Modify network structure by adjusting node degrees and output in original format.
    """
    # Read the spreadsheet and store original column order
    try:
        if input_file.endswith('.csv'):
            original_df = pd.read_csv(input_file)
        else:
            original_df = pd.read_excel(input_file)
        original_columns = original_df.columns.tolist()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    print("Data types of source and target:")
    print(f"Source: {original_df['source'].dtype}")
    print(f"Target: {original_df['target'].dtype}")
    
    # Convert source and target to strings to ensure consistent handling
    original_df['source'] = original_df['source'].astype(str)
    original_df['target'] = original_df['target'].astype(str)
    
    # Create original network graph
    G = nx.Graph()
    for _, row in original_df[['source', 'target']].iterrows():
        G.add_edge(row['source'], row['target'])
    
    # Store original network statistics
    original_stats = get_network_stats(G)
    
    # Calculate target number of edges
    current_edges = G.number_of_edges()
    target_edges = int(current_edges * degree_change)
    
    if min_edges is not None:
        target_edges = max(target_edges, min_edges)
    if max_edges is not None:
        target_edges = min(target_edges, max_edges)
    
    # Create modified graph
    G_modified = G.copy()
    
    if target_edges > current_edges:
        add_strategic_edges(G_modified, target_edges - current_edges)
    elif target_edges < current_edges:
        remove_strategic_edges(G_modified, current_edges - target_edges)
    
    # Calculate new network statistics
    new_stats = get_network_stats(G_modified)
    
    # Create new edge list from modified graph
    new_edges = list(G_modified.edges())
    modified_df = pd.DataFrame(new_edges, columns=['source', 'target'])
    
    # Create mappings from original dataframe
    original_mappings = {}
    for col in original_columns:
        if col not in ['source', 'target']:
            if col == 'modularity_class':
                original_mappings[col] = original_df.groupby('source')[col].first().to_dict()
            elif col == 'Id':
                modified_df[col] = range(len(modified_df))
            elif 'edge' in col.lower():
                continue
            else:
                original_mappings[col] = original_df.groupby('source')[col].first().to_dict()
    
    # Apply mappings to new dataframe
    for col, mapping in original_mappings.items():
        modified_df[col] = modified_df['source'].map(mapping)
    
    # Calculate new network metrics
    degrees = dict(G_modified.degree())
    modified_df['source_degree'] = modified_df['source'].map(degrees)
    modified_df['target_degree'] = modified_df['target'].map(degrees)
    
    # Calculate edge betweenness with error handling
    try:
        edge_between = nx.edge_betweenness_centrality(G_modified)
        modified_df['edge_betweenness'] = [edge_between.get((s, t)) or edge_between.get((t, s), 0.0) 
                                          for s, t in zip(modified_df['source'], modified_df['target'])]
    except Exception as e:
        print(f"Warning: Error calculating edge betweenness: {e}")
        modified_df['edge_betweenness'] = 0.0
    
    # Ensure columns are in the original order
    final_columns = []
    for col in original_columns:
        if col in modified_df.columns:
            final_columns.append(col)
    
    # Add any new metrics at the end
    for col in modified_df.columns:
        if col not in final_columns:
            final_columns.append(col)
    
    modified_df = modified_df[final_columns]
    
    # Convert back to original datatypes if needed
    if 'source' in original_df.columns:
        try:
            original_source_dtype = original_df['source'].dtype
            modified_df['source'] = modified_df['source'].astype(original_source_dtype)
        except:
            pass
    
    if 'target' in original_df.columns:
        try:
            original_target_dtype = original_df['target'].dtype
            modified_df['target'] = modified_df['target'].astype(original_target_dtype)
        except:
            pass
    
    # Save modified data
    try:
        if output_file.endswith('.csv'):
            modified_df.to_csv(output_file, index=False)
        else:
            writer = pd.ExcelWriter(output_file, engine='openpyxl')
            modified_df.to_excel(writer, index=False, sheet_name='Network Data')
            
            # Add statistics to a new sheet
            stats_comparison = pd.DataFrame({
                'Metric': list(original_stats.keys()),
                'Original': list(original_stats.values()),
                'Modified': list(new_stats.values()),
                'Change': [f"{(new_stats[k] - original_stats[k])/original_stats[k]:.2%}" 
                          if isinstance(original_stats[k], (int, float)) and original_stats[k] != 0 
                          else "N/A" for k in original_stats.keys()]
            })
            stats_comparison.to_excel(writer, index=False, sheet_name='Network Statistics')
            
            writer.close()
        print(f"Modified network data saved to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")
    
    return modified_df, original_stats, new_stats

def add_strategic_edges(G, num_edges):
    """
    Add edges to the graph strategically, preserving network properties.
    """
    nodes = list(G.nodes())
    possible_edges = list(combinations(nodes, 2))
    existing_edges = set(G.edges())
    possible_edges = [e for e in possible_edges if e not in existing_edges]
    
    degrees = dict(G.degree())
    edge_scores = [(e, degrees[e[0]] + degrees[e[1]]) for e in possible_edges]
    edge_scores.sort(key=lambda x: x[1], reverse=True)
    
    edges_to_add = min(num_edges, len(edge_scores))
    for i in range(edges_to_add):
        edge = edge_scores[i][0]
        G.add_edge(edge[0], edge[1])

def remove_strategic_edges(G, num_edges):
    """
    Remove edges strategically, preserving network connectivity and structure.
    """
    edge_betweenness = nx.edge_betweenness_centrality(G)
    edges_to_consider = [(e, edge_betweenness[e]) for e in G.edges()]
    edges_to_consider.sort(key=lambda x: x[1])
    
    edges_removed = 0
    for edge, _ in edges_to_consider:
        G.remove_edge(*edge)
        if nx.is_connected(G):
            edges_removed += 1
            if edges_removed >= num_edges:
                break
        else:
            G.add_edge(*edge)

def get_network_stats(G):
    """
    Calculate and return comprehensive network statistics
    """
    stats = {
        'num_nodes': G.number_of_nodes(),
        'num_edges': G.number_of_edges(),
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
        'density': nx.density(G),
        'is_connected': nx.is_connected(G),
        'avg_clustering': nx.average_clustering(G),
        'degree_assortativity': nx.degree_assortativity_coefficient(G),
        'avg_shortest_path': nx.average_shortest_path_length(G) if nx.is_connected(G) else float('inf')
    }
    return stats
