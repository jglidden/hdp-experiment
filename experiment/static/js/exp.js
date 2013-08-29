function httpGet() {
    window.location.href = "/exp";
}


function nextStimuli() {
    setTimeout(httpGet, 1000);
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
}

d3.select(window)
    .on('keyup', keyup);
