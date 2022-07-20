
socket.on('connect', function() {
    // connect to subscriber channel
    // socket.emit('join', {"type": "subscriber"});
    socket.emit('advertised');
    poll();
});

socket.on('advertised', data =>{
    let displayed_data = document.getElementById("data");
    displayed_data.innerHTML = data.topics;
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
        socket.emit('subscribe', {"topic": value});
    }
}
function unsubscribe(){
    const value = parseInt(document.getElementById("price2").value);
    if (Number.isInteger(value)){
        socket.emit('unsubscribe', {"topic": value});
    }
}

function poll(){
    setTimeout(() => {
        socket.emit('update');
        poll()
        }, 5000);
}