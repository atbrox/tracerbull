<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js"></script>
    <script type="text/javascript">

        $(document).ready(function () {
            if ("WebSocket" in window) {
                console.log("0");
                var foo = new WebSocket("ws://{{wshostname}}:{{wsport}}/");
                console.log("0b");
                window.ws = foo;


                window.ws.onopen = function () {
                    console.log("1");
                    return console.log("open");
                };

                window.ws.onmessage = function (e) {
                    console.log("2");
                    alert(e.data);
                    return console.log(e.data);
                };

                window.ws.onclose = function (e) {
                    console.log("3");
                    return console.log("closed websocket connection");
                };

                window.ws.onerror = function (e) {
                    console.log("4");
                    return console.log("error with websocket connection" + e);
                };

                window.ws.sendform = function () {
                    console.log("5");
                    var myform = $(document.wsinputform);
                    var json_form_data = JSON.stringify(myform.serializeArray());
                    console.log("sending " + json_form_data);
                    ws.send(json_form_data);
                    return false;
                }

                $("#mybutton").click(window.ws.sendform);

            } else {
                window.alert("no websocket!");
            }

        });


    </script>
    <title></title>
</head>
<body>

Input values for websocket service ws://{{wshostname}}:{{wsport}}
<form name="wsinputform">
    arg0 <input type="text" name="arg0" value="default0">
    arg1 <input type="text" name="arg1" value="default1">


    <button id="mybutton">Submit</button>
</form>


</body>
</html>
