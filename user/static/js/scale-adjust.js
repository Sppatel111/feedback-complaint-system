(function adjustPageScale() {
  if (window.innerWidth > 1600) {
    document.documentElement.style.zoom = "1.1";

    // Apply color styles dynamically
    const style = document.createElement('style');
    style.innerHTML = `
      body {
        color: #626e78;
      }
      .table {
        color: #4d575e;
      }
      .text-muted {
        color: #737d85 !important;
      }
      .text-dark {
        color: #060606 !important;
      }
      .text-secondary {
        color: #646d75;
      }
    `;
    document.head.appendChild(style);
  } else {
    document.documentElement.style.zoom = "1";
  }
})();
