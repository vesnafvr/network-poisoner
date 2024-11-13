from network_degree_modifier import modify_network_structure

# Specify your input and output files
input_file = "lesmis.csv"  # Replace with your input file name
output_file = "modified_lesmis.csv"  # Replace with desired output name

# Modify the network (increase degrees by 20%)
modified_df, old_stats, new_stats = modify_network_structure(
    input_file=input_file,
    output_file=output_file,
    degree_change=1.2  # Change this value to increase/decrease degrees
)

# Print summary of changes
print("\nNetwork Modification Summary:")
print("-" * 30)
print(f"Original edges: {old_stats['num_edges']}")
print(f"Modified edges: {new_stats['num_edges']}")
print(f"Original avg degree: {old_stats['avg_degree']:.2f}")
print(f"Modified avg degree: {new_stats['avg_degree']:.2f}")
print(f"\nModified network saved to: {output_file}")
