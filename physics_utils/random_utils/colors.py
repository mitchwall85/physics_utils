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

def generate_cmap_colors(n, cmap):
    """Return n evenly spaced colors across a Matplotlib colormap."""
    cmap_obj = plt.get_cmap(cmap)

    if n <= 0:
        return []

    if n == 1:
        return [cmap_obj(0.0)]

    upper = 0.90
    return [cmap_obj(i * upper / (n - 1)) for i in range(n)]


def generate_jet_colors(n):
    """Return n evenly spaced colors across the useful jet color range."""
    return generate_cmap_colors(n, 'jet')
