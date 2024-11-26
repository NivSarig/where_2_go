input_file_path = "/home/niv/dev/route_your_way/external_integrations/optimization_engine/examples/hk48.tsp"
input_file_path = "/home/niv/dev/route_your_way/external_integrations/optimization_engine/examples/hk48_changed.tsp"
output = "/home/niv/output.txt"
process_string = '/home/niv/dev/tspsolver/concorde_env/bin/python ' \
                 '/home/niv/dev/route_your_way/external_integrations/optimization_engine/solve_tsp.py '\
                 '--input {}  --output {}'.format(input_file_path, output)

import subprocess

# Define the command to run
# Run the command

result = subprocess.run(process_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Check if the command was successful
if result.returncode == 0:
    # Print the output
    print("Output:", result.stdout.decode())
else:
    # Print the error message
    print("Error:", result.stderr.decode())
