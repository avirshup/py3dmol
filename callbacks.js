
function zip(arrays) {
    return arrays[0].map(function(_,i){
        return arrays.map(function(array){return array[i]})
    });
}

function move_and_render(viewer, atomSelection, positionList){
    var oldatoms = viewer.selectedAtoms(atomSelection);
    var newatoms = Array( oldatoms.length );
    for (i = 0; i < oldatoms.length; i++) {
	var atom = jQuery.extend({},oldatoms[i]);
        atom.x = positionList[i][0];
        atom.y = positionList[i][1];
        atom.z = positionList[i][2];
	newatoms[i] = atom;
    }
    var model = viewer.getModel(0);
    model.addFrame(newatoms);
    viewer.setFrame( viewer.getFrames() );
    viewer.render();
}

