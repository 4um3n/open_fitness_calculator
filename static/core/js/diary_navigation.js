function navButtonsClassController() {
    let navItems = document.getElementsByClassName(".nav-item");
    Array.from(navItems).forEach(function (elem) {
        setRadioButtonsClickEventListener(elem, navItems)
    });
}

function setRadioButtonsClickEventListener(elem, inputs) {
    elem.addEventListener('click', function (a) {
        Array.from(inputs).forEach(function (z) {
            if (z.classList.contains("active")) {
                z.classList.remove("active");
            }
        });
        a.classList.add("active");
    })
}