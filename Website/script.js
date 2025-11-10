const viewportWidthDisplay = document.querySelector('.tester');
const logoImage = document.querySelector('.logo');

const originalLogoSrc = 'img/XU_Logotype_Color.png';
const alternateLogoSrc = 'img/XU_Logo_2.png'; // Assuming the new logo is in the img folder

function displayViewportWidth() {
    if (!viewportWidthDisplay) return;
    const width = window.innerWidth;
    viewportWidthDisplay.textContent = `Current Viewport Width: ${width}px`;
}

function swapLogoOnResize() {
    if (!logoImage) return;

    if (window.innerWidth < 500) {
        logoImage.src = alternateLogoSrc;
        logoImage.classList.add('logo-alternate'); // Add class for alternate logo
    } else {
        logoImage.src = originalLogoSrc;
        logoImage.classList.remove('logo-alternate'); // Remove class for original logo
    }
}

function onResize() {
    displayViewportWidth();
    swapLogoOnResize();
}

onResize();
window.addEventListener('resize', onResize);
