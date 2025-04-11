document.addEventListener("DOMContentLoaded", () => {
  // Quantity increment/decrement buttons
  const decrementBtn = document.getElementById("decrement")
  const incrementBtn = document.getElementById("increment")
  const quantityInput = document.getElementById("id_quantity")

  if (decrementBtn && incrementBtn && quantityInput) {
    decrementBtn.addEventListener("click", () => {
      const currentValue = Number.parseInt(quantityInput.value)
      if (currentValue > 1) {
        quantityInput.value = currentValue - 1
      }
    })

    incrementBtn.addEventListener("click", () => {
      const currentValue = Number.parseInt(quantityInput.value)
      const maxValue = Number.parseInt(quantityInput.getAttribute("max") || 99)
      if (currentValue < maxValue) {
        quantityInput.value = currentValue + 1
      }
    })
  }

  // Star rating functionality
  const ratingLabels = document.querySelectorAll(".rating-label")
  const ratingInputs = document.querySelectorAll(".rating-input")

  if (ratingLabels.length > 0) {
    ratingLabels.forEach((label) => {
      label.addEventListener("click", function () {
        const starIcon = this.querySelector("i")
        const ratingInput = this.querySelector("input")

        // Reset all stars
        ratingLabels.forEach((l) => {
          l.querySelector("i").className = "far fa-star fa-lg"
        })

        // Fill stars up to the selected one
        const rating = Number.parseInt(ratingInput.value)
        for (let i = 0; i < rating; i++) {
          ratingLabels[i].querySelector("i").className = "fas fa-star fa-lg"
        }
      })

      // Hover effect
      label.addEventListener("mouseenter", function () {
        const ratingInput = this.querySelector("input")
        const rating = Number.parseInt(ratingInput.value)

        for (let i = 0; i < rating; i++) {
          ratingLabels[i].querySelector("i").className = "fas fa-star fa-lg"
        }
      })

      label.addEventListener("mouseleave", () => {
        // Reset to selected rating
        ratingLabels.forEach((l) => {
          l.querySelector("i").className = "far fa-star fa-lg"
        })

        // Find selected rating
        let selectedRating = 0
        ratingInputs.forEach((input) => {
          if (input.checked) {
            selectedRating = Number.parseInt(input.value)
          }
        })

        // Fill stars up to selected rating
        for (let i = 0; i < selectedRating; i++) {
          ratingLabels[i].querySelector("i").className = "fas fa-star fa-lg"
        }
      })
    })
  }

  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert:not(.alert-permanent)")
  if (alerts.length > 0) {
    setTimeout(() => {
      alerts.forEach((alert) => {
        const closeButton = alert.querySelector(".btn-close")
        if (closeButton) {
          closeButton.click()
        }
      })
    }, 5000)
  }
})
