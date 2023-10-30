const fileInp = document.getElementById("new_profile_picture");
const btn = document.getElementById("clear");
btn.addEventListener("click", () => {
    fileInp.value = null;
});
