App.user_mod_input = (what, o_value, vtype, callback) => {
  let repeat = false

  if (vtype === `password`) {
    repeat = true
  }

  function send(value) {
    if (vtype === `password`) {
      vtype = `string`
    }

    if (vtype === `number`) {
      value = parseInt(value)

      if (isNaN(value)) {
        value = 0
      }
    }

    if (o_value && (value === o_value)) {
      return
    }

    if (callback) {
      callback(what, value, vtype)
    }
    else {
      App.mod_user(what, value, vtype)
    }
  }

  let name = what.split(`_`).join(` `)

  let prompt_args = {
    value: o_value,
    placeholder: `Type the new ${name}`,
    max: App.max_reaction_length,
    password: vtype === `password`,
    callback: (value_1) => {
      if (!repeat) {
        send(value_1)
        return
      }

      let prompt_args_2 = {
        placeholder: `Enter the value again`,
        max: App.max_reaction_length,
        password: vtype === `password`,
        callback: (value_2) => {
          if (value_1 !== value_2) {
            App.popmsg(`Values don't match`)
            return
          }

          send(value_2)
        },
      }

      App.prompt_text(prompt_args_2)
    },
  }

  App.prompt_text(prompt_args)
}

App.edit_name = () => {
  App.user_mod_input(`name`, App.user_name, `string`, (what, value, vtype) => {
    App.do_user_edit(what, value, vtype, `Name`, () => {
      App.user_name = value
      DOM.el(`#user_name`).textContent = value
    })
  })
}

App.edit_password = () => {
  App.user_mod_input(`password`, ``, `password`, (what, value, vtype) => {
    App.do_user_edit(what, value, vtype, `Password`)
  })
}

App.do_user_edit = async (what, value, vtype, title, callback) => {
  let ids = [App.user_id]

  let response = await fetch(`/mod_user`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({ids, what, value, vtype}),
  })

  if (response.ok) {
    App.popmsg(`${title} updated`, () => {
      if (callback) {
        callback()
      }
    })
  }
  else {
    App.print_error(response.status)
  }
}