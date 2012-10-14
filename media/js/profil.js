function img_hover(co,jak) {
		document.getElementById(co).src = "/media/gfx/profil/" + co + jak + ".png";
	}
	
function msg_to(name) {
	var mrg = ($(window).height() - 499)/2;
	if (mrg<0) mrg=0;
    $('#msg_box').css('margin-top', ''+mrg+'px');
	document.getElementById("shadow").style.visibility = "visible";
	document.getElementById("msg_target").value = name;
}

function msg() {
	var mrg = ($(window).height() - 499)/2;
	if (mrg<0) mrg=0;
    $('#msg_box').css('margin-top', ''+mrg+'px');
	document.getElementById("shadow").style.visibility = "visible";
	document.getElementById("msg_target").value = "";
}

function hide() {
	document.getElementById("shadow").style.visibility = "hidden";
}