document.addEventListener("DOMContentLoaded", function () {
    const modeSelector = document.getElementById("spielmodus");
    
    if (localStorage.getItem("selectedMode")) {
        modeSelector.value = localStorage.getItem("selectedMode");
    }
    
    modeSelector.addEventListener("change", function () {
        const selectedMode = modeSelector.value;
        localStorage.setItem("selectedMode", selectedMode);
        
        fetch("/update_mode", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ mode: selectedMode })
        });
    });

    fetch("/get_mode")
        .then(response => response.json())
        .then(data => {
            if (data.mode) {
                modeSelector.value = data.mode;
            }
        });
});
