const main_form = document.querySelector("#request-website-indexing-form")
const main_form_submit_btn = document.querySelector("#request-website-indexing-form button.btn")
const main_form_input = document.querySelector("#request-website-indexing-form input")

function handle_indexing_request() {
    console.log(main_form_input.value)
}

main_form.addEventListener("submit", (e)=> {
    e.preventDefault()
    handle_indexing_request()
})

main_form_submit_btn.addEventListener("click", (e)=> {
    e.preventDefault()
    handle_indexing_request()
})

main_form_input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault() // Prevent adding a new line in the textarea
        handle_indexing_request()
    }
});