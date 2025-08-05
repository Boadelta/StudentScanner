// script.js file
function domReady(fn) {
    if (
        document.readyState === "complete" ||
        document.readyState === "interactive"
    ) {
        setTimeout(fn, 1000);
    } else {
        document.addEventListener("DOMContentLoaded", fn);
    }
}

domReady(function () {

    // If found you qr code
    function onScanSuccess(decodeText, decodeResult) {
        sendData(decodeText);
    }

    let htmlscanner = new Html5QrcodeScanner(
        "my-qr-reader",
        { fps: 10, qrbox: 250 }
    );
    htmlscanner.render(onScanSuccess);
});

function sendData(matNum){
    var value = matNum.toString();
    $.ajax({
        url: '/process',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({'value': value}),
        success: function(data) {
            window.location.href = data.redirect_url;
        },
        error: function(error) {
            console.log(error);
        }
    });
}
        