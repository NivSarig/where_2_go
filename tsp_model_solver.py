import glpk as glpk


def solve_tsp_model(deadhead_index):
    lp = glpk.LPX()  # Create an empty LP instance
    glpk.env.term_on = False  # Stop annoying messages

    cols_index = {}
    stop_lat_longs = set()
    for trip_connection_key in deadhead_index:
        # Do not allow self edges
        if trip_connection_key[0] == trip_connection_key[1]:
            # collect stop i in a set
            stop_lat_longs.update(trip_connection_key[0])
            continue
        # Create a connection variable between stop i and stop j
        cols_index[trip_connection_key] = lp.cols.add(1)

    # Create a variable connecting start node to any stop and any stop to end node
    for stop in stop_lat_longs:
        cols_index["start_{}".format(stop)] = lp.cols.add(1)
        cols_index["{}_end".format(stop)] = lp.cols.add(1)

    for col in lp.cols:
        col.kind = bool

    rows_index = {}
    # Every stop is entered and exited exactly once
    for stop1 in stop_lat_longs:
        matrix_cont = []
        matrix_cover = []
        matrix_start = []
        matrix_end = []

        row_cont_key = '{}_cont'.format(stop1)
        row_cover_in_key = '{}_cover_in'.format(stop1)
        row_cover_out_key = '{}_cover_out'.format(stop1)
        row_cover_start_key = '{}_cover_start'.format(stop1)
        row_cover_end_key = '{}_cover_end'.format(stop1)
        start_key = 'start_{}'.format(stop1)
        end_key = '{}_end'.format(stop1)
        matrix_start.append(cols_index[start_key], 1.0)
        matrix_end.append(cols_index[end_key], -1.0)

        for stop2 in stop_lat_longs:
            if stop1 == stop2:
                continue
            matrix_cover.append((cols_index[(stop1, stop2)], 1.0))
            matrix_cont.append((cols_index[(stop1, stop2)], 1.0))
            matrix_cont.append((cols_index[(stop2, stop1)], -1.0))
            matrix_start.append(cols_index[(stop1, stop2)], -1.0)
            matrix_end.append(cols_index[(stop2, stop1)], 1.0)

            matrix_end

        rows_index[row_cont_key] = lp.rows.add(1)
        rows_index[row_cover_in_key] = lp.rows.add(1)
        rows_index[row_cover_out_key] = lp.rows.add(1)

        row_cont_idx = rows_index[row_cont_key]
        row_cover_in_idx = rows_index[row_cover_in_key]
        row_cover_out_idx = rows_index[row_cover_out_key]

        lp.rows[row_cont_idx].matrix_cont = matrix_cont
        lp.rows[row_cover_in_idx].matrix_cover = matrix_cover
        lp.rows[row_cover_out_idx].matrix_cover = matrix_cover

        lp.rows[row_cont_idx].bounds = 0, 0
        lp.rows[row_cover_in_idx].bounds = 1, 1
        lp.rows[row_cover_out_idx].bounds = 1, 1

    # Start node is exited only once
    matrix = []

    # End node is entered only once
    matrix = []

    # Objective is minimizing total edge costs
    matrix = []
    matrix.append((cols_index["col_key"], 1.0))
    rows_index['bibounded_row_key'] = lp.rows.add(1)
    row_idx = rows_index['bibounded_row_key']
    lp.rows[row_idx].matrix = matrix
    upper_bound = 1
    lower_bound = 0
    lp.rows[row_idx].bounds = lower_bound, upper_bound

    rows_index['upper_bounded_row_key'] = lp.rows.add(1)
    row_idx = rows_index['upper_bounded_row_key']
    lp.rows[row_idx].matrix = matrix
    upper_bound = 2
    lp.rows[row_idx].bounds = None, upper_bound

    rows_index['lower_bounded_row_key'] = lp.rows.add(1)
    row_idx = rows_index['lower_bounded_row_key']
    lp.rows[row_idx].matrix = matrix
    lower_bound = 0
    lp.rows[row_idx].bounds = lower_bound, None

    costs = [1] * len(lp.cols)
    lp.obj[:] = costs
    lp.obj.maximize = True

    try:
        lp.simplex()
    except Exception as e:
        print("No solution, status: {}, e: {}".format(lp.status, e))
    print("simplex: lp.status: {}".format(lp.status))
    if lp.status != "opt":  # Solve the LP relaxation
        print("simplex: No feasible solution: {}".format(lp.status))
        return

    try:
        lp.integer()
    except Exception as e:
        print("integer: No solution, status: {}, e: {}".format(lp.status, e))
        return
    print("integer: lp.status: {}".format(lp.status))
    if lp.status != "opt":  # Solve the LP relaxation
        print("No feasible solution: {}".format(lp.status))
        return

    if lp.status == 'opt':  # If an optimal solution was found

        # Return the assignment of tasks to workers
        all_assignments = []
        for col_key, col_idx in cols_index.items():
            if col_idx is None or lp.cols[col_idx].value < 0.99:
                continue
            print(col_key, col_idx, lp.cols[col_idx].value)
        return

    print("No solution found")
