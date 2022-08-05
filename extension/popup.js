const urlInput = document.querySelector("#url");
const descriptionInput = document.querySelector("#description");
const authorInput = document.querySelector("#author");
const form = document.forms["add-form"];
const sentAlert = document.querySelector("#success");

authorInput.value = localStorage.getItem("id");

const WEBHOOK_URL =
    "https://discord.com/api/webhooks/1004941371997704413/VZhV-7V-IsiJwB3NKI4xJhDLt81LrMw-A6cGDce_70vgjjBpQqECSQdq9txDjhHfl2zm";

const sendMessage = (cmd, authorId) => {
    const request = new XMLHttpRequest();
    request.open("POST", WEBHOOK_URL);
    request.setRequestHeader("Content-type", "application/json");
    const params = {
        username: authorId,
        avatar_url: "",
        content: cmd,
    };
    request.send(JSON.stringify(params));
};

browser.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
    const { title, url } = tabs[0];
    urlInput.value = url;
    descriptionInput.value = title;
});

form.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const keywords = formData.get("keywords");
    const description = formData.get("description");
    const authorId = formData.get("author");
    const url = formData.get("url");

    // save author id in localstorage
    localStorage.setItem("id", authorId);

    const command = `"${keywords}" "${description}" ${url}`;
    sendMessage(command, authorId);
    sentAlert.classList.remove("hide");
});
