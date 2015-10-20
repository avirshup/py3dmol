import uuid
import json
import mdanalysis as mda
from IPython.display import Javascript,HTML
import IPython.display as ipyd

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
        if display: self.display()

    def get_input_file(self):
        """OVERRIDE IN SUBCLASSES"""
        string,format=None,None
        return string,format

    def display(self):
        ipyd.display(self.display_object)

    def set_positions(self,positions):
        try:
            jspos = json.dumps(positions.tolist())
        except AttributeError:
            jspos = json.dumps(positions)
        snippet = 'var jspos = %s;\nmove_and_render(myviewer,{},jspos);'%jspos
        self.run_js(snippet)


    def set_style(self,style=None,atomselection=None,spec=None):
        if spec is None: spec={}
        if style not in self.STYLES:
            raise KeyError('Style keys: %s'%(', '.join(self.STYLES)))
        if atomselection:
            atomselection = self._atoms_to_json(atomselection)
        else:
            atomselection = '{}'
        code = "myviewer.setStyle(%s,{%s:%s,'stick':{}});"%(atomselection,style,spec)
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


class MdaViz(JS3DMol):
    @staticmethod
    def _atoms_to_json(atomgroup):
        atomsel = {'serial':(atomgroup.indices+1).tolist()}
        return atomsel
    
    def get_input_file(self):
        self.mol.atoms.write('temp%s.pdb'%self.id)
        with open('temp%s.pdb'%self.id,'r') as infile:
            molstring = infile.read()
        return molstring,'pdb'

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

HTML_HEADER = """ <head><script src='3dmol_build/3Dmol.js'></script></head>
<script>""" + callbackjs +"""</script>
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
