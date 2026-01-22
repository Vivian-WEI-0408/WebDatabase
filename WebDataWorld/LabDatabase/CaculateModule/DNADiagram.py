import dnaplotlib as dpl
from io import BytesIO
import matplotlib as plt

def get_plasmid_diagram(plasmid_dict):
    renderer = dpl.Renderer()
    
    reg_renderer = dpl.RegulatorRenderer(renderer)
    part_renderer = dpl.PartRenderer(renderer)
    
    fig, ax = renderer.create_figure(width = 800, height = 200)
    reg_renderer.render(ax, plasmid_dict)
    part_renderer.render(ax, plasmid_dict)
    
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png', dpi = 150, bbox_inches = "tight")
    plt.close(fig)
    img_buffer.seek(0)
    
    return img_buffer