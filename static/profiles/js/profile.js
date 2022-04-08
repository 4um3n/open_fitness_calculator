function getProfilePicture() {
    document.getElementById("id_profile_picture").click();
}


function clickStaffCardButton(profilePk) {
    let buttonId = "id_card_button_staff_" + profilePk.toString()
    document.getElementById(buttonId).click()
}


function profilePictureChanged() {
    let selectedFile = document.getElementById("id_profile_picture").files[0];
    let img = document.getElementById("profile_image")

    let reader = new FileReader();
    reader.onload = function () {
        img.src = this.result
    }
    reader.readAsDataURL(selectedFile);
}


function profileRadioButtonsClassController() {
    let disabledRadioInputs = document.querySelectorAll(".form-control-radio input[type=radio]");
    Array.from(disabledRadioInputs).forEach(function (elem) {
        if (elem.checked && elem.disabled) {
            elem.parentNode.classList.add("delete");
        } else if (elem.checked) {
            elem.parentNode.classList.add("radio-checked");
        } else if (elem.disabled) {
            elem.parentNode.classList.add("transparent");
        }
    });


    let genderInputs = document.querySelectorAll(".form-control-radio.gender input[type=radio]");
    Array.from(genderInputs).forEach(function (elem) {
        setRadioButtonsClickEventListener(elem, genderInputs)
    });

    let activeLevelInputs = document.querySelectorAll(".form-control-radio.active-level input[type=radio]");
    Array.from(activeLevelInputs).forEach(function (elem) {
        setRadioButtonsClickEventListener(elem, activeLevelInputs)
    });

    let goalInputs = document.querySelectorAll(".form-control-radio.goal input[type=radio]");
    Array.from(goalInputs).forEach(function (elem) {
        setRadioButtonsClickEventListener(elem, goalInputs)
    });

    let perWeekInputs = document.querySelectorAll(".form-control-radio.per-week input[type=radio]");
    Array.from(perWeekInputs).forEach(function (elem) {
        setRadioButtonsClickEventListener(elem, perWeekInputs)
    });
}


function setRadioButtonsClickEventListener(elem, inputs) {
    elem.addEventListener('click', function (a) {
        Array.from(inputs).forEach(function (z) {
            if (z.parentNode.classList.contains("radio-checked")) {
                z.parentNode.classList.remove("radio-checked");
            }
        });
        a.target.parentNode.classList.add("radio-checked");
    })
}
