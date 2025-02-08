let selected_files = []

window.onload = () => {
    document.addEventListener(`click`, async (e) => {
        if (e.target.classList.contains(`delete`)) {
            selected_files = [e.target.closest(`.link`)]
            delete_files()
        }

        if (e.target.classList.contains(`delete_above`)) {
            let el = e.target.closest(`.link`)
            delete_above(el)
        }

        if (e.target.classList.contains(`delete_below`)) {
            let el = e.target.closest(`.link`)
            delete_below(el)
        }
    })

    let delete_selected = document.querySelector(`#delete_selected`)

    if (delete_selected) {
        delete_selected.addEventListener(`click`, () => {
            let files = []
            let checkboxes = document.querySelectorAll(`.select_checkbox`)

            for (let checkbox of checkboxes) {
                if (checkbox.checked) {
                    files.push(checkbox.closest(`.link`))
                }
            }

            if (files.length === 0) {
                return
            }

            selected_files = files
            delete_files()
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

function delete_above(el) {
    let links = document.querySelectorAll(`.link`)
    let files = []

    for (let link of links) {
        if (link === el) {
            break
        }

        files.push(link)
    }

    selected_files = files
    delete_files()
}

function delete_below(el) {
    let links = document.querySelectorAll(`.link`)
    let files = []
    let start = false

    for (let link of links) {
        if (link === el) {
            start = true
            continue
        }

        if (start) {
            files.push(link)
        }
    }

    selected_files = files
    delete_files()
}

function delete_files() {
    let size = 0

    for (let file of selected_files) {
        size += parseFloat(file.dataset.size)
    }

    size = Math.round(size * 100) / 100

    if (confirm(`Delete (${selected_files.length} files) (${size} mb)`)) {
        let files = []

        for (let file of selected_files) {
            files.push(file.dataset.name)
        }

        delete_selected_files(files)
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

async function delete_selected_files(files) {
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