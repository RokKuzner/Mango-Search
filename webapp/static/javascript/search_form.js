const search_form = document.querySelector("#search-form")
const search_texarea = document.querySelector("#search-form .search-textarea-wrapper textarea")

function handle_search() {
    let query = encodeURIComponent(search_texarea.value)
    let new_url = window.location.origin + "/search?q=" + query
    console.log(new_url)
    window.location.replace(new_url)
}

search_form.addEventListener("submit", (e)=> {
    e.preventDefault()
    handle_search()
})

document.querySelector("#search-form .search-icon img").addEventListener("click", ()=> {
    handle_search()
})

search_texarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault() // Prevent adding a new line in the textarea
        handle_search()
    }
});