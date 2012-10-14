var shoutbox_last_token = null;
var shoutbox_current_coloring = 'c1';

function shoutbox_enter() {
    $.ajax('/profile/ajax/shout/', {
        data: {
            content: $('#shoutbox input').val()
        },
        type: 'POST',
        success: function() { shoutbox_refresh(); }
    });
    $('#shoutbox input').val('');
}

function shoutbox_refresh() {
    var data = {};
    if (shoutbox_last_token != null) data = {since: shoutbox_last_token};
        
        $.ajax('/profile/ajax/ask/', {
            data: data,
            dataType: 'json',
            type: 'GET',
            success: function(data) {                
                var suggested_last_token = data[0];
                data = data[1];
                if (data != null) {
                    shoutbox_last_token = suggested_last_token;
                    for (var i=0; i<data.length; i++) {
                        var x = '<div class="shout '+shoutbox_current_coloring+'">'+$('<div/>').text(data[i][1]).html()+'<div class="stats">'+data[i][0]+' '+data[i][2]+'</div></div>';
                        shoutbox_current_coloring = (shoutbox_current_coloring == 'c1') ? 'c2' : 'c1';
                        $('#shoutbox_input_container').after(x);
                        while ($('#shoutbox .shout').length > 10) $('#shoutbox .shout').last().remove();
                    }
                }
                setTimeout("shoutbox_refresh()", 5000);
            }
        });
}

function shoutbox_load() {
    shoutbox_refresh();
    $('#shoutbox input').keyup(function(e) {
        if (e.keyCode == 13) shoutbox_enter();
    }).focus(function() { $('#shoutbox input').val(''); })
}