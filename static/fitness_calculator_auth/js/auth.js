function googleLikePlaceholderHandler (placeholder, input_id, legend_id) {
    let input_field = document.getElementById(input_id)
    let legend = document.getElementById(legend_id)

    input_field.placeholder = placeholder

    if (window.getComputedStyle(legend).display === "none") {
        legend.removeAttribute('hidden')
    } else {
        legend.hidden = 'hidden'
    }
}
