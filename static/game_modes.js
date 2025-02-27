document.addEventListener("DOMContentLoaded", function () {
    const modeSelector = document.getElementById("spielmodus");
    const modeDisplay = document.getElementById("spielmodus-anzeige");

    if (localStorage.getItem("selectedMode")) {
        modeSelector.value = localStorage.getItem("selectedMode");
        modeDisplay.textContent = localStorage.getItem("selectedMode");
    }
    
    modeSelector.addEventListener("change", function () {
        const selectedMode = modeSelector.value;
        localStorage.setItem("selectedMode", selectedMode);
        modeDisplay.textContent = selectedMode;

        fetch("/update_mode", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ mode: selectedMode })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Mode updated successfully:", data);
        })
        .catch(error => {
            console.error("Error updating mode:", error);
        });
    });

    fetch("/get_mode")
        .then(response => response.json())
        .then(data => {
            if (data.mode) {
                modeSelector.value = data.mode;
                modeDisplay.textContent = data.mode;
            }
        })
        .catch(error => {
            console.error("Error fetching mode:", error);
        });
});

