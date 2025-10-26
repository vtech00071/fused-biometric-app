/* Get the hamburger icon and the navigation menu */
const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".nav-menu");

/* Add a 'click' event listener to the hamburger icon.
  When it's clicked, it will run the 'mobileMenu' function.
*/
hamburger.addEventListener("click", mobileMenu);

/* This function toggles the 'active' class on both elements */
function mobileMenu() {
    /* Toggles 'active' on the hamburger icon (to make the 'X') */
    hamburger.classList.toggle("active");
    
    /* Toggles 'active' on the menu (to slide it in/out) */
    navMenu.classList.toggle("active");
}

/* This part is a small improvement: 
  It closes the menu if you click on one of the links 
  (e.g., "Face", "Fingerprint").
*/
const navLink = document.querySelectorAll(".nav-link");

navLink.forEach(n => n.addEventListener("click", closeMenu));

function closeMenu() {
    hamburger.classList.remove("active");
    navMenu.classList.remove("active");
}




/* === Image Preview Logic for Face Page === */

// Find the elements on the face page
const faceUploadInput = document.getElementById("face_image_upload");
const facePreviewImage = document.getElementById("facePreview");
const placeholderIcon = document.querySelector(".placeholder-icon");

// We must check if these elements exist first.
// This prevents errors on pages that don't have them (like home.html).
if (faceUploadInput && facePreviewImage && placeholderIcon) {

    // Add an event listener to the file input
    faceUploadInput.addEventListener("change", function() {
        // Get the file that was just selected
        const file = this.files[0];

        if (file) {
            // Create a URL for the selected file
            const reader = new FileReader();

            reader.onload = function(e) {
                // Set the preview image's 'src' to the file's URL
                facePreviewImage.src = e.target.result;
                
                // Show the image and hide the icon
                facePreviewImage.style.display = "block";
                placeholderIcon.style.display = "none";
            }

            // Read the file as a Data URL
            reader.readAsDataURL(file);
        }
    });
}



/* === Image Preview Logic for Fingerprint Page === */

// Find the elements on the fingerprint page
const fingerprintUploadInput = document.getElementById("fingerprint_image_upload");
const fingerprintPreviewImage = document.getElementById("fingerprintPreview");
const fingerprintPlaceholder = document.querySelector(".fa-fingerprint"); // We target the icon specifically

// Check if these elements exist
if (fingerprintUploadInput && fingerprintPreviewImage && fingerprintPlaceholder) {

    // Add an event listener to the file input
    fingerprintUploadInput.addEventListener("change", function() {
        // Get the file that was just selected
        const file = this.files[0];

        if (file) {
            // Create a URL for the selected file
            const reader = new FileReader();

            reader.onload = function(e) {
                // Set the preview image's 'src' to the file's URL
                fingerprintPreviewImage.src = e.target.result;
                
                // Show the image and hide the icon
                fingerprintPreviewImage.style.display = "block";
                
                // We need to find the icon inside the preview box to hide it
                const icon = fingerprintPreviewImage.previousElementSibling;
                if (icon && icon.classList.contains("placeholder-icon")) {
                    icon.style.display = "none";
                }
            }

            // Read the file as a Data URL
            reader.readAsDataURL(file);
        }
    });
}