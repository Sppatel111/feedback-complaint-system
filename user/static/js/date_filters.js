document.addEventListener('DOMContentLoaded', function () {
  flatpickr("#dateRange", {
    mode: "range",
    dateFormat: "D, M j",  // e.g., "Sun, May 4"
    allowInput: false,
    onOpen: function(_, __, fp) {
      fp._positionElement = document.querySelector(".custom-daterange-wrapper");
    },
    onChange: function(selectedDates) {
      if (selectedDates.length === 2) {
        const [start, end] = selectedDates;
        const rows = document.querySelectorAll("table tbody tr");

        rows.forEach(row => {
          const dateCells = row.querySelectorAll("td[data-date]");
          let showRow = false;

          dateCells.forEach(cell => {
            const cellDate = new Date(cell.getAttribute("data-date"));
            if (cellDate >= start && cellDate <= end) {
              showRow = true;
            }
          });

          row.style.display = showRow ? "" : "none";
        });
      }
    }
  });
});
