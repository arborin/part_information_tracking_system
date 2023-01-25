$("[id^='saveScaleSettings-']").click(function () {
    let id = this.id.split("-")[1];

    var data = {
        scale_id: id,
        scale_ip: $("#scaleIpInput-" + id).val(),
        scale_port: $("#scalePortInput-" + id).val(),
    };

    console.log(data);

    $.post("/settings/scale", data).done(function (data) {
        if (data == "OK") {
            $("#scaleSettings-" + id).click();

            $("#scaleIpInput-" + id).prop("disabled", true);
            $("#scalePortInput-" + id).prop("disabled", true);

            alertify.success("Success!");
        } else {
            alertify.error("Failed...");
        }
    });
});

$("#saveDBSettings").click(function () {
    var data = {
        database_ip: $("#databaseIPInput").val(),
        database_port: $("#databasePortInput").val(),
        database_user: $("#databaseUserInput").val(),
        database_password: $("#databasePasswordInput").val(),
    };

    $.post("/settings/db", data).done(function (data) {
        if (data == "OK") {
            $("#toggleDbSettings").click();
            alertify.success("Success!");
        } else {
            alertify.error("Failed...");
        }
    });
});

$(".checkScaleConnection").click(function () {
    let id = this.id.split("-")[1];

    var data = {
        scale_ip: $("#scaleIpInput-" + id).val(),
        scale_port: $("#scalePortInput-" + id).val(),
    };

    console.log(data);

    $.post(
        "/settings/scale/checkconnection",
        data,
        function (data, status, xhr) {
            let res = xhr.responseText;
            if (res == "OK") {
                $(".connection-settings").click();
                alertify.success("Success!");
            } else {
                alertify.error(res);
                console.log(res);
            }
        }
    );
});

$(".checkScaleConnection").click(function () {
    let id = this.id.split("-")[1];

    var data = {
        scale_ip: $("#scaleIpInput-" + id).val(),
        scale_port: $("#scalePortInput-" + id).val(),
    };

    console.log(data);

    $.post(
        "/settings/scale/checkconnection",
        data,
        function (data, status, xhr) {
            let res = xhr.responseText;
            if (res == "OK") {
                $(".connection-settings").click();
                alertify.success("Success!");
            } else {
                alertify.error(res);
                console.log(res);
            }
        }
    );
});

$(".checkCameraIpConnection").click(function () {
    var data = {
        camera_ip: $("#cameraIpInput").val(),
        camera_port: $("#cameraPort").val(),
    };

    console.log(data);

    $.post(
        "/settings/camera_ip/checkconnection",
        data,
        function (data, status, xhr) {
            let res = xhr.responseText;
            if (res == "OK") {
                $(".connection-settings").click();
                alertify.success("Success!");
            } else {
                alertify.error(res);
                console.log(res);
            }
        }
    );
});

$("#checkDBConnection").click(function () {
    var data = {
        db_ip: $("#databaseIPInput").val(),
        db_port: $("#databasePortInput").val(),
        db_user: $("#databaseUserInput").val(),
        db_password: $("#databasePasswordInput").val(),
    };

    console.log(data);

    $.post("/settings/db/checkconnection", data, function (data, status, xhr) {
        let res = xhr.responseText;

        if (res == "OK") {
            alertify.success("Success!");
        } else {
            alertify.error(res);
            console.log(res);
        }
    });
});

$(".saveCameraSettings").click(saveCameraSettings);

function saveCameraSettings() {
    var data = {
        com_port: $("#ComPortInput").val(),
        baud_rate: $("#BaudRateInput").val(),
        byte_size: $("#BiteSizeInput").val(),
        stop_bits: $("#StopBitsInput").val(),
        parity: $("#ParityInput").val(),
        flow_control: $("#FlowControlInput").val(),
    };

    // POST ALL DATA
    $.post("/settings/camera", data, saveCameraSettingsCallback);

    // DISABLE ALL INPUTS
    $("#ComPortInput").prop("disabled", true);
    $("#BaudRateInput").prop("disabled", true);
    $("#BiteSizeInput").prop("disabled", true);
    $("#ParityInput").prop("disabled", true);
    $("#StopBitsInput").prop("disabled", true);
    $("#StopBitsInput").prop("disabled", true);
    $("#FlowControlInput").prop("disabled", true);

    $("#saveCameraSettings").prop("disabled", true);
}

function saveCameraSettingsCallback(data, status, xhr) {
    let res = xhr.responseText;
    console.log(res);

    if (res == "OK") {
        $("#cameraSetting").click();
        alertify.success("Settings Saved");
    } else {
        alertify.error("ERROR");
    }
}

$("#checkCameraConnection").click(function () {
    // saveCameraSettings();
    $.post(
        "/settings/camera/checkconnection",
        null,
        checkCameraConnectionCallback
    );
});

function checkCameraConnectionCallback(data, status, xhr) {
    let res = xhr.responseText;
    console.log(res);

    if (res == "OK") {
        alertify.success("Connected!");
    } else {
        alertify.error("Connection error!");
    }
}

$(document).ready(function () {
    $("#toggleDbSettings").change(function () {
        if (this.checked) {
            $("#databaseIPInput").prop("disabled", false);
            $("#databasePortInput").prop("disabled", false);
            $("#databaseUserInput").prop("disabled", false);
            $("#databasePasswordInput").prop("disabled", false);

            $("#saveDBSettings").prop("disabled", false); // ENABLE SAVE BTN
            $("#checkDBConnection").prop("disabled", true); // DISABLE TEST BTN
        } else {
            $("#databaseIPInput").prop("disabled", true);
            $("#databasePortInput").prop("disabled", true);
            $("#databaseUserInput").prop("disabled", true);
            $("#databasePasswordInput").prop("disabled", true);

            $("#saveDBSettings").prop("disabled", true); // ENABLE SAVE BTN
            $("#checkDBConnection").prop("disabled", false); // DISABLE TEST BTN
        }
    });

    $(".scale-connection-settings").change(function () {
        let id = this.id.split("-")[1];
        if (this.checked) {
            $("#scaleIpInput-" + id).prop("disabled", false);
            $("#scalePortInput-" + id).prop("disabled", false);
            $("#saveScaleSettings-" + id).prop("disabled", false);
            $("#scaleConnection-" + id).prop("disabled", true); // disable test connection btn
        } else {
            $("#scaleIpInput-" + id).prop("disabled", true);
            $("#scalePortInput-" + id).prop("disabled", true);
            $("#saveScaleSettings-" + id).prop("disabled", true);
            $("#scaleConnection-" + id).prop("disabled", false); // enable test connection btn
        }
    });

    $(".enable-camera-settings").change(function () {
        /*
            CAMERA SETTINGS CHECKBOX
        */

        if (this.checked) {
            $("#ComPortInput").prop("disabled", false);
            $("#BaudRateInput").prop("disabled", false);
            $("#BiteSizeInput").prop("disabled", false);
            $("#ParityInput").prop("disabled", false);
            $("#StopBitsInput").prop("disabled", false);
            $("#StopBitsInput").prop("disabled", false);
            $("#FlowControlInput").prop("disabled", false);

            // ENABLE SAVE BUTTON
            $("#saveCameraSettings").prop("disabled", false);
            // DISABLE TEST CONNECTION BTN
            $("#checkCameraConnection").prop("disabled", true);
        } else {
            $("#ComPortInput").prop("disabled", true);
            $("#BaudRateInput").prop("disabled", true);
            $("#BiteSizeInput").prop("disabled", true);
            $("#ParityInput").prop("disabled", true);
            $("#StopBitsInput").prop("disabled", true);
            $("#StopBitsInput").prop("disabled", true);
            $("#FlowControlInput").prop("disabled", true);

            // DISABLE CAMMERA SAVE BTN
            $("#saveCameraSettings").prop("disabled", true);
            // ENABLE TEST CONNECTION BTN
            $("#checkCameraConnection").prop("disabled", false);
        }
    });
});
