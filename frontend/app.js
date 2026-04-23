let conversation_id = null;
let conversations = null;

async function register() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    alert(data.message || data.error);
}

async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        showChat()
        loadConversations()
    } else {
        alert("Login failed");
    }
}

function logout() {
    localStorage.removeItem("token");
    location.reload();
}

function toggleSidebar() {
    const sidebar = document.getElementsByClassName("sidebar")[0];
    sidebar.classList.toggle("hidden")
}

function newChat() {
    conversation_id = null;
    document.getElementById("messages").innerHTML = "";
    if(conversations){
        conversations.childNodes.forEach(div =>{
            div.classList.remove("active")
        })
    }
}

async function loadConversations() {
    const token = localStorage.getItem("token");

    const res = await fetch("/conversations", {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const data = await res.json();

    conversations = document.getElementById("conversations");
    conversations.innerHTML = "";

    data.forEach(conv => {
        const div = document.createElement("div");
        div.id = conv.title
        div.innerText = conv.title;
        div.onclick = () => loadConversation(conv.id,conv.title);
        conversations.appendChild(div);
    });
}

async function loadConversation(id,title) {
    const token = localStorage.getItem("token");

    const res = await fetch(`/conversations/${id}`, {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const messages = await res.json();

    const container = document.getElementById("messages");
    container.innerHTML = "";
    
    messages.forEach(m => {
        addMessage(m.role, m.content, m.timestamp);
    });

    conversations.childNodes.forEach(child =>{
        child.classList.remove("active")
    })


    document.getElementById(title).classList.add("active");
    
    const orderRes = await fetch(`/conversations`, {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const orders = await orderRes.json();
    orders.forEach(order =>{
        conversations.appendChild(document.getElementById(order.title))
    })

    conversation_id = id;
}

function typeText(element, text, speed = 20) {
    const messages = document.getElementById("messages")
    element.innerHTML = ""
    let i = 0;
    element.classList.remove("typing")
    text = marked.parse(text)
    function typing() {
        if (i < text.length) {
            element.innerHTML = text.slice(0,i);
            messages.scrollTop = messages.scrollHeight
            i++;
            setTimeout(typing, speed);
        }
    }

    typing();
}

async function sendMessage() {
    const token = localStorage.getItem("token");

    if (!token) {
        alert("Please login first");
        return;
    }

    if(conversation_id){
        const res = await fetch(`/conversations`, {
                headers: {
                    "Authorization": "Bearer " + token
                }
            });
        const data = await res.json();
        const item = data.find(el => el.id === conversation_id)
        const title = item ? item.title : null;
        conversations.prepend(document.getElementById(title))
    }

    const input = document.getElementById("input");
    const text = input.value.trim();

    if (!text) return;
    addMessage("user", text,new Date().toISOString());
    input.value = "";

    const messageContainer = addMessage("ai", "");
    
    const messageDiv = messageContainer.childNodes[0]
    messageDiv.classList.add("typing")
    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json",
                   "Authorization": "Bearer " + localStorage.getItem("token")
                },
        body: JSON.stringify({
            question: text,
            conversation_id: conversation_id
        })
    });

    const data = await response.json();
    if(!document.getElementById(data.conversation)){
        const div = document.createElement("div")
        div.id = data.conversation
        div.innerText = data.conversation;
        div.onclick = () => loadConversation(data.conversation_id,data.conversation);
        conversations.prepend(div)
        div.classList.add("active")
    } 
    typeText(messageDiv,data.answer)
    
    messageContainer.lastChild.innerText = new Date(data.timestamp).toLocaleTimeString([],{
        hour: '2-digit',
        minute: '2-digit'
    })

    if(conversation_id == null){
        conversation_id = data.conversation_id
    }
}

function addMessage(role, text, timestamp=null) {
    
    const messages = document.getElementById("messages");
    const container = document.createElement("div")

    const message = document.createElement("div");
    message.classList.add("message", role);

    const html = marked.parse(text)
    message.innerHTML = html;

    const time = document.createElement("div");
    time.classList.add("timestamp");

    container.appendChild(message)
    if (timestamp){
        const date = new Date(timestamp)
        time.innerText = date.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    if (role == "user"){
        container.style.justifyItems="right"
    }
    container.appendChild(time)
    messages.appendChild(container);
    messages.scrollTop = messages.scrollHeight;

    return container; 
}

// Enter
document.getElementById("input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

function showChat() {
    document.getElementById("auth-view").style.display = "none";
    document.getElementsByClassName("layout")[0].style.display = "flex";
}

function showAuth() {
    document.getElementById("auth-view").style.display = "flex";
    document.getElementsByClassName("layout")[0].style.display = "None";
}

window.onload = () => {
    const token = localStorage.getItem("token");

    if (token) {
        showChat()
        loadConversations()
    }else{
        showAuth()
    }
};

