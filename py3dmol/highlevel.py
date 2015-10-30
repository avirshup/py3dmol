#High-level functions for the most common tasks

def show(obj):
    """
    Create a default visualization
    :param obj: 4-letter PDB code OR filename OR MDAnalysis object OR MDTraj object OR Pybel object or OpenBabel object or CCLib data
    :return type: py3dmol.vizinterfaces.JS3DMol
    """
    raise NotImplementedError()

#Some synonyms
visualize = viz = render = show