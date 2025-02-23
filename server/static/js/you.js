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
      vars.msg_edit.close()
      edit_name()
    })

    DOM.ev(`#edit_password`, `click`, () => {
      vars.msg_edit.close()
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
    popmsg(`${title} updated.`, () => {
      window.location = `/you`
    })
  }
  else {
    print_error(response.status)
  }
}

function edit_name() {
  let prompt_args = {
    placeholder: `Enter your new public name`,
    value: vars.name,
    max: vars.max_name_length,
    callback: (value) => {
      if (!value) {
        return
      }

      do_edit(`name`, value, `Name`)
    },
  }

  prompt_text(prompt_args)
}

function edit_password() {
  let prompt_args = {
    placeholder: `Enter your new password`,
    max: vars.max_password_length,
    callback: (value) => {
      if (!value) {
        return
      }

      let prompt_args_2 = {
        placeholder: `Enter the password again`,
        max: vars.max_password_length,
        callback: (value_2) => {
          if (value !== value_2) {
            popmsg(`Passwords do not match.`)
            return
          }

          do_edit(`password`, value, `Password`)
        },
      }

      prompt_text(prompt_args_2)
    },
  }

  prompt_text(prompt_args)
}