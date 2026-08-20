const chatWindow = document.getElementById("chat");
const input = document.getElementById("message");
const sendBtn = document.getElementById("send-btn");

let pendingRequestId = null;

function addMessage(text, cssClass) {
    const div = document.createElement("div");

    div.className = `message ${cssClass}`;

    div.textContent = text;

    chatWindow.appendChild(div);

    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showTyping() {

    const div = document.createElement("div");

    div.className = "message bot typing";

    div.id = "typing";

    div.innerHTML = `
        <div class="typing-container">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    chatWindow.appendChild(div);

    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeTyping() {

    const typing = document.getElementById("typing");

    if (typing) {
        typing.remove();
    }
}

function showGuardrailStatus(status, reason = null) {

    let css = "";

    switch (status) {

        case "PASSED":
            css = "guard-pass";
            break;

        case "BLOCKED":
            css = "guard-block";
            break;

        case "WAITING_FOR_CONFIRMATION":
            css = "guard-wait";
            break;

        case "CANCELLED_BY_USER":
            css = "guard-cancel";
            break;

        case "MASKED":
            css = "guard-block";
            break;

        default:
            css = "";
    }

    const div = document.createElement("div");

    div.className = `message eval`;

    div.innerHTML = `
        <div class="guardrail-card ${css}">
            <div class="guardrail-title">
                Guardrail Status
            </div>

            <div class="guardrail-status">
                ${status}
            </div>

            ${
                reason
                    ? `<div class="guardrail-reason">${reason}</div>`
                    : ""
            }
        </div>
    `;

    chatWindow.appendChild(div);

    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showConfirmationButtons(message) {

    const div = document.createElement("div");

    div.className = "message eval";

    div.innerHTML = `
        <div class="confirmation-card">

            <div class="confirmation-title">
                🛡 Sensitive Operation
            </div>

            <div class="confirmation-text">
                ${message}
            </div>

            <div class="confirmation-actions">

                <button class="approve-btn">
                    Continue
                </button>

                <button class="reject-btn">
                    Cancel
                </button>

            </div>

        </div>
    `;

    chatWindow.appendChild(div);

    div.querySelector(".approve-btn").onclick = () =>
        confirmRequest(true, div);

    div.querySelector(".reject-btn").onclick = () =>
        confirmRequest(false, div);

    chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function confirmRequest(approved, confirmationDiv) {

    confirmationDiv.innerHTML = `
        <div class="confirmation-processing">
            <div class="spinner"></div>
            <div>Processing your request...</div>
        </div>
    `;

    showTyping();

    try {

        const res = await fetch("/chat/confirm", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                request_id: pendingRequestId,

                approved: approved

            })

        });

        if (!res.ok) {
            throw new Error("Server Error");
        }

        const data = await res.json();

        removeTyping();

        confirmationDiv.remove();

        if (data.guardrail_status) {
            showGuardrailStatus(
                data.guardrail_status,
                data.blocked_reason
            );
        }

        addMessage(data.reply, "bot");

        pendingRequestId = null;

    }

    catch (err) {

        console.error(err);

        removeTyping();

        addMessage(
            "❌ Something went wrong. Please try again.",
            "bot"
        );
    }
}

async function sendMessage() {

    const message = input.value.trim();

    if (!message) {
        return;
    }

    addMessage(message, "user");

    input.value = "";

    sendBtn.disabled = true;

    showTyping();

    try {

        const res = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message
            })

        });

        if (!res.ok) {
            throw new Error("Server Error");
        }

        const data = await res.json();

        removeTyping();

        if (data.guardrail_status) {

            showGuardrailStatus(
                data.guardrail_status,
                data.blocked_reason
            );
        }

        if (data.requires_confirmation) {

            pendingRequestId = data.request_id;

            showConfirmationButtons(data.reply);

            return;
        }

        addMessage(data.reply, "bot");

    }

    catch (err) {

        console.error(err);

        removeTyping();

        addMessage(
            "❌ Something went wrong. Please try again.",
            "bot"
        );
    }

    finally {

        sendBtn.disabled = false;

        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", (e) => {

    if (e.key === "Enter") {
        sendMessage();
    }

});