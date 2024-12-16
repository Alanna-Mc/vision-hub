// Code adapted for this application from: https://www.geeksforgeeks.org/how-to-design-digital-clock-using-javascript/ and https://www.freecodecamp.org/news/javascript-get-current-date-todays-date-in-js

document.addEventListener("DOMContentLoaded", function () {
    // Update every second
    setInterval(showDateAndTime, 6000);

    function showDateAndTime() {
        // Getting current time and date
        const time = new Date();
        let hour = time.getHours();
        let min = time.getMinutes();
        let day = time.getDate();
        let month = time.getMonth() + 1;
        let year = time.getFullYear();
        let am_pm = "AM";

        // Setting time for 12 Hrs format
        if (hour >= 12) {
            if (hour > 12) hour -= 12;
            am_pm = "PM";
        } else if (hour === 0) {
            hour = 12;
            am_pm = "AM";
        }

        // Add leading zero to single-digit values
        hour = hour < 10 ? "0" + hour : hour;
        min = min < 10 ? "0" + min : min;
        day = day < 10 ? "0" + day : day;
        month = month < 10 ? "0" + month : month;

        // Combine date and time
        const currentDateAndTime = `${day}/${month}/${year} ${hour}:${min} ${am_pm}`;

        // Update the element in the HTML
        const clockElement = document.getElementById("clock");
        if (clockElement) {
            clockElement.innerHTML = currentDateAndTime;
        }
    }

    // Initial call to display the time 
    showDateAndTime();
});
