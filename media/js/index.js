function nr_hover(co,gdzie) {
		document.getElementById("elem" + co).src = "gfx/index/" + co + gdzie + ".png";
	}
function lconfirm(msgbox, url) {
    if (confirm(msgbox))
        window.location = url;
}    