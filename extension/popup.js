const urlInput = document.querySelector("#url");
const descriptionInput = document.querySelector("#description");
const form = document.forms["add-form"]

const sendMessage = (cmd) => {
    const request = new XMLHttpRequest();
    request.open("POST", "https://discord.com/api/webhooks/1004941371997704413/VZhV-7V-IsiJwB3NKI4xJhDLt81LrMw-A6cGDce_70vgjjBpQqECSQdq9txDjhHfl2zm")
    request.setRequestHeader('Content-type', 'application/json');
    const params = {
        username: "Browser Extension",
        avatar_url: "",
        content: cmd
    }
    request.send(JSON.stringify(params))
}

browser.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const { title, url } = tabs[0];
    urlInput.value = url;
    descriptionInput.value = title;
});

form.addEventListener("submit", event => {
    event.preventDefault()
    const formData = new FormData(form);
    const keywords = formData.get("keywords")
    const description = formData.get("description")
    const url = formData.get("url")

    const command = `"${keywords}" "${description}" ${url}`
    sendMessage(command)
})
