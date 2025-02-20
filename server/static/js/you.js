window.onload = () => {
  DOM.ev(`#logout`, `click`, () => {
    if (confirm(`Are you sure you want to logout?`)) {
      window.location = `/logout`
    }
  })

  let edit = DOM.el(`#edit`)

  if (edit) {
    vars.msg_edit = Msg.factory()
    let t = DOM.el(`#template_edit`)
    vars.msg_edit.set(t.innerHTML)

    DOM.ev(`#edit_name`, `click`, () => {
      edit_name()
    })

    DOM.ev(`#edit_password`, `click`, () => {
      edit_password()
    })

    DOM.ev(edit, `click`, () => {
      vars.msg_edit.show()
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
  let value = prompt(`Enter your new public name`, vars.name)

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