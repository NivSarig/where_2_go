import logging
import argparse
import sys

logger = logging.getLogger(__name__)


def main():

    if len(sys.argv) == 1:

        input = '/home/niv/dev/route_your_way/external_integrations/optimization_engine/examples/hk48.tsp'
        output = '/home/niv/output.txt'
    else:
        # Create the parser
        cparser = argparse.ArgumentParser(description='Commandline tool to run tsp problems with concorde')

        # Add the arguments
        cparser.add_argument('--input',
                             required=True,
                             metavar='inputfile',
                             type=str,
                             help='TSPLIB input format file.')
        cparser.add_argument('--output',
                             required=True,
                             metavar='outputfile',
                             type=str,
                             help='TSPLIB output format file.')

        # Execute the parse_args() method
        args = cparser.parse_args()


        input = args.input
        output = args.output

    import tsplib95
    from concorde.tsp import TSPSolver

    # Show selected input
    print("Input file  : {}".format(input))
    print("Output file : {}".format(output))

    # Load input file and run Concorde
    solver = TSPSolver.from_tspfile(input)

    # Access the optimal tour
    tour_data = solver.solve()

    # Print optimal tour
    print(tour_data.tour)

    with open(output, 'w') as f:
        for stop in tour_data.tour:
            f.write(f"{stop}\n")


if __name__ == "__main__":
    main()
