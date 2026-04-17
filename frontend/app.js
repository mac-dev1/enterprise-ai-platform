let session_id = localStorage.getItem("session_id");

if (!session_id) {
    session_id = crypto.randomUUID();
    localStorage.setItem("session_id", session_id);
}

async function sendMessage() {
    const input = document.getElementById("input");
    const text = input.value.trim();

    if (!text) return;

    addMessage("user", text);
    input.value = "";

    const response = await fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: text,
            session_id: session_id
        })
    });

    const data = await response.json();

    summary = data.summary;

    addMessage("ai", data.answer);
}

function addMessage(role, text) {
    const messages = document.getElementById("messages");

    const div = document.createElement("div");
    div.classList.add("message", role);

    const html = marked.parse(text)
    div.innerHTML = html;

    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

// Enter
document.getElementById("input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});