let selected_files = []
let date_mode = `ago`

window.onload = () => {
    document.addEventListener(`click`, async (e) => {
        if (e.target.classList.contains(`delete`)) {
            selected_files = [e.target.closest(`.link`)]
            delete_files()
        }

        if (e.target.classList.contains(`delete_above`)) {
            let el = e.target.closest(`.link`)
            select_above(el)
        }

        if (e.target.classList.contains(`delete_below`)) {
            let el = e.target.closest(`.link`)
            select_below(el)
        }
    })

    let s_all = document.querySelector(`#select_all`)

    if (s_all) {
        s_all.addEventListener(`click`, () => {
            select_all()
        })
    }

    let u_all = document.querySelector(`#unselect_all`)

    if (u_all) {
        u_all.addEventListener(`click`, () => {
            unselect_all()
        })
    }

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

    let page_select = document.querySelector(`#page_select`)

    if (page_select) {
        fill_page_select(page_select)

        page_select.addEventListener(`change`, () => {
            on_page_select_change()
        })
    }

    let filter = document.querySelector(`#filter`)

    if (filter) {
        filter.addEventListener(`input`, () => {
            let links = document.querySelectorAll(`.link`)
            let value = filter.value.toLowerCase()

            for (let link of links) {
                let name = link.dataset.name.toLowerCase()
                let ago = link.dataset.ago.toLowerCase()
                let date = link.dataset.date.toLowerCase()
                let size = link.dataset.size.toLowerCase()
                let opts = [name, size]

                if (date_mode === `ago`) {
                    opts.push(ago)
                }
                else if (date_mode === `date`) {
                    opts.push(date)
                }

                if (opts.some(x => x.includes(value))) {
                    link.style.display = `flex`
                }
                else {
                    link.style.display = `none`
                }
            }
        })
    }

    let age = document.querySelector(`#age`)

    if (age) {
        age.addEventListener(`click`, () => {
            if (date_mode === `ago`) {
                date_mode = `date`
            }
            else {
                date_mode = `ago`
            }

            for (let link of document.querySelectorAll(`.link`)) {
                if (date_mode === `ago`) {
                    link.querySelector(`.date`).innerText = link.dataset.ago
                }
                else {
                    link.querySelector(`.date`).innerText = link.dataset.date
                }
            }
        })
    }
}

function select_above(el) {
    unselect_all()
    let links = document.querySelectorAll(`.link`)

    for (let link of links) {
        let check = link.querySelector(`.select_checkbox`)
        check.checked = true

        if (link === el) {
            break
        }
    }
}

function select_below(el) {
    unselect_all()
    let links = document.querySelectorAll(`.link`)
    let start = false

    for (let link of links) {
        if (link === el) {
            start = true
        }

        if (start) {
            let check = link.querySelector(`.select_checkbox`)
            check.checked = true
        }
    }
}

function fill_page_select(page_select) {
    function add_option(n, disabled = false, selected = false) {
        let option = document.createElement(`option`)
        option.value = n
        option.innerText = n
        option.disabled = disabled
        option.selected = selected
        page_select.appendChild(option)
    }

    add_option(`Default`, false, def_page_size)
    add_option(`------`, true)

    let nums = [10, 20, 50, 100, 200, 500, 1000]

    for (let n of nums) {
        let selected = false

        if (!def_page_size) {
            if (page_size === n.toString()) {
                selected = true
            }
        }

        add_option(n, false, selected)
    }

    add_option(`------`, true)
    add_option(`All`, false, page_size === `all`)
}

function on_page_select_change() {
    let value = page_select.value
    let psize

    if (value === `-`) {
        return
    }

    if (value === `All`) {
        psize = `all`
    }
    else if (value === `Default`) {
        psize = `default`
    }
    else {
        psize = parseInt(value)
    }

    let url = new URL(window.location.href)
    url.searchParams.set(`page_size`, psize)
    window.location.href = url.href
}

function delete_files() {
    if (selected_files.length === 0) {
        return
    }

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
            body: JSON.stringify({files})
        })

        if (response.ok) {
            remove_files(files)
        }
        else {
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
            body: JSON.stringify({files})
        })

        if (response.ok) {
            remove_files(files)
        }
        else {
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
            body: JSON.stringify()
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

function select_all() {
    let checkboxes = document.querySelectorAll(`.select_checkbox`)

    for (let checkbox of checkboxes) {
        checkbox.checked = true
    }
}

function unselect_all() {
    let checkboxes = document.querySelectorAll(`.select_checkbox`)

    for (let checkbox of checkboxes) {
        checkbox.checked = false
    }
}