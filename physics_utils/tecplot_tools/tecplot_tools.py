import numpy as np

def append_tecplot_var(var_vect, var_name, plt_file):
    # Load the new variable vector (ensure this is correct length)
    var_vect = np.loadtxt("var_vect.txt")  # or define manually

    # Read input .plt file
    with open(plt_file, "r") as f:
        lines = f.readlines()

    # Find line with VARIABLES
    var_line_index = next(i for i, line in enumerate(lines) if "VARIABLES" in line)
    variables = [v.strip().strip('"') for v in lines[var_line_index].split("=")[1].split(",")]

    # Add new variable to header
    variables.append(var_name)
    lines[var_line_index] = 'VARIABLES = ' + ', '.join(variables) + '\n'

    # Find start of data (after ZONE ...)
    zone_line_index = next(i for i in range(var_line_index + 1, len(lines)) if lines[i].strip().startswith("ZONE"))
    data_start_index = zone_line_index + 1

    # Read existing data
    data = np.loadtxt(lines[data_start_index:])

    # Sanity check
    if len(var_vect) != data.shape[0]:
        raise ValueError(f"Length of var_vect ({len(var_vect)}) doesn't match data rows ({data.shape[0]})")

    # Append new column
    data = np.column_stack([data, var_vect])

    # Write out new .plt file
    with open(f"field_{var_name}.plt", "w") as f:
        f.writelines(lines[:data_start_index])
        np.savetxt(f, data, fmt="%.6e")
