import numpy as np

from py3dmol.backend_3dmol import JS3DMol
from py3dmol.common import VolumetricGrid


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


class PyQuante2Viz(JS3DMol):
    """This takes a pyquante2 solver """
    def __init__(self,*args,**kwargs):
        super(PyQuante2Viz,self).__init__(*args,**kwargs)
        if kwargs.get('display',True):
            self.set_style('sphere',radius=0.3)

    def get_input_file(self):
        from cStringIO import StringIO
        fobj = StringIO()
        self.mol.geo.xyz(fobj=fobj)
        xyzfile = fobj.getvalue()
        fobj.close()
        return xyzfile,'xyz'

    def calc_orb_grid(self,orbnum,npts=50):
        """Taken from the vieworb function pyquante2.graphics.mayavi"""
        grid = VolumetricGrid( *self.mol.geo.bbox(),
                              npoints=npts)
        x, y, z = grid.xyzlist()
        orb = self.mol.orbs[:,orbnum]

        for c,bf in zip(orb,self.mol.bfs):
            grid.fxyz += c*bf(x, y, z)
        return grid

    @property
    def homo(self):
        return self.mol.geo.nel()/2 - 1

