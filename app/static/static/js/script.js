document.addEventListener("DOMContentLoaded", function () {
    // Add click event listener to all summary elements
    document.querySelectorAll('details').forEach(function (details) {
        details.addEventListener('click', function () {
            // Toggle the open/closed state of the parent details element
            this.parentNode.toggleAttribute('open');
        });
    });
});