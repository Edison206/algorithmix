function login_funcion() {
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    fetch("/login/verify/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `email=${email}&password=${password}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}
