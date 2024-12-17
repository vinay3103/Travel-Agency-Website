// Booking Form Validation
function validateBookingForm() {
  const travelersInput = document.getElementById("travelers");
  const startDateInput = document.getElementById("start_date");
  const endDateInput = document.getElementById("end_date");
  const currentDate = new Date().toISOString().split("T")[0];

  if (travelersInput.value <= 0) {
      alert("Please enter a valid number of travelers.");
      return false;
  }

  if (startDateInput.value < currentDate || endDateInput.value < currentDate) {
      alert("Booking dates cannot be in the past.");
      return false;
  }

  if (startDateInput.value > endDateInput.value) {
      alert("Start date cannot be later than end date.");
      return false;
  }

  return true;
}


// Function to Show Success Modal
function showSuccessModal() {
  const successModal = new bootstrap.Modal(document.getElementById("successModal"));
  successModal.show();
}

// Function to Show Error Modal with Message
function showErrorModal(message) {
  const errorModalMessage = document.getElementById("errorModalMessage");
  errorModalMessage.textContent = message;
  const errorModal = new bootstrap.Modal(document.getElementById("errorModal"));
  errorModal.show();
}

// Confirm Deletion for Admin Actions
function confirmDeletion() {
  return confirm("Are you sure you want to delete this item?");
}

// Success Popup for Booking
function showBookingSuccess() {
  const successMessage = document.getElementById("success-message");
  successMessage.style.display = "block";

  // Hide the success message after 3 seconds
  setTimeout(() => {
    successMessage.style.display = "none";
  }, 3000);
}
document.addEventListener("DOMContentLoaded", () => {
    const packages = document.querySelectorAll(".package");
  
    packages.forEach((packageCard) => {
      const availability = parseInt(packageCard.getAttribute("data-availability"), 10);
      const bookNowButton = packageCard.querySelector(".btn");
  
      if (availability <= 0) {
        bookNowButton.textContent = "Fully Booked";
        bookNowButton.disabled = true;
        bookNowButton.style.backgroundColor = "gray";
      }
    });
  });
  