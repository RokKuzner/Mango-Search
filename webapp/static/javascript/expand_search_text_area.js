window.addEventListener("load", (e) => {
    document.querySelector(".search-textarea-wrapper textarea").addEventListener("input", handle_textarea_input)
})

function handle_textarea_input() {
    let element = this
    let computed_style = window.getComputedStyle(element)

    element.style.height = computed_style.minHeight //temporarily set to min height for scrollHeight to work properly when removing text

    let required_height = element.scrollHeight
    
    element.style.height = required_height + "px"
}