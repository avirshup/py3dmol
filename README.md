#Py3DMol
Py3DMol is a python package for dependency-free molecular visualization in iPython notebooks. Objects from MDAnalysis, MDTraj, OpenBabel, and CClib can be visualized and manipulated directly in a notebook notebook. The backend visualization library, 3DMol.js, is included, so no additional libraries are necessary - visualizations will function in any modern browser using javascript and WebGL.

<img src="images/demo.png" width="200x" alt="Notebook image demo">

##About
This package started as hackathon project for the <a href="http://www.cecam.org/workshop-1214.html">CECAM 2015 Macromolecular Simulation Workshop.</a>

###Contributors
**Maintained by**:
Aaron Virshup, _Bio/Nano Research Group, Autodesk Research_<br>
<img src="http://www.autodeskresearch.com/img/title.gif" width="60x">

Kasia Ziolkowska, _Max Planck Institute_<br>
Tom Newport, _University of Oxford_<br>
Fiona Naughton,  _University of Oxford_<br>
Martin Vögele, _Max Planck Institute_

##Dependencies
This package is designed for the Jupyter Notebook platform and requires the ```ipython[notebook]``` and ```ipywidgets``` packages.

*Inclusions
- This packages uses the 3DMol.js library as a backend for molecular visualization - a minified version is included here. See <a href="http://3dmol.csb.pitt.edu/doc/index.html">3DMol.js</a>
- Several functions dealing with wavefunction math were derived from <a href="https://github.com/rpmuller/pyquante2">the PyQuante2 source code</a>.