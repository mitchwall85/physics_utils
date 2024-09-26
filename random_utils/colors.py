def generate_blue_shades(n):
    # Generate n shades of blue using the 'Blues' colormap
    base_blue = (0.0, 0.0, 1.0, 1.0)  # RGBA: blue with full opacity
    
    # Generate n shades of blue with varying opacity
    if n == 1:
        blue_shades = [base_blue]
    else:
        blue_shades = [(base_blue[0], base_blue[1], base_blue[2], 0.2 + 0.8 * (i / (n - 1))) for i in range(n)]
    
    
    return blue_shades

def generate_jet_colors(n):
    # Get the 'jet' colormap from matplotlib
    cmap = plt.get_cmap('jet')
    
    # Generate n colors from the jet colormap
    jet_colors = [cmap(i / (n - 1)) for i in range(n)]
    
    return jet_colors
