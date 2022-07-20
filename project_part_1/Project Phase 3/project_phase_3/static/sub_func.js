var set_id = -1;

socket.on('connect', function() {
    // connect to subscriber channel
    // socket.emit('join', {"type": "subscriber"});
});

socket.on('load', data =>{
    let displayed_data = document.getElementById("data");
    displayed_data.innerHTML = data.data;
});

socket.on('advertised', data =>{
    let displayed_data = document.getElementById("data");
    displayed_data.innerHTML = data.data;
});

socket.on('subscribed', data =>{
    let displayed_data = document.getElementById("data2");
    displayed_data.innerHTML = data.data;
});

socket.on('notified', data =>{
    console.log("notified...");
    let displayed_data = document.getElementById("data3");
    displayed_data.innerHTML += "<b>Title: </b>" + data.title + " <b>Price: </b>" + data.price + "<br>";
});

function subscribe(){
    const value = parseInt(document.getElementById("price").value);
    if (Number.isInteger(value)){
        socket.emit('subscribe', {"value": value});
    }
}
function unsubscribe(){
    const value = parseInt(document.getElementById("price2").value);
    if (Number.isInteger(value)){
        socket.emit('unsubscribe', {"value": value});
    }
}

function login(){
    const value = parseInt(document.getElementById("login_ID").value);
    if (Number.isInteger(value)){
        socket.emit('sub_login', {"id": value});
    }
}
socket.on('login_response', data =>{
    let received_value = data.data;
    if (received_value !== "error") {
        set_id = received_value;
        let display = document.getElementById('login_form');
        display.innerHTML = "<h1><br><b> Welcome, subscriber #" + set_id.toString() + "</b></h1>";
    }else{
        let display = document.getElementById('login_response');
        display.innerHTML = "<br><b>Login Failed: subscriber ID does not exist.</b>";
    }
});

function create(){
    const value = parseInt(document.getElementById("create_ID").value);
    if (Number.isInteger(value)){
        if (Number.isInteger(value)){
            socket.emit('sub_create', {"id": value});
        }
    }
}
socket.on('create_response', data =>{
    let received_value = data.data;
    if (received_value !== "error") {
        set_id = received_value;
        let display = document.getElementById('create_response');
        display.innerHTML = "<br><b>ID: " + set_id.toString() + " has been created successfully!</b>";
    }else{
        let display = document.getElementById('create_response');
        display.innerHTML = "<br><b>ID creation failed: ID already exists.</b>";
    }
});