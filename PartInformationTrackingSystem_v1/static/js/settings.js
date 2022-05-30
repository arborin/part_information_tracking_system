$("#saveScaleSettings").click(function(){
    var data = {
        "scale_ip" : $("#scaleIpInput").val(),
        "scale_port" : $("#scalePortInput").val()
    };
    //alert(data["scale_ip"]);
    $.post('/settings/scale', data )
});

$("#saveDBSettings").click(function(){
    var data = {
        "database_ip" : $("#databaseIPInput").val(),
        "database_port" : $("#databasePortInput").val(),
        "database_user" : $("#databaseUserInput").val(),
        "database_password": $("#databasePasswordInput").val()
    };
    $.post('/settings/db', data )
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