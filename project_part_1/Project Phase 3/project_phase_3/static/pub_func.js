var socket = io('http://localhost:8001');
var parent = io('http://localhost:8101');
var set_id = -1;

socket.on('connect', function() {
    // connect to publisher channel
    // socket.emit('join', {"room": "publisher"});
});

parent.on('connect', function() {
    // connect to parent
});

socket.on('load', data =>{
    console.log("receiving currently advertised topics...")
    let displayed_data = document.getElementById("data");
    displayed_data.innerHTML = data.topics;
    console.log(data);
    parent.emit('load_data', data);
});

parent.on('print', data =>{
    console.log(data.value);
});

function advertise(){
    const value = parseInt(document.getElementById("price").value);
    if (Number.isInteger(value)){
        console.log("advertising...")
        socket.emit('advertise', {"value": value});
    }
}
socket.on('advertised', data =>{
    let displayed_data = document.getElementById("data");
    displayed_data.innerHTML = data.data;
    parent.emit('update', data);
});
function deadvertise(){
    const value = parseInt(document.getElementById("price2").value);
    if (Number.isInteger(value)){
        console.log("deadvertising... " + value.toString());
        socket.emit('deadvertise', {"value": value});
    }
}

function publish(){
    console.log("publishing...")
    parent.emit('publish', {"value": "publish"});
}
parent.on('published', data =>{
    console.log(data.topics);
    let displayed_data = document.getElementById("data2");
    displayed_data.innerHTML = "<b>Title: </b>" + data.game.title + " <b>Price: </b>" + data.game.price;
    socket.emit('publish', data)
});

function login(){
    const value = parseInt(document.getElementById("login_ID").value);
    if (Number.isInteger(value)){
        socket.emit('pub_login', {"id": value});
    }
}
socket.on('login_response', data =>{
    let received_value = data.data;
    if (received_value !== "error") {
        set_id = received_value;
        let display = document.getElementById('login_form');
        display.innerHTML = "<h1><br><b> Welcome, publisher #" + set_id.toString() + "</b></h1>";
    }else{
        let display = document.getElementById('login_response');
        display.innerHTML = "<br><b>Login Failed: ID does not exist.</b>";
    }
});

function create(){
    const value = parseInt(document.getElementById("create_ID").value);
    if (Number.isInteger(value)){
        if (Number.isInteger(value)){
            socket.emit('pub_create', {"id": value});
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
        display.innerHTML = "<br><b>ID creation failed: publisher ID already exists.</b>";
    }
});