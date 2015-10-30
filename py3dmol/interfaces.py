from py3dmol.backend_3dmol import JS3DMol

class PybelViz(JS3DMol):
    """Visualize a pybel molecule"""
    @staticmethod
    def _atoms_to_json(atomlist):
        idxes = [a.idx for a in atomlist]
        atomsel = {'serial':idxes.tolist()}
        return atomsel

    def get_input_file(self):
        instring = self.mol.write('pdb')
        return instring,'pdb'


class MdaViz(JS3DMol):
    """Visualize an MDAnalysis molecule"""
    def __init__(self,*args,**kwargs):
        super(MdaViz,self).__init__(*args,**kwargs)
        self.frame_map = {}
        self.frames_ready = False

    @staticmethod
    def _atoms_to_json(atomgroup):
        atomsel = {'serial':(atomgroup.indices+1).tolist()}
        return atomsel

    def get_current_positions(self):
        return self.mol.atoms.positions

    def get_input_file(self):
        self.mol.atoms.write('temp%s.pdb'%self.id)
        with open('temp%s.pdb'%self.id,'r') as infile:
            molstring = infile.read()
        return molstring,'pdb'

    def make_animation(self):
        traj = self.mol.universe.trajectory
        traj.rewind()
        for iframe,frame in enumerate(traj):
            framenum = self.add_frame()
            self.frame_map[iframe] = framenum
        self.frames_ready = True

class CCLibViz(JS3DMol):
    pass