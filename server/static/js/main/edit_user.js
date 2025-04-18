App.init = () => {
  let uname = DOM.el(`#username`)

  if (uname) {
    uname.focus()
  }

  let del = DOM.el(`#delete`)

  if (del) {
    DOM.ev(del, `click`, () => {
      let confirm_args = {
        message: `Delete ${App.user.username}`,
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

  let menu = DOM.el(`#menu`)

  if (menu) {
    DOM.ev(menu, `click`, () => {
      App.setup_menu_opts(true)
    })
  }
}

App.delete_user = async () => {
  let ids = [App.user.id]

  let response = await fetch(`/delete_users`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({ids}),
  })

  if (response.ok) {
    App.popmsg(`Deleted`)
  }
  else {
    App.feedback(response)
  }
}