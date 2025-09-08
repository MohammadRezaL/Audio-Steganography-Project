// Display decoded message
document.getElementById("decodeForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    let formData = new FormData(this);
    let response = await fetch("/decode", { method: "POST", body: formData });
    let result = await response.json();
    document.getElementById("decodedMessage").innerText = "📩 Message: " + result.message;
});
