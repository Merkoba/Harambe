window.onload = () => {
    document.addEventListener(`click`, async (e) => {
        if (e.target.classList.contains(`delete`)) {
            let name = e.target.dataset.name

            if (confirm(`Delete: ${name}`)) {
                delete_file(name, e.target)
            }
        }
    })

    let delete_all = document.getElementById(`delete_all`)

    delete_all.addEventListener(`click`, () => {
        if (confirm(`Delete All`)) {
            delete_all_files()
        }
    })
}

async function delete_file(name, el) {
    try {
        let response = await fetch(`/delete`, {
            method: `POST`,
            headers: {
                "Content-Type": `application/json`
            },
            body: JSON.stringify({name, password})
        })

        if (response.ok) {
            el.closest(`.link`).remove()
        } else {
            console.error(`Error:`, response.status)
        }
    }
    catch (error) {
        console.error(`Error:`, error)
    }
}

async function delete_all_files() {
    try {
        let response = await fetch(`/delete_all`, {
            method: `POST`,
            headers: {
                "Content-Type": `application/json`
            },
            body: JSON.stringify({password})
        })

        if (response.ok) {
            document.getElementById(`links`).innerHTML = ``
        }
        else {
            console.error(`Error:`, response.status)
        }
    }
    catch (error) {
        console.error(`Error:`, error)
    }
}