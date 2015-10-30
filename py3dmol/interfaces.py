from py3dmol.backend_3dmol import JS3DMol

__author__ = 'aaronvirshup'


class PybelViz(JS3DMol):
    @staticmethod
    def _atoms_to_json(atomlist):
        idxes = [a.idx for a in atomlist]
        atomsel = {'serial':idxes.tolist()}
        return atomsel

    def get_input_file(self):
        instring = self.mol.write('pdb')
        return instring,'pdb'