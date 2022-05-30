function getWeight(){
    $.get("/get_weight", "", function(data, status, xhr){
        $("#logarea").text(xhr.responseText+ '\n' + $("#logarea").text().slice(0,4000));
    } );

}
// setInterval(getWeight, 1000);

$(document).ready(function () {
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

    //receive details from server
    socket.on('newnumber', function (msg) {
        console.log("Received number" + msg.number);

        // $('#log').html(numbers_string);
        $("#logarea").text(msg.number + '\n\n' + $("#logarea").text().slice(0, 4000));

    });

});

$('#setActiveWeight').click(function(){
    part_name = $("#selectActiveWeight").val();
    row = $('#row'+part_name.replace(' ','_'));
    values = row.find('input')
    var data = {
        "part_name": values[0].value,
        "weight":values[1].value,
        "ll": values[2].value,
        'hl': values[3].value
    }
    $.post('/set_active_weight', data, checkWeightWasSet)
})

$("#saveWeights").click(function(){
    var data = []
    rows = $('.weight-row');
    rows.each(function(){
        inputs = $(this).find('input');
        // inputs = this.children;
        data.push({
            "part_name":inputs[0].value,
            "weight":inputs[1].value,
            "ll":inputs[2].value,
            "hl": inputs[3].value
        });
    })
    data = JSON.stringify(data);
    $.ajax({
        method: "POST",
        url:'/settings/weights',
        data : data,
        contentType:"application/json; charset=utf-8",
        success:reload
    } );
})

function reload(){
    location.reload();
}

function checkWeightWasSet(data, status, xhr){
    resp = xhr.responseText;
    if( resp.includes('MH') && resp.includes('MH') && resp.includes('MM')){
        console.log('Weight was set');
        var res = data.split("#");
        $("#active_weight").text(res[1])
    }
    else{
        console.log('Weight was not set');
    }

};