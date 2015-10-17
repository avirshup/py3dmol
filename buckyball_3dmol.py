import uuid

from IPython.display import Javascript,HTML
import IPython.display as ipyd

#    HTML_HEADER = infile.read()

#with open('3dmol.draggable.js') as infile:
#    DRAGGABLE = infile.read()

#TODO: make sure 3dmol.js is loaded exactly once

class JS3DMol(object):
    STYLES = 'stick line cross sphere cartoon VDW MS'.split()

    def __init__(self,mol,width='800px',height='600px',
                 div_id=None,display=True):
        if div_id is None:
            div_id = uuid.uuid4()
        self.mol = mol
        self.id = div_id
        self.width = width
        self.height = height
        molstring = mol.write(format='sdf')
        self.html = HTML_HEADER%(self.id,self.id,self.id,self.id,
                                 width,height,self.id,
                                 molstring)
        self.display_object = HTML(self.html)
        self.commands = []
        if display: self.display()

    def display(self):
        ipyd.display(self.display_object)

    def __repr__(self):
        return self.display_object

    def set_style(self,atomselection=None,style=None,spec=None):
        if spec is None: spec={}
        if style not in self.STYLES:
            raise KeyError('Style keys: %s'%(', '.join(self.STYLES)))
        if atomselection:
            atomselection = self._atoms_to_json(atomselection)
        else:
            atomselection = '{}'
        code = "myviewer.setStyle(%s,{%s:%s,'stick':{}});"%(atomselection,style,spec)
        self.run_js(code)

    def center(self): self.run_js('myviewer.zoomTo();')

    def move_atom(self,atom,newcoords):
        code = """var atom = myviewer.selectedAtoms({'serial':%d})[0];
        atom.x=%f;
        atom.y=%f;
        atom.z=%f;
        myviewer.setStyle({'serial':%d},{'sphere':{'radius':0.75}});
        """%(atom.idx,newcoords[0],newcoords[1],newcoords[2],atom.idx)
        self.run_js(code)


    def run_js(self,code,render=True):
        snippet= ["var myviewer = $3Dmol.viewers['%s'];"%self.id,
                  code]
        if render:
            snippet.append("myviewer.render();")

        command = '\n'.join(snippet)
        self.commands.append(command)
        ipyd.display(Javascript(command))


    @staticmethod
    def _atoms_to_json(atoms):
        idxlist = [atom.idx for atom in atoms]
        atomsel = {'serial':idxlist}
        return atomsel

    def add_frame(self,mol=None,show=True):
        if mol is None: mol=self.mol
        positions = ['tempx=%s;'%str(mol.positions[:,0].tolist()),
                     'tempy=%s;'%str(mol.positions[:,1].tolist()),
                     'tempz=%s;'%str(mol.positions[:,2].tolist())]

        code = [positions,
                'model = glviewer.getModel(0);',
                'atoms = glviewer.selectAtoms();',
                'atoms.forEach(positionUpdate);']

        if show: pass
        self.run_js(code='\n'.join(code),render=False)


    def simulate_live(self,steps_per_update=1,
                      snapshots=None,total_steps=float('inf'),
                      method='propagate'):
        nsteps = 0
        propagator = getattr(self.mol,method)
        while nsteps < total_steps:
            propagator(nsteps = steps_per_update)
            if snapshots is not None:
                snapshots.store(self.mol)
        self.add_frame(self.mol,show=True)



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

		receptorModel = glviewer.addModel(data, "sdf");

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
