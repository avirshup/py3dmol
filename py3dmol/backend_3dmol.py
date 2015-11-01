import uuid
import json
from cStringIO import StringIO

from IPython.display import Javascript,HTML
import IPython.display as ipyd
from ipywidgets import IntSlider,interactive

from py3dmol import renderables

try: _imported_3dmol
except NameError:  #try to only import 3dmol.js once
    importer = HTML('<head><script>%s</script></head>'%renderables.javascript_library)
    ipyd.display(importer)
    _imported_3dmol = True



class JS3DMol(object):
    """ This is the main class for the 3DMol.js backend.
    The _atoms_to_json static method and get_input_file
    instancemethods need to be implemented by subclasses.
    """
    STYLES = 'stick line cross sphere cartoon VDW MS'.split()

    def __init__(self,mol,width='500px',height='300px',
                 div_id=None,display=True):
        self.mol = mol
        if div_id is None: div_id = uuid.uuid4()
        self.id = div_id
        
        molstring,format = self.get_input_file()
        self.width = width
        self.height = height
        self.html = renderables.viewer_html(self.id,format,width,height,molstring)
        self.display_object = HTML(self.html)
        self.commands = []
        self.nframes = 1
        if display: self.display()

    def get_input_file(self):
        """OVERRIDE IN SUBCLASSES"""
        string,format=None,None
        return string,format

    def display(self):
        ipyd.display(self.display_object)

    def add_frame(self,positions=None,annotation=None):
        if positions is None:
            positions = self.get_current_positions() #implement in subclasses
        try:
            jspos = json.dumps(positions.tolist())
        except AttributeError:
            jspos = json.dumps(positions)
        snippet = 'var jspos = %s;\nmove_and_render(myviewer,{},jspos);'%jspos
        self.run_js(snippet)
        self.nframes += 1
        return self.nframes-1

    def show_frame(self,framenum):
        self.run_js('myviewer.setFrame(%d);'%framenum)

    def set_style(self,style=None,atoms=None,**spec):
        if spec is None: spec={}
        if style not in self.STYLES:
            raise KeyError('Style keys: %s'%(', '.join(self.STYLES)))
        if atoms:
            atoms = self._atoms_to_json(atoms)
        else:
            atoms = '{}'
        code = "myviewer.setStyle(%s,{%s:%s});"%(atoms,style,spec)
        self.run_js(code)

    def center(self):
        self.run_js('myviewer.zoomTo();')

    def run_js(self,code,render=True):
        snippet= ["var myviewer = $3Dmol.viewers['%s'];"%self.id,
                  code]
        if render:
            snippet.append("myviewer.render();")
        command = '\n'.join(snippet)
        self.commands.append(command)
        ipyd.display(Javascript(command))

    @staticmethod
    def _atoms_to_json(atomgroup):
        "OVERRIDE IN SUBCLASSES"
        atomsel = {'serial':(atomgroup.indices+1).tolist()}
        return atomsel

    def create_controls(self):
        raise NotImplementedError()

    def animate(self):
        def slide(frame):
            self.show_frame(frame)
        s = IntSlider(min=0, max=self.nframes-1,value=0)
        slider = interactive(slide, frame=s)
        ipyd.display(slider)

    def show_orb(self,orbname,npts=50,isoval=0.01,
                 opacity=0.95,negative_color='red',
                 positive_color='blue'):
        """show a molecular orbital
        calc_orb_grid must be implemented in subclass
        TODO: is caching cube files a good idea? cache in JS?
        TODO: need to keep track of orbital shape objects se we don't need removeAllShapes"""
        orbidx = self.get_orbidx(orbname)
        voldata = self.get_voldata(orbidx, npts)

        js = """var volData = myviewer.pyObjects['%s'] ;
        myviewer.removeAllShapes();
        myviewer.addIsosurface(volData,{isoval: %f, color: "%s", opacity: %f});
        myviewer.addIsosurface(volData,{isoval: %f, color: "%s", opacity: %f});
        myviewer.render();"""%(
            voldata.id,
            -isoval, negative_color, opacity,
            isoval, positive_color, opacity)
        self.run_js(js)

    def get_orbidx(self, orbname):
        try:
            if orbname.lower().strip() == 'homo':
                orbname = self.homo_index()
            elif orbname.lower().strip() == 'lumo':
                orbname = self.homo_index() + 1
        except AttributeError:
            pass
        return orbname

    def get_voldata(self, orbname, npts):
        if not hasattr(self, 'cached_voldata'): self.cached_voldata = {}
        if (orbname, npts) not in self.cached_voldata:
            grid = self.calc_orb_grid(orbname, npts)
            cubefile = self._grid_to_cube(grid)
            volume_data = self.read_cubefile(cubefile)
            self.cached_voldata[orbname, npts] = volume_data
        return self.cached_voldata[orbname,npts]

    def read_cubefile(self,cubefile):
        volume_data = ViewerObject()
        js = """var cubefile = `%s`;
        myviewer.pyObjects['%s'] = new $3Dmol.VolumeData(cubefile,"cube");
        """%(cubefile,volume_data.id)
        self.run_js(js,False)
        return volume_data

    @staticmethod
    def _grid_to_cube(grid,f=None):
        if f is None:
            fobj = StringIO()
        elif not hasattr(f,'write'):
            fobj = open(f,'w')
        else:
            fobj = f

        #First two header lines
        print>>fobj,'CUBE File\nGenerated by py3dmol'
        #third line: number of atoms (0, here) + origin of grid
        print>>fobj,'-1 %f %f %f'%grid.origin()
        #lines 4-7: number of points in each direction and basis vector for each
        #basis vectors are negative to indicate angstroms
        print >> fobj,'%d %f 0.0 0.0' %(-grid.npoints,grid.dx)
        print >> fobj,'%d 0.0 %f 0.0' %(-grid.npoints,grid.dy)
        print >> fobj,'%d 0.0 0.0 %f' %(-grid.npoints,grid.dz)
        #Next is a line per atom
        #We put just one atom here - it shouldn't be rendered
        print >> fobj,'6 0.000 0.0 0.0 0.0'
        #Next, indicate that there's just one orbital
        print >> fobj,1,1
        #finally, write out all the grid values
        ival = 0
        for ix in xrange(grid.npoints):
            for iy in xrange(grid.npoints):
                for iz in xrange(grid.npoints):
                    print >> fobj,grid.fxyz[ix,iy,iz],
                    #ival += 1
                    #if ival%6 == 0: print >> fobj #newline
                    if iz%6==5: print >> fobj
                print >> fobj

        if f is None:
            fobj.seek(0)
            return fobj.getvalue()
        else:
            fobj.close()




class ViewerObject(object):
    """This is a convenient python reference to a javascript object.
    Really, it just stores a string"""
    def __init__(self,objid=None):
        if objid is None:
            self.id = uuid.uuid4()
        else:
            self.id = objid