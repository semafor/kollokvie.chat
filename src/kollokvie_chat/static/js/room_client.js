
function poller(url) {
    var oReq = new XMLHttpRequest();
    oReq.addEventListener("load", handlePollresponse);
    oReq.open("GET", url);
    oReq.send();
}

function handlePollresponse() {
    var messages = parseInt(this.getResponseHeader("messages"), 10);
    if (isNaN(messages)) {
        throw new Error("no messages");
    } else {
        body.classList.remove('bad-poll-response');
    }

    if (messages > 0) {
        scrollToBottom();
    }

    message_list.insertAdjacentHTML('beforeend', this.responseText);
}

function get_last_msg_id() {
    var list = message_list.getElementsByTagName('li');
    if (list.length) {
        return list[list.length - 1].dataset.msgId;
    } else {
        return 0;
    }
}

function makeid() {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}

function scrollToBottom() {
    var chatbox = document.getElementById("chat-box");
    chatbox.scrollTop = chatbox.scrollHeight;
}
