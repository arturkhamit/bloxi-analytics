const auth = document.querySelector(".auth");
const loginTab = document.querySelector('[data-tab="login"]');
const signupTab = document.querySelector('[data-tab="signup"]');
const submitBtn = document.querySelector(".button-submit");
const form = auth.querySelector("form");
const emailField = auth.querySelector(".email-field");

const usernameInput = document.getElementById("username");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");

function setMode(mode) {
  auth.dataset.mode = mode;

  if (mode === "login") {
    emailField.textContent = "Email address or login";
    loginTab.classList.add("active");
    loginTab.classList.remove("dim");

    signupTab.classList.add("dim");
    signupTab.classList.remove("active");

    submitBtn.textContent = "Log In";
  } else {
    emailField.textContent = "Email address";
    signupTab.classList.add("active");
    signupTab.classList.remove("dim");

    loginTab.classList.add("dim");
    loginTab.classList.remove("active");

    submitBtn.textContent = "Sign Up";
  }
}

loginTab.addEventListener("click", (e) => {
  e.preventDefault();
  setMode("login");
});

signupTab.addEventListener("click", (e) => {
  e.preventDefault();
  setMode("signup");
});

setMode("login");

if (emailInput) {
  const emailField = emailInput.closest(".field-email");

  emailInput.addEventListener("input", () => {
    const value = emailInput.value.trim();

    const isValid =
      value !== "" && emailInput.type === "email"
        ? emailInput.checkValidity()
        : value !== "";

    if (!emailField) return;

    if (isValid) {
      emailField.classList.add("has-value");
    } else {
      emailField.classList.remove("has-value");
    }
  });
}

const USERS_KEY = "users";
const CURRENT_USER_KEY = "currentUser";

function getUsers() {
  const raw = localStorage.getItem(USERS_KEY);
  return raw ? JSON.parse(raw) : [];
}

function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function setCurrentUser(user) {
  sessionStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));

  localStorage.removeItem(CURRENT_USER_KEY);
}

function goToMain() {
  window.location.href = "main.html";
}

function registerUser(login, email, password) {
  const users = getUsers();

  if (users.some((u) => u.email === email)) {
    alert("A user with this email already exists.");
    return false;
  }

  const newUser = {
    id: Date.now(),
    login: login,
    email: email,
    password: password,
  };

  users.push(newUser);
  saveUsers(users);


  console.log("All user:", users);

  return true;
}

function loginUser(identifier, password) {
  const users = getUsers();

  const user = users.find(
    (u) =>
      (u.email === identifier || u.login === identifier) &&
      u.password === password
  );

  if (!user) {
    alert("Wrond login/email or password");
    return false;
  }


  return true;
}

form.addEventListener("submit", (e) => {
  e.preventDefault();

  const mode = auth.dataset.mode;
  const loginValue = usernameInput.value.trim();
  const emailValue = emailInput.value.trim();
  const passwordValue = passwordInput.value;

  let ok = false;

  if (mode === "signup") {
    if (!loginValue || !emailValue || !passwordValue) {
      alert("Enter login/password");
      return;
    }

    ok = registerUser(loginValue, emailValue, passwordValue);
  } else {
    if (!emailValue || !passwordValue) {
      alert("Enter login/password");
      return;
    }

    ok = loginUser(emailValue, passwordValue);
  }

  if (ok) {
    goToMain();
  }
});

window.addEventListener("DOMContentLoaded", () => {
  const rawLocal = localStorage.getItem(CURRENT_USER_KEY);
  if (!rawLocal) return;

  try {
    const user = JSON.parse(rawLocal);
    console.log("Auto-login as: ", user.login);
    // goToMain();
  } catch (e) {
    console.error("Error read currentUser in localStorage", e);
    localStorage.removeItem(CURRENT_USER_KEY);
  }
});

const toggle = document.getElementById("togglePass");
if (toggle && passwordInput) {
  toggle.addEventListener("click", () => {
    const isPwd = passwordInput.type === "password";
    passwordInput.type = isPwd ? "text" : "password";
    toggle.setAttribute("aria-pressed", isPwd ? "true" : "false");
  });
}
