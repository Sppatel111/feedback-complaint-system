function parseCustomDate(dateStr) {
    // Expects format: "10 Apr 2025, 04:43 PM"
    const months = {
        Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5,
        Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11
    };

    const match = dateStr.match(/(\d{1,2}) (\w{3}) (\d{4}), (\d{1,2}):(\d{2}) (AM|PM)/);
    if (!match) {
        console.warn("Date parse failed for:", dateStr);
        return null;
    }

    let [_, day, month, year, hour, minute, meridian] = match;
    hour = parseInt(hour);
    minute = parseInt(minute);
    if (meridian === "PM" && hour < 12) hour += 12;
    if (meridian === "AM" && hour === 12) hour = 0;

    return new Date(parseInt(year), months[month], parseInt(day), hour, minute);
}

function filterRows() {
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");

    const startDate = startDateInput.value ? new Date(startDateInput.value) : null;
    const endDate = endDateInput.value ? new Date(endDateInput.value) : null;

    // Modify these selectors based on your specific table and the date column's data attribute.
    const rows = document.querySelectorAll("table tbody tr");

    rows.forEach(row => {
        // Add data-date attributes for each date column in the row
        const dateCells = row.querySelectorAll("td[data-date]");
        let showRow = true;

        dateCells.forEach(cell => {
            const rawDateText = cell.textContent.replace(/\s+/g, ' ').trim();
            const cellDate = parseCustomDate(rawDateText);

            if (!cellDate) return;

            if (
                (startDate && cellDate < startDate) ||
                (endDate && cellDate > endDate)
            ) {
                showRow = false;
            }
        });

        row.style.display = showRow ? "" : "none";
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const rows = document.querySelectorAll('table tbody tr');

    function filterByDate() {
        const start = startDate.value ? new Date(startDate.value) : null;
        const end = endDate.value ? new Date(endDate.value) : null;

        rows.forEach(row => {
            const dateCells = row.querySelectorAll('td[data-date]');
            let showRow = true;

            dateCells.forEach(cell => {
                const rowDateStr = cell.getAttribute('data-date');
                const rowDate = new Date(rowDateStr);

                if (start && rowDate < start) showRow = false;
                if (end && rowDate > end) showRow = false;
            });

            row.style.display = showRow ? '' : 'none';
        });
    }

    startDate.addEventListener('change', filterByDate);
    endDate.addEventListener('change', filterByDate);
});
