window.onload = () => {
  DOM.ev(`#logout`, `click`, () => {
    if (confirm(`Are you sure you want to logout?`)) {
      window.location = `/logout`
    }
  })

  let edit = DOM.el(`#edit`)
  let edit_dialog = DOM.el(`#edit_dialog`)

  if (edit && edit_dialog) {
    edit_dialog.addEventListener(`close`, () => {
      let value = edit_dialog.returnValue

      if (value === `name`) {
        edit_name()
      }
      else if (value === `password`) {
        edit_password()
      }
    })

    DOM.ev(edit, `click`, () => {
      edit_dialog.showModal()
    })

    DOM.ev(edit_dialog, `click`, (e) => {
      if (e.target === edit_dialog) {
        edit_dialog.close()
      }
    })
  }
}

async function do_edit(what, value, title) {
  let response = await fetch(`/user_edit`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({what, value}),
  })

  if (response.ok) {
    alert(`${title} updated.`)
    window.location = `/you`
  }
  else {
    print_error(response.status)
  }
}

function edit_name() {
  let value = prompt(`Enter your new public name`)

  if (!value) {
    return
  }

  do_edit(`name`, value, `Name`)
}

function edit_password() {
  let value = prompt(`Enter your new password`)

  if (!value) {
    return
  }

  do_edit(`password`, value, `Password`)
}