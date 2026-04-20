let session_id = localStorage.getItem("session_id");

if (!session_id) {
    session_id = crypto.randomUUID();
    localStorage.setItem("session_id", session_id);
}

function typeText(element, text, speed = 20) {
    const messages = document.getElementById("messages")
    element.innerHTML = ""
    let i = 0;
    element.classList.remove("typing")
    function typing() {
        if (i < text.length) {
            element.innerHTML = marked.parse(text.substring(0, i));
            messages.scrollTop = messages.scrollHeight
            i++;
            setTimeout(typing, speed);
        }
    }

    typing();
}

async function sendMessage() {
    const input = document.getElementById("input");
    const text = input.value.trim();

    if (!text) return;

    addMessage("user", text);
    input.value = "";

    const messageDiv = addMessage("ai", "");
    messageDiv.classList.add("typing")

    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            question: text,
            session_id: session_id
        })
    });

    const data = await response.json();
    
    typeText(messageDiv,data.answer)
}

function addMessage(role, text) {
    const messages = document.getElementById("messages");

    const div = document.createElement("div");
    div.classList.add("message", role);

    const html = marked.parse(text)
    div.innerHTML = html;

    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;

    return div; 
}

async function loadHistory() {
    const res = await fetch(`/history/${session_id}`);

    if (!res.ok) return;

    const history = await res.json();

    history.forEach(item => {
        addMessage("user", item.q);
        addMessage("ai", item.a);
    });
}

// Enter
document.getElementById("input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

window.onload = async function () {
    await loadHistory();
};