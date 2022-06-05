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

$('.setActiveWeight').click(function(){
    // CHECK SCALE_A OR SCALE_B
    let id = this.id;
    
    // FIND SELECTED VALUE
    part_name = $("#selectActiveWeight"+id).val();
    
    // FIND ROW BY ID
    // ID EXAMPLE: ScaleA_PistonUpperPart_SOP1
    let row_id = id + "_" + part_name.replaceAll(' ','_')     
    row = $("#"+row_id);
    
    console.log(row);
    values = row.find('input')
    
    var data = {
        'scale': id,
        "part_name": values[0].value,
        "weight":values[1].value,
        "ll": values[2].value,
        'hl': values[3].value
    }
    
    console.log("-----------------------------------");
    console.log(data);
    console.log("-----------------------------------");
    $.post('/set_active_weight', data, checkWeightWasSet);
    

})


$(document).ready(function () {
    $(".saveWeights").click(function(){
        var data = []
        scale_id = this.id
        
        
        
        rows = $('.WeightRow'+scale_id);
        // console.log(scale_id);
        console.log(rows);
        
        rows.each(function(){
            inputs = $(this).find('input');
            // inputs = this.children;
            if (inputs[1].value != ''){
                data.push({
                    "part_name":inputs[1].value,
                    "part_number": inputs[2].value,
                    "weight":inputs[3].value,
                    "ll":inputs[4].value,
                    "hl": inputs[5].value,
                    "scale": scale_id
                });
            }
        })
        
        let send_data = {};
        send_data['weight'] = data;
        send_data['scale_id'] = scale_id;
        
        data = JSON.stringify(send_data);
        
        console.log(data);
        
        $.ajax({
            method: "POST",
            url:'/settings/weights',
            data : data,
            contentType:"application/json; charset=utf-8",
            success:reload
        } );
    });
});

function reload(){
    location.reload();
}

function checkWeightWasSet(data, status, xhr){
    resp = xhr.responseText;

    if(resp == 'NOK'){
        alertify.error("Connection Error...")
    }
    else{
        if( resp.includes('MH') && resp.includes('MH') && resp.includes('MM')){
            console.log('Weight was set');
            var res = data.split("#");
            $("#active_weight").text(res[1])
            
            alertify.error("Success")
        }
        else{
            console.log('Weight was not set');
        }
    }

};


$("#disableScaleB").click(function(){
    var data = {
        "active" : 0
    };
    $.post('/settings/scale/enable', data, function(data, status, xhr){
        if( xhr.responseText == "OK"){
            reload();
            alertify.success("OK");
        }else{
            alertify.error("Can not enable Scale B");
        }
    });
});

$("#enableScaleB").click(function(){
    var data = {
        "active" : 1
    };
    $.post('/settings/scale/enable', data, function(data, status, xhr){
        if( xhr.responseText == "OK"){
            reload();
            alertify.success("OK");
        }else{
            alertify.error("Can not enable Scale B");
        }
    });
});



