function img_hover(co,jak) {
		document.getElementById(co).src = "gfx/profil/" + co + jak + ".png";
	}
	
function msg_to(name) {
	document.getElementById("shadow").style.visibility = "visible";
	document.getElementById("msg_target").value = name;
}

function msg() {
	document.getElementById("shadow").style.visibility = "visible";
	document.getElementById("msg_target").value = "";
}

function hide() {
	document.getElementById("shadow").style.visibility = "hidden";
}