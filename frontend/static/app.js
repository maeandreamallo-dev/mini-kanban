const API_URL = "/tasks";

const taskDialog = document.getElementById("task-dialog");
const taskForm = document.getElementById("task-form");
const addTaskButton = document.getElementById("add-task-btn");
const cancelButton = document.getElementById("cancel-btn");

const statuses = [
    "BACKLOG",
    "TODO",
    "IN_PROGRESS",
    "REVIEW",
    "DONE"
];

document.addEventListener("DOMContentLoaded", loadTasks);

addTaskButton.addEventListener("click", () => {
    taskForm.reset();
    taskDialog.showModal();
});

cancelButton.addEventListener("click", () => {
    taskDialog.close();
});

taskForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(taskForm);

    const task = {
        title: formData.get("title").trim(),
        description: formData.get("description").trim() || null,
        priority: formData.get("priority")
    };

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(task)
        });

        if (!response.ok) {
            throw new Error("Failed to create task.");
        }

        taskDialog.close();
        await loadTasks();
    } catch (error) {
        alert(error.message);
    }
});


async function loadTasks() {
    try {
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error("Failed to load tasks.");
        }

        const tasks = await response.json();

        clearBoard();
        tasks.forEach(renderTask);
        updateTaskCounts(tasks);
    } catch (error) {
        console.error(error);
        alert("Unable to load tasks.");
    }
}


function clearBoard() {
    statuses.forEach((status) => {
        const container = document.getElementById(status);
        container.innerHTML = "";
    });
}


function renderTask(task) {
    const container = document.getElementById(task.status);

    if (!container) {
        return;
    }

    const card = document.createElement("article");
    card.className = "task-card";

    card.innerHTML = `
        <h3>${escapeHtml(task.title)}</h3>

        <p>
            ${escapeHtml(task.description || "No description")}
        </p>

        <span class="priority priority-${task.priority}">
            ${task.priority}
        </span>

        <div class="task-actions">
            <button onclick="moveTask(${task.id}, '${task.status}')">
                Move
            </button>

            <button onclick="deleteTask(${task.id})">
                Delete
            </button>
        </div>
    `;

    container.appendChild(card);
}


async function moveTask(taskId, currentStatus) {
    const currentIndex = statuses.indexOf(currentStatus);

    if (currentIndex === -1 || currentIndex === statuses.length - 1) {
        return;
    }

    const nextStatus = statuses[currentIndex + 1];

    try {
        const response = await fetch(
            `${API_URL}/${taskId}/status`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: nextStatus
                })
            }
        );

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));

            throw new Error(
                errorData.detail ||
                `Failed to move task: ${response.status}`
            );
        }

        await loadTasks();
    } catch (error) {
        alert(error.message);
    }
}

async function deleteTask(taskId){
    const confirmed = confirm(
        "Are you sure you want to delete this task?"
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/${taskId}`,
            {
                method: "DELETE"
            }
        );

        if (!response.ok) {
            throw new Error("Failed to delete task.");
        }

        await loadTasks();
    } catch (error) {
        alert(error.message);
    }
}


function updateTaskCounts(tasks) {
    statuses.forEach((status) => {
        const count = tasks.filter(
            (task) => task.status === status
        ).length;

        document.getElementById(
            `count-${status}`
        ).textContent = count;
    });
}


function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
}
