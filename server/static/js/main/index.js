let clicked = false

window.onload = () => {
  let image = DOM.el(`#image`)
  let file = DOM.el(`#file`)

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

      if (file) {
        file.click()
      }
    })

    DOM.ev(image, `auxclick`, (e) => {
      if (e.button === 1) {
        e.preventDefault()
        reset_file()
      }
    })
  }

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

  let submit_btn = DOM.el(`#submit_btn`)

  if (submit_btn) {
    DOM.ev(submit_btn, `click`, (e) => {
      if (validate()) {
        let form = DOM.el(`#form`)
        form.submit()
      }
    })
  }

  let picker = DOM.el(`#picker`)

  if (picker && file) {
    DOM.ev(picker, `click`, (e) => {
      file.click()
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
  user_mod_input(`name`, `string`, (what, value, vtype) => {
    do_edit(what, value, vtype, `Name`, () => {
      vars.user_name = value
      DOM.el(`#user_name`).textContent = value
    })
  })
}

function edit_password() {
  user_mod_input(`password`, `password`, (what, value, vtype) => {
    do_edit(what, value, vtype, `Password`)
  })
}

async function do_edit(what, value, vtype, title, callback) {
  let ids = [vars.user_id]

  let response = await fetch(`/mod_user`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({ids, what, value, vtype}),
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