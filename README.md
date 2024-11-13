# network_poisoner

The network_degree_modifier.py script contains all the functions and code needed, it defines the network modification.
The network_runner.py script uses the tools created in network_degree_modifier.py and executes the modification.

So your workflow should be:

1. Have these files in your folder:
   
  Your network Excel/CSV file
  
  network_degree_modifier.py
  
  network_runner.py 
  
3. Change the input_file in network_runner.py to the network file name
4. Change the output_file in network_runner.py to the your chosen modified network name
5. You can optioanlly change degree_change=1.2 in network_runner.py if you want more or less modification (1.2 = +20%, 0.8 = -20%, etc.)
6. Run: python3 network_runner.py  in bash
