document.addEventListener('DOMContentLoaded', function () {
  const startInput = document.getElementById("startDateInput");
  const endInput = document.getElementById("endDateInput");

  const defaultStart = startInput?.value ? new Date(startInput.value) : null;
  const defaultEnd = endInput?.value ? new Date(endInput.value) : null;

  const datePicker = flatpickr("#dateRange", {
    mode: "range",
    dateFormat: "Y-m-d",
    allowInput: false,
    defaultDate: [defaultStart, defaultEnd].filter(Boolean),
    onOpen: function (_, __, fp) {
      fp._positionElement = document.querySelector(".custom-daterange-wrapper");
    },
    onChange: function (selectedDates) {
      if (selectedDates.length === 2) {
        const [start, end] = selectedDates;

        if (startInput && endInput) {
          startInput.value = flatpickr.formatDate(start, "Y-m-d");
          endInput.value = flatpickr.formatDate(end, "Y-m-d");
        }

        const rows = document.querySelectorAll("table tbody tr");
        rows.forEach(row => {
          const rowDateStr = row.getAttribute("data-date");
          if (!rowDateStr) return;

          const rowDate = new Date(rowDateStr);
          const showRow = rowDate >= start && rowDate <= end;

          row.style.display = showRow ? "" : "none";
        });

        const form = document.getElementById("dateFilterForm");
        if (form) {
          form.submit();
        }
      } else {
        document.querySelectorAll("table tbody tr").forEach(row => {
          row.style.display = "";
        });

        if (startInput && endInput) {
          startInput.value = "";
          endInput.value = "";
        }
      }
    }
  });

  // Clear Date Filter Button
  document.getElementById("clearDateFilter")?.addEventListener("click", function () {
    datePicker.clear(); // Clear date picker selection

    if (startInput) startInput.value = "";
    if (endInput) endInput.value = "";

    const form = document.getElementById("dateFilterForm");
    if (form) {
      form.submit(); // Resubmit to reset view
    }
  });
});
