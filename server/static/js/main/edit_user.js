DOM.ev(document, `DOMContentLoaded`, () => {
  App.init()
})

App.init = () => {
  let uname = DOM.el(`#username`)

  if (uname) {
    uname.focus()
  }

  let del = DOM.el(`#delete`)

  if (del) {
    DOM.ev(del, `click`, () => {
      let confirm_args = {
        message: `Delete ${App.username} ?`,
        callback_yes: () => {
          App.delete_user()
        },
      }

      App.confirmbox(confirm_args)
    })
  }

  DOM.ev(document, `click`, (e) => {
    if (e.target.closest(`.checkbox`)) {
      if (e.target.tagName === `INPUT`) {
        return
      }

      let c = e.target.closest(`.checkbox`)
      let cb = DOM.el(`input[type="checkbox"]`, c)

      if (cb) {
        cb.checked = !cb.checked
      }
    }
  })
}

App.delete_user = async () => {
  let username = App.username

  if (!username) {
    return
  }

  try {
    let response = await fetch(`/delete_user`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify({username}),
    })

    if (response.ok) {
      App.popmsg(`Deleted`)
    }
    else {
      App.print_error(response.status)
    }
  }
  catch (error) {
    App.print_error(error)
  }
}