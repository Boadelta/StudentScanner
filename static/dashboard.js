const home = document.getElementById("home");
const user = document.getElementById("user");
const student = document.getElementById("student");
const logout = document.getElementById("logout");


window.onload = () => {
    $(".holder").load("/home");
    }

home.addEventListener("click", () => {
    $(".holder").load("/home");
    home.className ="active";
    user.className ="";
    student.className = "";
    })

user.addEventListener("click", () => {
    $(".holder").load("/userMgt");
    home.className = "";
    user.className = "active";
    student.className = "";
    
    })

student.addEventListener("click", () => {
    $(".holder").load("/studMgt");
    home.className = "";
    user.className="";
    student.className = "active";
    })


    