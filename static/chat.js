const ws = new WebSocket("ws://localhost:8888/ws");

ws.onopen = () => {
    console.log("Connected to WebSocket");
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const messages = document.getElementById("messages");
    const messageElement = document.createElement("div");

    if (data.type === "info") {
        messageElement.textContent = `[INFO]: ${data.message}`;
    } else if (data.type === "message") {
        messageElement.textContent = data.message;
    }
    messages.appendChild(messageElement);
};

document.getElementById("send").addEventListener("click", () => {
    const input = document.getElementById("message");
    ws.send(input.value);
    input.value = "";
});
