import uuid
import json
import mdanalysis as mda
from IPython.display import Javascript,HTML
import IPython.display as ipyd

load_script = HTML('<head><script src="http://3Dmol.csb.pitt.edu/build/3Dmol.js"></script></head>')
ipyd.display(load_script)

class JS3DMol(object):
    STYLES = 'stick line cross sphere cartoon VDW MS'.split()

    def __init__(self,universe,width='800px',height='600px',
                 div_id=None,display=True):
        if div_id is None:
            div_id = uuid.uuid4()
        self.u = universe
        self.id = div_id
        self.width = width
        self.height = height
        self.u.atoms.write('temp%s.pdb'%div_id)
        with open('temp%s.pdb'%div_id,'r') as infile:
            molstring = infile.read()
        self.html = HTML_HEADER%(self.id,self.id,self.id,self.id,
                                 width,height,self.id,
                                 molstring)
        self.display_object = HTML(self.html)
        self.commands = []
        if display: self.display()

    def display(self):
        ipyd.display(self.display_object)

    def set_positions(self,positions):
        jspos = json.dumps(positions.dumps.tolist())
        snippet = 'jspos = %s\nmove_and_render(myviewer,jspos)'%jspos


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
        atomsel = {'serial':(atomgroup.indices+1).tolist()}
        return atomsel






HTML_HEADER = """
<head>
</head>
<body>
<script>
	$(document).ready(function() {


		moldata = data = $("#%s_data").val();
		glviewer = $3Dmol.createViewer("%s", {
			defaultcolors : $3Dmol.rasmolElementColors
		});
		glviewer.setBackgroundColor(0xffffff);

		receptorModel = glviewer.addModel(data, "pdb");

		glviewer.zoomTo();
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
