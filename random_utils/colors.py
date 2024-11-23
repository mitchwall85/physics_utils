import matplotlib.pyplot as plt


def generate_shades(n, base_color):
    # Generate n shades of blue using the 'Blues' colormap
    """generate shades of a base color

    Args:
        n (_type_): number of shades to generate
        base_color (_type_): 4 length tuple representing the base color

    Returns:
        _type_: list of shades
    """
    # examples 
    # base_blue = (0.0, 0.0, 1.0, 1.0)
    # base_green = (0.0, 1.0, 0.0, 1.0) 
    # base_red = (1.0, 0.0, 0.0, 1.0) 
    
    # Generate n shades of blue with varying opacity
    if n == 1:
        shades = [base_color]
    else:
        shades = [(base_color[0], base_color[1], base_color[2], 0.2 + 0.8 * (i / (n - 1))) for i in range(n)]
    
    return shades

def generate_jet_colors(n):
    # Get the 'jet' colormap from matplotlib
    cmap = plt.get_cmap('jet')
    
    # Generate n colors from the jet colormap
    if n == 1:
        jet_colors = [cmap(0.5)]
    else:
        jet_colors = [cmap(i / (n - 1)) for i in range(n)]
    
    return jet_colors
