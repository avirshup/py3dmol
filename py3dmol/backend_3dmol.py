import uuid
import json

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

