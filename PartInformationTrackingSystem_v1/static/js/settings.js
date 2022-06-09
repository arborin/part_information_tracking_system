
$("[id^='saveScaleSettings-']").click(function(){
    
    let id = this.id.split('-')[1];

    var data = {
        "scale_id" : id,
        "scale_ip" : $("#scaleIpInput-"+id).val(),
        "scale_port" : $("#scalePortInput-"+id).val()
    };
    
    console.log(data);

    $.post('/settings/scale', data ).done(function( data ) {
        if(data == 'OK'){
            
            $(".connection-settings").prop("checked", false);
            $("#scaleIpInput-"+id).prop("disabled", true);
            $("#scalePortInput-"+id).prop("disabled", true);
            
            alertify.success("Success!")
        }else{
            alertify.error("Failed...")
        }
    });
    
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
        // alert(xhr.responseText); 
        alertify.success("Success")
    });
});



$('.saveCameraSettings').click(saveCameraSettings);

function saveCameraSettings(){
    
    let id = this.id.split('-')[1];
    

    var data = {
        'com_port': $('#ComPortInput-' + id).val(), 
        'baud_rate': $('#BaudRateInput-' + id).val(), 
        'byte_size': $('#BiteSizeInput-' + id).val(), 
        'stop_bits': $('#StopBitsInput-' + id).val(), 
        'parity': $('#ParityInput-' + id).val(), 
        'flow_control': $('#FlowControlInput-' + id).val(),
        'camera_id': id,
    };
    
    // POST ALL DATA
    $.post('/settings/camera',data, saveCameraSettingsCallback);
    
    // DISABLE ALL INPUTS
    $("#ComPortInput-"+id).prop("disabled", true);
    $("#BaudRateInput-"+id).prop("disabled", true);
    $("#BiteSizeInput-"+id).prop("disabled", true);
    $("#ParityInput-"+id).prop("disabled", true);
    $("#StopBitsInput-"+id).prop("disabled", true);
    $("#StopBitsInput-"+id).prop("disabled", true);
    $("#FlowControlInput-"+id).prop("disabled", true);
    
    $("#saveCameraSettings-"+id).prop("disabled", true);
}


function saveCameraSettingsCallback(data, status, xhr){
    let res = xhr.responseText
    if(res == 'OK'){ 
        alertify.success('Settings Saved')
    }else{
        alertify.error("Settings")
    }
   
};


$('#checkCameraConnection').click(function(){
    saveCameraSettings();
    $.post('/settings/camera/checkconnection', null, checkCameraConnectionCallback);
})


function checkCameraConnectionCallback(data, status, xhr){
    alert(xhr.responseText);
}


$(document).ready(function () {
    
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
    
    
    $(".connection-settings").change(function(){
        let id = this.id.split('-')[1];
        if(this.checked) {
            $("#scaleIpInput-"+id).prop("disabled", false);
            $("#scalePortInput-"+id).prop("disabled", false);
            $("#saveScaleSettings-"+id).prop("disabled", false);
        }else{
            $("#scaleIpInput-"+id).prop("disabled", true);
            $("#scalePortInput-"+id).prop("disabled", true);
            $("#saveScaleSettings-"+id).prop("disabled", true);
        }
    });
    
    
    $(".enable-camera-settings").change(function(){
        /*
            CAMERA SETTINGS CHECKBOX
        */
        let id = this.id.split('-')[1]; // id - ScaleA or ScaleB
        
        // alert(id);
    
        if(this.checked) {
            $("#ComPortInput-"+id).prop("disabled", false);
            $("#BaudRateInput-"+id).prop("disabled", false);
            $("#BiteSizeInput-"+id).prop("disabled", false);
            $("#ParityInput-"+id).prop("disabled", false);
            $("#StopBitsInput-"+id).prop("disabled", false);
            $("#StopBitsInput-"+id).prop("disabled", false);
            $("#FlowControlInput-"+id).prop("disabled", false);
            
            // ENABLE BUTTON
            $("#saveCameraSettings-"+id).prop("disabled", false);
        }else{
            $("#ComPortInput-"+id).prop("disabled", true);
            $("#BaudRateInput-"+id).prop("disabled", true);
            $("#BiteSizeInput-"+id).prop("disabled", true);
            $("#ParityInput-"+id).prop("disabled", true);
            $("#StopBitsInput-"+id).prop("disabled", true);
            $("#StopBitsInput-"+id).prop("disabled", true);
            $("#FlowControlInput-"+id).prop("disabled", true);
            
            $("#saveCameraSettings-"+id).prop("disabled", true);
        }
    });
    
    
   
});