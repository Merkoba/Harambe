let clicked = false

window.onload = () => {
  let image = DOM.el(`#image`)

  if (image) {
    DOM.ev(image, `click`, (e) => {
      if (!vars.is_user) {
        popmsg(`Login or register first.`)
        return
      }

      if (e.shiftKey || e.ctrlKey || e.altKey) {
        reset_file()
        return
      }

      let file = DOM.el(`#file`)
      file.click()
    })

    DOM.ev(image, `auxclick`, (e) => {
      if (e.button === 1) {
        e.preventDefault()
        reset_file()
      }
    })

    let file = DOM.el(`#file`)

    if (file) {
      DOM.ev(file, `change`, (e) => {
        clicked = false
        reflect_file()
      })

      DOM.ev(file, `click`, (e) => {
        if (e.shiftKey || e.ctrlKey || e.altKey) {
          e.preventDefault()
          reset_file()
        }
      })

      DOM.ev(file, `auxclick`, (e) => {
        if (e.button === 1) {
          e.preventDefault()
          reset_file()
        }
      })
    }
  }

  DOM.ev(document, `dragover`, (e) => {
    e.preventDefault()
  })

  DOM.ev(document, `drop`, (e) => {
    e.preventDefault()
    let files = e.dataTransfer.files

    if (files && (files.length > 0)) {
      let file = DOM.el(`#file`)
      let dataTransfer = new DataTransfer()
      dataTransfer.items.add(files[0])
      file.files = dataTransfer.files
      reflect_file()
    }
  })

  let video = DOM.el(`#video`)

  if (video) {
    DOM.ev(video, `loadeddata`, () => {
      video.muted = true
      video.play()
    })
  }

  let links_btn = DOM.el(`#links_btn`)

  if (links_btn) {
    vars.msg_links = Msg.factory()
    let t = DOM.el(`#template_links`)
    vars.msg_links.set(t.innerHTML)
    let c = DOM.el(`#links_container`)

    for (let link of vars.links) {
      let item = DOM.create(`div`, `aero_button`)
      item.textContent = link.name
      item.title = link.url

      DOM.ev(item, `click`, (e) => {
        vars.msg_links.close()
        window.open(link.url, item.target)
      })

      c.appendChild(item)
    }

    DOM.ev(links_btn, `click`, (e) => {
      vars.msg_links.show()
    })
  }

  let admin_btn = DOM.el(`#admin_btn`)

  if (admin_btn) {
    setup_admin_opts(`admin`)

    DOM.ev(admin_btn, `click`, (e) => {
      vars.msg_admin_opts.show()
    })
  }

  let explore_btn = DOM.el(`#explore_btn`)

  if (explore_btn) {
    setup_explore_opts()

    DOM.ev(explore_btn, `click`, (e) => {
      vars.msg_explore_opts.show()
    })

    DOM.ev(explore_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        window.location = `/fresh`
      }
    })
  }

  let login_btn = DOM.el(`#login_btn`)

  if (login_btn) {
    DOM.ev(login_btn, `click`, (e) => {
      window.location = `/login`
    })
  }

  let register_btn = DOM.el(`#register_btn`)

  if (register_btn) {
    DOM.ev(register_btn, `click`, (e) => {
      window.location = `/register`
    })
  }

  let you_btn = DOM.el(`#you_btn`)

  if (you_btn) {
    setup_you_opts(vars.username)

    DOM.ev(you_btn, `click`, (e) => {
      vars.msg_you_opts.show()
    })

    DOM.ev(you_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        window.location = `/list/posts`
      }
    })
  }

  let submit_btn = DOM.el(`#submit_btn`)

  if (submit_btn) {
    DOM.ev(submit_btn, `click`, (e) => {
      if (validate()) {
        let form = DOM.el(`#form`)
        form.submit()
      }
    })
  }
}

function validate() {
  if (clicked) {
    return false
  }

  let file = DOM.el(`#file`)
  let file_length = file.files.length

  if (file_length === 0) {
    file.click()
    return false
  }

  if (file_length > 1) {
    return false
  }

  if (file.files[0].size > vars.max_size) {
    return false
  }

  let title = DOM.el(`#title`)

  if (title) {
    if (title.value.length > vars.max_title_length) {
      return false
    }
  }

  clicked = true
  return true
}

function reflect_file() {
  let title = DOM.el(`#title`)

  if (title) {
    title.focus()
  }

  let file = DOM.el(`#file`)
  let the_file = file.files[0]

  if (the_file.size > vars.max_size) {
    reset_file()
    popmsg(`That file is too big.`)
    return
  }

  reset_image()
  video.pause()
  DOM.hide(video)

  if (is_image(the_file)) {
    let reader = new FileReader()

    reader.onload = (e) => {
      image.src = e.target.result
    }

    DOM.hide(video)
    DOM.show(image)
    reader.readAsDataURL(the_file)
  }
  else if (is_audio(the_file) || is_video(the_file)) {
    video.src = URL.createObjectURL(the_file)
    DOM.hide(image)
    DOM.show(video)
    video.load()
  }
}

function reset_file() {
  let file = DOM.el(`#file`)
  file.value = null
  reset_image()
  reset_video()
  DOM.show(`#image`)
}

function reset_image() {
  let image = DOM.el(`#image`)
  image.src = `/static/img/banners/${vars.banner}`
}

function reset_video() {
  let video = DOM.el(`#video`)
  video.pause()
  DOM.hide(video)
}

function show_links() {
  let links_dialog = DOM.el(`#links_dialog`)
  links_dialog.showModal()
}

function show_explore() {

}

function show_you() {
  window.location = `/you`
}

function edit_name() {
  let prompt_args = {
    placeholder: `Enter your new public name`,
    value: vars.user_name,
    max: vars.max_name_length,
    callback: (value) => {
      if (!value) {
        return
      }

      do_edit(`name`, value, `Name`, () => {
        vars.user_name = value
        DOM.el(`#user_name`).textContent = value
      })
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

async function do_edit(what, value, title, callback) {
  let response = await fetch(`/user_edit`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({what, value}),
  })

  if (response.ok) {
    popmsg(`${title} updated.`, () => {
      if (callback) {
        callback()
      }
    })
  }
  else {
    print_error(response.status)
  }
}