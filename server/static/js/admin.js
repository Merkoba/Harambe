let selected_files = []

window.onload = () => {
    document.addEventListener(`click`, async (e) => {
        if (e.target.classList.contains(`delete`)) {
            let name = e.target.dataset.name

            if (confirm(`Delete: ${name}`)) {
                delete_file(name, e.target)
            }
        }
    })

    let delete_selected = document.querySelector(`#delete_selected`)

    if (delete_selected) {
        delete_selected.addEventListener(`click`, () => {
            let files = []
            let checkboxes = document.querySelectorAll(`.select_checkbox`)

            for (let checkbox of checkboxes) {
                if (checkbox.checked) {
                    files.push(checkbox.dataset.name)
                }
            }

            if (files.length === 0) {
                return
            }

            selected_files = files

            if (confirm(`Delete Selected (${files.length})`)) {
                delete_selected_files()
            }
        })
    }

    let delete_all = document.querySelector(`#delete_all`)

    if (delete_all) {
        delete_all.addEventListener(`click`, () => {
            if (confirm(`Delete All`)) {
                delete_all_files()
            }
        })
    }
}

async function delete_file(name, el) {
    let files = [name]

    try {
        let response = await fetch(`/delete_files`, {
            method: `POST`,
            headers: {
                "Content-Type": `application/json`
            },
            body: JSON.stringify({files, password})
        })

        if (response.ok) {
            remove_files(files)
        } else {
            console.error(`Error:`, response.status)
        }
    }
    catch (error) {
        console.error(`Error:`, error)
    }
}

async function delete_selected_files() {
    let files = selected_files

    try {
        let response = await fetch(`/delete_files`, {
            method: `POST`,
            headers: {
                "Content-Type": `application/json`
            },
            body: JSON.stringify({files, password})
        })

        if (response.ok) {
            remove_files(files)
        } else {
            console.error(`Error:`, response.status)
        }
    }
    catch (error) {
        console.error(`Error:`, error)
    }
}

function remove_files(files) {
    for (let file of files) {
        let el = document.querySelector(`.link[data-name="${file}"]`)

        if (el) {
            el.remove()
        }
    }
}

async function delete_all_files() {
    try {
        let response = await fetch(`/delete_all_files`, {
            method: `POST`,
            headers: {
                "Content-Type": `application/json`
            },
            body: JSON.stringify({password})
        })

        if (response.ok) {
            document.querySelector(`#links`).innerHTML = ``
        }
        else {
            console.error(`Error:`, response.status)
        }
    }
    catch (error) {
        console.error(`Error:`, error)
    }
}