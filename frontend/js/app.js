
const API = "/api";

// PAGE NAVIGATION
function showPage(page) {
    document.querySelectorAll(".page").forEach(p => {
        p.classList.remove("active");
    });

    document.querySelectorAll(".nav-item").forEach(n => {
        n.classList.remove("active");
    });

    document.getElementById(page).classList.add("active");

    const nav = document.querySelector(`[data-page="${page}"]`);
    if (nav) nav.classList.add("active");

    const titles = {
        dashboard: "Overview",
        assistant: "AI Support Assistant",
        tickets: "Service Tickets",
        submit: "Submit Request"
    };

    document.getElementById("page-title").textContent = titles[page];
    document.getElementById("page-name").textContent = titles[page];

    if (page === "dashboard" || page === "tickets") {
        loadDashboard();
    }
}

document.querySelectorAll(".nav-item").forEach(button => {
    button.addEventListener("click", () => {
        showPage(button.dataset.page);
    });
});


// DASHBOARD
async function loadDashboard() {
    try {
        const [statsResponse, ticketResponse] = await Promise.all([
            fetch(`${API}/stats`),
            fetch(`${API}/tickets`)
        ]);

        if (!statsResponse.ok || !ticketResponse.ok) {
            throw new Error("Unable to load dashboard");
        }

        const stats = await statsResponse.json();
        const tickets = await ticketResponse.json();

        document.getElementById("total-stat").textContent = stats.total;
        document.getElementById("open-stat").textContent = stats.open;
        document.getElementById("progress-stat").textContent = stats.in_progress;
        document.getElementById("resolved-stat").textContent = stats.resolved;

        renderRecentTickets(tickets.slice(0, 5));
        renderTicketTable(tickets);

    } catch (error) {
        console.error("Dashboard error:", error);
    }
}


// RECENT TICKETS
function renderRecentTickets(tickets) {
    const container = document.getElementById("recent-tickets");

    if (!tickets.length) {
        container.innerHTML = '<p class="empty-state">No tickets created yet.</p>';
        return;
    }

    container.innerHTML = tickets.map(ticket => `
        <div style="padding:13px 5px;border-bottom:1px solid #24334b">
            <strong style="font-size:12px">
                #${ticket.id} - ${escapeHTML(ticket.title)}
            </strong>
            <p style="font-size:10px;color:#91a0b8;margin-top:6px">
                ${escapeHTML(ticket.employee_name)}
                · ${escapeHTML(ticket.category)}
                · ${escapeHTML(ticket.status)}
            </p>
        </div>
    `).join("");
}


// TICKET TABLE

function renderTicketTable(tickets) {
    const table = document.getElementById("ticket-table");

    if (!tickets.length) {
        table.innerHTML = `
            <tr><td colspan="7" class="empty-state">
                No tickets available.
            </td></tr>`;
        return;
    }

    const statuses = [
        "Open",
        "In Progress",
        "Resolved",
        "Closed"
    ];

    table.innerHTML = tickets.map(ticket => `
        <tr>
            <td>#${ticket.id}</td>
            <td>${escapeHTML(ticket.employee_name)}</td>
            <td>${escapeHTML(ticket.title)}</td>
            <td>${escapeHTML(ticket.category)}</td>
            <td>
                <span class="badge">
                    ${escapeHTML(ticket.priority)}
                </span>
            </td>
            <td>
                <span class="badge">
                    ${escapeHTML(ticket.status)}
                </span>
            </td>
            <td>
                <select class="action-select"
                    onchange="updateTicket(${ticket.id}, this.value)">
                    ${statuses.map(status => `
                        <option value="${status}"
                            ${ticket.status === status ? "selected" : ""}>
                            ${status}
                        </option>
                    `).join("")}
                </select>
            </td>
        </tr>
    `).join("");
}


// BASIC HTML ESCAPING
function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}


// UPDATE TICKET STATUS
async function updateTicket(id, status) {
    if (!status) return;

    try {
        const response = await fetch(`${API}/tickets/${id}`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ status })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Update failed");
        }

        alert("Ticket status updated successfully.");
        loadDashboard();

    } catch (error) {
        alert(error.message);
    }
}


// AI CHAT
const chatForm = document.getElementById("chat-form");

chatForm.addEventListener("submit", async event => {
    event.preventDefault();

    const input = document.getElementById("chat-input");
    const message = input.value.trim();

    if (!message) return;

    addChatMessage(message, "user");
    input.value = "";

    const loading = addChatMessage("NEXUS AI is analyzing your issue...", "ai");

    try {
        const response = await fetch(`${API}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "AI service unavailable");
        }

        loading.querySelector("p").textContent = result.response;

    } catch (error) {
        loading.querySelector("p").textContent =
            "Unable to connect to AI: " + error.message;
    }
});


function addChatMessage(message, type) {
    const container = document.getElementById("chat-messages");
    const element = document.createElement("div");

    element.className = type === "user" ? "user-message" : "ai-message";

    if (type === "ai") {
        const heading = document.createElement("strong");
        heading.textContent = "NEXUS AI";

        const paragraph = document.createElement("p");
        paragraph.textContent = message;

        element.append(heading, paragraph);
    } else {
        element.textContent = message;
    }

    container.appendChild(element);
    container.scrollTop = container.scrollHeight;

    return element;
}


// SUBMIT SUPPORT TICKET
document.getElementById("ticket-form").addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        const resultBox = document.getElementById("ticket-result");
        const submitButton = event.target.querySelector("button");

        const data = {
            employee_name: document.getElementById("employee-name").value.trim(),
            title: document.getElementById("issue-title").value.trim(),
            description: document.getElementById("issue-description").value.trim()
        };

        submitButton.disabled = true;
        submitButton.textContent = "✦ AI is analyzing...";

        resultBox.textContent = "Analyzing issue and creating ticket...";

        try {
            const response = await fetch(`${API}/tickets`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Ticket creation failed");
            }

            resultBox.innerHTML = `
                <div class="panel">
                    <h3>✓ Ticket Created Successfully</h3>
                    <p>Ticket ID: <strong>#${result.ticket_id}</strong></p>
                    <p>Category: ${escapeHTML(result.analysis.category)}</p>
                    <p>Priority: ${escapeHTML(result.analysis.priority)}</p>
                    <p>Summary: ${escapeHTML(result.analysis.summary)}</p>
                </div>
            `;

            event.target.reset();
            loadDashboard();

        } catch (error) {
            resultBox.textContent = "Error: " + error.message;

        } finally {
            submitButton.disabled = false;
            submitButton.textContent = "✦ Analyze & Submit Request";
        }
    }
);


// INITIALIZE APPLICATION
loadDashboard();
