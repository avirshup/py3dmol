import uuid
import json
from IPython.display import Javascript,HTML
import IPython.display as ipyd
from ipywidgets import IntSlider,interactive, Box

JSURL = 'http://3dmol.csb.pitt.edu/build/3Dmol.js'
#JSURL = '3dmol_build/3Dmol.js'
try: _imported_3dmol
except NameError:  #try to only import 3dmol.js once
    importer = HTML('<head><script src="%s"></script></head>'%JSURL)
    ipyd.display(importer)
    _imported_3dmol = True


class JS3DMol(object):
    STYLES = 'stick line cross sphere cartoon VDW MS'.split()

    def __init__(self,mol,width='500px',height='300px',
                 div_id=None,display=True):
        self.mol = mol
        if div_id is None: div_id = uuid.uuid4()
        self.id = div_id
        
        molstring,format = self.get_input_file()

        self.width = width
        self.height = height
        self.html = HTML_HEADER%(self.id,self.id,format,
                                 self.id,self.id,
                                 width,height,self.id,
                                 molstring)
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

    def add_frame(self,positions=None):
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

    def set_style(self,style=None,atomselection=None,**spec):
        if spec is None: spec={}
        if style not in self.STYLES:
            raise KeyError('Style keys: %s'%(', '.join(self.STYLES)))
        if atomselection:
            atomselection = self._atoms_to_json(atomselection)
        else:
            atomselection = '{}'
        code = "myviewer.setStyle(%s,{%s:%s});"%(atomselection,style,spec)
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


class MdaViz(JS3DMol):
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


class PybelViz(JS3DMol):
    @staticmethod
    def _atoms_to_json(atomlist):
        idxes = [a.idx for a in atomlist]
        atomsel = {'serial':idxes.tolist()}
        return atomsel

    def get_input_file(self):
        instring = self.mol.write('pdb')
        return instring,'pdb'
        


import os
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
with open('%s/callbacks.js'%dir_path,'r') as infile:
    callbackjs = infile.read()


HTML_HEADER = """ <head></head>
<script>""" + callbackjs +"""
</script>
</head>
<body>
<script>
	$(document).ready(function() {

		moldata = data = $("#%s_data").val();
		glviewer = $3Dmol.createViewer("%s", {
			defaultcolors : $3Dmol.rasmolElementColors
		});
		glviewer.setBackgroundColor(0xffffff);

		receptorModel = glviewer.addModel(data, "%s",{'keepH':true});

		glviewer.zoomTo();
                glviewer.setStyle({},{'stick':{}});
		glviewer.render();

        $3Dmol.viewers['%s']=glviewer;
		})

    //callback function to set atom positions (for creating a new frame)
	function positionUpdate(atom,index,atomlist){
        atom.x = tempx[index];atom.y=tempy[index];atom.z=tempz[index];
	}
</script>
<div id="%s" style="width: %s; height:%s"></div>

<textarea style="display: none;" id="%s_data">
%s</textarea>
</body>
"""
