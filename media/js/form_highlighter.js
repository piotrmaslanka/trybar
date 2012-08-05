function highlight_input(e) {
    $(e.target).parent().css("background", "url('/media/gfx/field_p.png') no-repeat");
}

function unhighlight_input(e) {
    $(e.target).parent().css("background", "url('/media/gfx/field.png') no-repeat");
}