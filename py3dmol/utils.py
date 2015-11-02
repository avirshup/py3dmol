import numpy as np
import pyquante2

ANGSTROM_PER_BOHR = 0.5291772616368011
BOHR_PER_ANGSTROM = 1.8897259434513847

atomic_numbers = {'Ac': 89, 'Ag': 47, 'Al': 13, 'Am': 95, 'Ar': 18, 'As': 33, 'At': 85, 'Au': 79,
                  'B': 5, 'Ba': 56, 'Be': 4, 'Bh': 107, 'Bi': 83, 'Bk': 97, 'Br': 35, 'C': 6,
                  'Ca': 20, 'Cd': 48, 'Ce': 58, 'Cf': 98, 'Cl': 17, 'Cm': 96, 'Cn': 112, 'Co': 27,
                  'Cr': 24, 'Cs': 55, 'Cu': 29, 'Db': 105, 'Ds': 110, 'Dy': 66, 'Er': 68, 'Es': 99,
                  'Eu': 63, 'F': 9, 'Fe': 26, 'Fm': 100, 'Fr': 87, 'Ga': 31, 'Gd': 64, 'Ge': 32,
                  'H': 1, 'He': 2, 'Hf': 72, 'Hg': 80, 'Ho': 67, 'Hs': 108, 'I': 53, 'In': 49, 'Ir': 77,
                  'K': 19, 'Kr': 36, 'La': 57, 'Li': 3, 'Lr': 103, 'Lu': 71, 'Md': 101, 'Mg': 12,
                  'Mn': 25, 'Mo': 42, 'Mt': 109, 'N': 7, 'Na': 11, 'Nb': 41, 'Nd': 60, 'Ne': 10,
                  'Ni': 28, 'No': 102, 'Np': 93, 'O': 8, 'Os': 76, 'P': 15, 'Pa': 91, 'Pb': 82,
                  'Pd': 46, 'Pm': 61, 'Po': 84, 'Pr': 59, 'Pt': 78, 'Pu': 94, 'Ra': 88, 'Rb': 37,
                  'Re': 75, 'Rf': 104, 'Rg': 111, 'Rh': 45, 'Rn': 86, 'Ru': 44, 'S': 16, 'Sb': 51,
                  'Sc': 21, 'Se': 34, 'Sg': 106, 'Si': 14, 'Sm': 62, 'Sn': 50, 'Sr': 38, 'Ta': 73,
                  'Tb': 65, 'Tc': 43, 'Te': 52, 'Th': 90, 'Ti': 22, 'Tl': 81, 'Tm': 69, 'U': 92,
                  'Uuh': 116, 'Uuo': 118, 'Uup': 115, 'Uuq': 114, 'Uus': 117, 'Uut': 113, 'V': 23,
                  'W': 74, 'Xe': 54, 'Y': 39, 'Yb': 70, 'Zn': 30, 'Zr': 40}

elements = {atnum:el for el,atnum in atomic_numbers.iteritems()}


def bbox(coords,padding=5.,BIG=1e12):
    """Return a bounding box for a molecule.
    Derived from pyquante2.geo.molecule.bbox"""
    xmin = ymin = zmin = BIG
    xmax = ymax = zmax = -BIG
    for x,y,z in coords:
        xmin = min(x,xmin)
        ymin = min(y,ymin)
        zmin = min(z,zmin)
        xmax = max(x,xmax)
        ymax = max(y,ymax)
        zmax = max(z,zmax)
    xmin,ymin,zmin = xmin-padding,ymin-padding,zmin-padding
    xmax,ymax,zmax = xmax+padding,ymax+padding,zmax+padding
    return xmin,xmax,ymin,ymax,zmin,zmax

class VolumetricGrid(object):
    def __init__(self,xmin,xmax,ymin,ymax,zmin,zmax,
                 npoints=None):
        self.xr = (xmin,xmax)
        self.yr = (ymin,ymax)
        self.zr = (zmin,zmax)
        if npoints is not None:
            self.make_grid(npoints)

    def xyzlist(self):
        stride = self.npoints*1j
        grids = np.mgrid[self.xr[0]:self.xr[1]:stride,
                        self.yr[0]:self.yr[1]:stride,
                        self.zr[0]:self.zr[1]:stride]
        return grids

    def origin(self):
        return (self.xr[0],self.yr[0],self.zr[0])

    def make_grid(self,npoints):
        self.npoints = npoints
        self.fxyz = np.zeros((npoints,npoints,npoints))
        self.dx = (self.xr[1]-self.xr[0]) / (float(npoints)-1)
        self.dy = (self.yr[1]-self.yr[0]) / (float(npoints)-1)
        self.dz = (self.zr[1]-self.zr[0]) / (float(npoints)-1)


class CCLibBasis(pyquante2.basisset):
    """Edited version of the superclass __init__ that supports cclib gbasis
    """
    def __init__(self,gbasis,coords):
        from pyquante2.basis.tools import sym2pow,sym2am,am2pow,am2sym
        self.bfs = []
        self.shells = []
        for atom_basis_function,pos in zip(gbasis,coords):
            for sym,prims in atom_basis_function:
                exps = [e for e,c in prims]
                coefs = [c for e,c in prims]
                self.shells.append(
                    pyquante2.basis.basisset.shell(sym2am[sym],
                                          pos*BOHR_PER_ANGSTROM,
                                          exps,coefs))
                for power in sym2pow[sym]:
                    self.bfs.append(
                        pyquante2.basis.cgbf.cgbf(
                            pos*BOHR_PER_ANGSTROM,
                            power,exps,coefs))


def calc_orbvals(grid,orb,bfs):
    """Derived from pyquante2.graphics.mayavi.vieworb"""
    x, y, z = grid.xyzlist()
    for c,bf in zip(orb,bfs):
        grid.fxyz += c*bf(x*BOHR_PER_ANGSTROM,
                          y*BOHR_PER_ANGSTROM,
                          z*BOHR_PER_ANGSTROM)
    return grid