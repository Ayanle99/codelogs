const profilePic = document.getElementById("profilePic");
const picInput = document.getElementById("picInput");

// Click image to open file picker
profilePic.addEventListener("click", () => {
  picInput.click();
});

// Preview the new image
picInput.addEventListener("change", () => {
  const file = picInput.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = e => {
      profilePic.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
});

// Tabs functionality
document.addEventListener("DOMContentLoaded", () => {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach(button => {
    button.addEventListener("click", () => {
      tabButtons.forEach(btn => btn.classList.remove("active"));
      tabContents.forEach(content => content.classList.remove("active"));

      button.classList.add("active");
      const tabId = button.getAttribute("data-tab");
      document.getElementById(tabId).classList.add("active");
    });
  });
});

// user account age

document.addEventListener("DOMContentLoaded", () => {
  const joinedElem = document.querySelector(".user-joined");

  if (joinedElem) {
    const joinedDate = new Date(joinedElem.dataset.joined);
    const now = new Date();

    // Format "Month Day, Year"
    const formattedDate = joinedDate.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric"
    });

    // Calculate age
    const diffTime = now - joinedDate;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const diffYears = now.getFullYear() - joinedDate.getFullYear();
    const diffMonths = now.getMonth() - joinedDate.getMonth() + (diffYears * 12);

    let age = "";
    if (diffYears >= 1) {
      age = `${diffYears} year${diffYears > 1 ? "s" : ""} ago`;
    } else if (diffMonths >= 1) {
      age = `${diffMonths} month${diffMonths > 1 ? "s" : ""} ago`;
    } else {
      age = `${diffDays} day${diffDays !== 1 ? "s" : ""} ago`;
    }

    // Update content and accessibility label
    joinedElem.textContent = `Joined ${formattedDate} (${age})`;
    joinedElem.setAttribute("aria-label", `User joined on ${formattedDate}, ${age}`);
  }
});
