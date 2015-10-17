
function zip(arrays) {
    return arrays[0].map(function(_,i){
        return arrays.map(function(array){return array[i]})
    });
}

function move_and_render(viewer, atomSelection, positionList){
    atoms = viewer.SelectedAtoms(atomSelection);
    for (i = 0; i < atoms.length; i++) {
        pos = positionList[i];
        atom = atom[i];
        atom.x = pos[0];
        atom.y = pos[1];
        atom.z = pos[2];
    }

}

