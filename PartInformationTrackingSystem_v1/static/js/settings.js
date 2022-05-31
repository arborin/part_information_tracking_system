
$("[id^='saveScaleSettings-']").click(function(){
    
    let id = this.id.split('-')[1];

    var data = {
        "scale_id" : id,
        "scale_ip" : $("#scaleIpInput-"+id).val(),
        "scale_port" : $("#scalePortInput-"+id).val()
    };
    
    console.log(data);

    $.post('/settings/scale', data )
});

$("#saveDBSettings").click(function(){
    
    var data = {
        "database_ip" : $("#databaseIPInput").val(),
        "database_port" : $("#databasePortInput").val(),
        "database_user" : $("#databaseUserInput").val(),
        "database_password": $("#databasePasswordInput").val()
    };
    
    $.post('/settings/db', data ).done(function( data ) {
        if(data == 'OK'){
            $('#toggleDbSettings').click(); 
            alertify.success("Success!")
        }else{
            alertify.error("Failed...")
        }
    });
    
    
});

$("#checkScaleConnection").click(function(){
    var data = {
        "scale_ip": $("#scaleIpInput").val(),
        "scale_port": $("#scalePortInput").val()
    }
    $.post('/settings/scale/checkconnection', data, function(data, status, xhr){
        alert(xhr.responseText);
        
    });
});

$("#checkDBConnection").click(function(){
    var data = {
        "db_ip" : $("#databaseIPInput").val(),
        "db_port" : $("#databasePortInput").val(),
        "db_user" : $("#databaseUserInput").val(),
        "db_password": $("#databasePasswordInput").val()
    };
    $.post('/settings/db/checkconnection', data, function(data, status, xhr){
        alert(xhr.responseText); 

    });
});

$('#saveCameraSettings').click(saveCameraSettings);

function saveCameraSettings(){
    var data = {
        'com_port':$('#ComPortInput').val(),
        'baud_rate':$('#BaudRateInput').val(),
        'byte_size':$('#BiteSizeInput').val(),
        'stop_bits':$('#StopBitsInput').val(),
        'parity':$('#ParityInput').val(),
        'flow_control':$('#FlowControlInput').val()
    };
    $.post('/settings/camera',data, saveCameraSettingsCallback);
}
function saveCameraSettingsCallback(data, status, xhr){
    alert('Settings Saved')
};

$('#checkCameraConnection').click(function(){
    saveCameraSettings();
    $.post('/settings/camera/checkconnection', null, checkCameraConnectionCallback);
})

function checkCameraConnectionCallback(data, status, xhr){
    alert(xhr.responseText);
}


$(document).ready(function () {
    console.log("Ready ...");
    
    $("#toggleDbSettings").change(function() {
        if(this.checked) {
            $("#databaseIPInput").prop("disabled", false);
            $("#databasePortInput").prop("disabled", false);
            $("#databaseUserInput").prop("disabled", false);
            $("#databasePasswordInput").prop("disabled", false);
            
            // ENABLE SAVE BTN
            $("#saveDBSettings").prop('disabled', false);
            
        }else{
            $("#databaseIPInput").prop("disabled", true);
            $("#databasePortInput").prop("disabled", true);
            $("#databaseUserInput").prop("disabled", true);
            $("#databasePasswordInput").prop("disabled", true);
            
            // DISABLE SAVE BTN
            $("#saveDBSettings").prop('disabled', true);
        }
    });
});