function httpGet() {
    window.location.href = "/exp";
}


function nextStimuli(wait) {
    setTimeout(httpGet, wait);
}

function submitResponse(res) {
    var resfield = document.getElementById("resfield");
    resfield.value = res;
    var resform = document.getElementById("resform");
    resform.submit();
}

function keyup() {
    // submit yes
    if (d3.event.keyCode === 65) {
        submitResponse(1);
    }
    // submit no
    else if (d3.event.keyCode === 76) {
        submitResponse(0);
    }

    //FIXME
    else if (d3.event.keyCode === 32) {
        httpGet();
    }
}


d3.select(window)
    .on('keyup', keyup);
