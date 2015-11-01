import numpy as np


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




