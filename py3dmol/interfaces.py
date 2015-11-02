from py3dmol.backend_3dmol import JS3DMol
from py3dmol import utils


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
        """TODO:don't use a temporary file!"""
        fname ='/tmp/temp%s.pdb'%self.id
        self.mol.atoms.write(fname)
        with open(fname,'r') as infile:
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
    """
    TODO: cclib doesn't return the name of the basis, just the parameters if it can find them. If we can figure out that we're using, e.g., 6-31g**, we should be able to reconstruct that ourselves?
    """
    def __init__(self,*args,**kwargs):
        super(CCLibViz,self).__init__(*args,**kwargs)
        self.basis = self.build_basis()

    def build_basis(self):
        """TODO: deal with multiple coordinates and orbitals. For now, take the last one of each
        TODO: lose the pyquante dependency?"""
        gbasis = self.mol.gbasis
        coords = self.mol.atomcoords[-1]
        assert len(self.mol.atomnos) == len(gbasis)
        self.bfs = utils.CCLibBasis(gbasis,coords)


    def get_input_file(self):
        coords = self.mol.atomcoords[-1]
        outfile = [' %d \ncomment line'%len(coords)]
        for atnum,pos in zip(self.mol.atomnos,coords):
            outfile.append('%s %f %f %f'%(utils.elements[atnum],
                                          pos[0],pos[1],pos[2]))
        return '\n'.join(outfile),'xyz'

    def calc_orb_grid(self,orbnum,npts=50):
        bbox = utils.bbox(self.mol.atomcoords[-1])
        grid = utils.VolumetricGrid(*bbox,npoints=npts)
        orb = self.mol.mocoeffs[-1][:,orbnum]
        return utils.calc_orbvals(grid,orb,self.bfs)

    @property
    def homo(self):
        return self.mol.homos[-1]



class PyQuante2Viz(JS3DMol):
    """This takes a pyquante2 solver """
    def __init__(self,*args,**kwargs):
        super(PyQuante2Viz,self).__init__(*args,**kwargs)
        if kwargs.get('display',True): #because we don't get bonds by default (?)
            self.set_style('sphere',radius=0.3)

    def get_input_file(self):
        from cStringIO import StringIO
        fobj = StringIO()
        self.mol.geo.xyz(fobj=fobj)
        xyzfile = fobj.getvalue()
        fobj.close()
        try: #use pybel to assign bonds if available
            import pybel as pb
        except ImportError:
            return xyzfile,'xyz'
        else:
            pbmol = pb.readstring('xyz',xyzfile)
            sdffile = pbmol.write('sdf')
            return sdffile,'sdf'

    def calc_orb_grid(self,orbnum,npts=50):
        grid = utils.VolumetricGrid( *self.mol.geo.bbox(),
                                      npoints=npts)
        orb = self.mol.orbs[:,orbnum]
        return utils.calc_orbvals(grid,orb,self.mol.bfs)

    @property
    def homo(self):
        return self.mol.geo.nel()/2 - 1


