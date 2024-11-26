import os.path
import argparse

import tsplib95
from concorde.tsp import TSPSolver
from concorde.problem import Problem

import itertools
import numpy as np
import re

INF = 10000


class ATSPConvert:
    def __init__(self, matrix):
        """
        input: Adjacency matrix N x N
        len(nodes) = shape(input)
        @param matrix: N x N matrix
        """
        # 1: Check if the adjacency matrix is symmetric
        self.cost_matrix = np.array(matrix)
        self.size = len(self.cost_matrix)
        self.nodes = range(self.size)

    def get_cost_matrix(self):
        return self.cost_matrix

    def as_symmetric(self):
        """
        Reformulate an asymmetric TSP as a symmetric TSP:
        "Jonker and Volgenant 1983"
        This is possible by doubling the number of nodes. For each city a dummy
        node is added: (a, b, c) => (a, a', b, b', c, c')

        distance = "value"
        distance (for each pair of dummy nodes and pair of nodes is INF)
        distance (for each pair node and its dummy node is -INF)
        ------------------------------------------------------------------------
          |A'   |B'   |C'   |A    |B    |C    |
        A'|0    |INF  |INF  |-INF |dBA  |dCA  |
        B'|INF  |0    |INF  |dAB  |-INF |dCB  |
        C'|INF  |INF  |0    |dAC  |dBC  |-INF |
        A |-INF |dAB  |dAC  |0    |INF  |INF  |
        B |dBA  |-INF |dBC  |INF  |0    |INF  |
        C |dCA  |dCB  |-INF |INF  |INF  |0    |

        For large matrix an exact solution is infeasible
        if N > 5 (N = N*2 > 10) then use other techniques:
        Heuristics and relaxation methods
        @return: new symmetric matrix

        [INF][A.T]
        [A  ][INF]
        """

        shape = len(self.cost_matrix)
        mat = np.identity(shape) * -INF + self.cost_matrix

        new_shape = shape * 2
        new_matrix = np.ones((new_shape, new_shape)) * INF * 100
        np.fill_diagonal(new_matrix, 0)

        # insert new matrices
        new_matrix[shape:new_shape, :shape] = mat
        new_matrix[:shape, shape:new_shape] = mat.T
        # new cost matrix after transformation
        self.cost_matrix = new_matrix

    def total_tour(self, tour):
        total = sum(self.cost_matrix[tour[node], tour[(node + 1) % self.size]] for node in self.nodes)
        return total, tour


def main():
    # Create the parser
    cparser = argparse.ArgumentParser(description="Commandline tool to run tsp problems with concorde")

    # Add the arguments
    cparser.add_argument(
        "--tspinput",
        required=False,
        metavar="tspinputfile",
        type=str,
        help="TSPLIB input format file for a symmetric case.",
    )
    cparser.add_argument(
        "--atspinput",
        required=False,
        metavar="atspinputfile",
        type=str,
        help="TSPLIB input format file for a asymmetric case.",
    )
    cparser.add_argument("--output", required=True, metavar="outputfile", type=str, help="TSPLIB output format file.")

    # Execute the parse_args() method
    args = cparser.parse_args()

    # Show selected input
    print("Input tsp file   : {}".format(args.tspinput))
    print("Input atsp file  : {}".format(args.atspinput))
    print("Output file      : {}".format(args.output))

    if args.tspinput:
        # Load input file and run Concorde
        solver = TSPSolver.from_tspfile(args.tspinput)

        # Access the optimal tour
        tour_data = solver.solve()

        # Print optimal tour
        print(tour_data.tour)

        with open(args.output, "w") as f:
            for stop in tour_data.tour:
                f.write(f"{stop}\n")
    elif args.atspinput:
        result = np.array(
            [
                [
                    0,
                    1,
                    2
                ],
                [6, 0, 3],
                [5, 4, 0],
            ]
        )

        print(result)

        conv = ATSPConvert(result)

        conv.as_symmetric()

        problem = Problem.from_matrix(conv.get_cost_matrix())

        problem.to_tsp("atsp.tsp")

        print(conv.get_cost_matrix())

        # Load input file and run Concorde
        solver = TSPSolver.from_tspfile("atsp.tsp")

        # Access the optimal tour
        tour_data = solver.solve()

        # Print optimal tour
        print(tour_data.tour)

        with open(args.output, "w") as f:
            for stop in tour_data.tour:

                f.write(f"{stop}\n")
            else:
                print("No input files")


if __name__ == "__main__":
    main()